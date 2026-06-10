/* global window, navigator, fetch */
"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

type TaskItem = {
  title: string;
  date?: string;
  source: "manual" | "sheet" | "routine" | "moved";
};

const NAME_KEY = "planner3000:name";
const ROUTINE_KEY = "planner3000:routines";
const SHEET_KEY = "planner3000:sheetUrl";

const ignoredRows = [
  "важные незапланированные проекты",
  "текущие задачи месяца",
  "задачи от соседних отделов",
  "задачи от СОСЕДНИХ отделов",
  "название задачи",
  "ссылка на задачу",
];

const quotes = [
  "План нужен не для контроля, а для спокойствия.",
  "Хорошая неделя начинается с понятного списка.",
  "Сначала смысл. Потом структура.",
  "Меньше хаоса — больше энергии на работу.",
  "Не держи задачи в голове. Дай им место.",
  "Сильная команда видит общую картину.",
  "Планирование — это забота о будущем себе.",
  "Рутина не враг. Враг — забытая рутина.",
  "Чёткий список экономит десятки сообщений.",
  "Лучший план — тот, который можно выполнить.",
  "Задачи любят простые формулировки.",
  "Сначала фиксируем факты. Потом строим план.",
  "Не усложняй то, что можно упорядочить.",
  "Неделя становится легче, когда её видно.",
  "Порядок в задачах — это порядок в решениях.",
  "Сделанное тоже нужно показывать.",
  "План — это не обещание. Это направление.",
  "Когда всё записано, команда дышит свободнее.",
  "Маленькая ясность каждый день даёт большой результат.",
  "Система должна помогать, а не спорить.",
  "Не угадывай. Проверяй. Форматируй.",
  "Важное не должно теряться в чате.",
  "Хороший отчёт говорит коротко и по делу.",
  "Планируй проще. Делай увереннее.",
  "Форма освобождает место для смысла.",
];

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function addDays(date: Date, days: number) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function toShortDate(value: string) {
  if (!value) return "";
  const [, month, day] = value.split("-");
  return `${day}.${month}`;
}

function normalizeTask(line: string) {
  return line
    .replace(/^[-*•]\s*/, "")
    .replace(/^\d+[).]\s*/, "")
    .replace(/\s+/g, " ")
    .trim();
}

function isIgnoredRow(value: string) {
  const clean = normalizeTask(value).toLowerCase();
  if (!clean) return true;
  return ignoredRows.some((row) => clean === row.toLowerCase());
}

function normalizeDate(value: string) {
  const clean = value.trim();
  if (!clean) return "";

  const iso = clean.match(/^(\d{4})-(\d{2})-(\d{2})/);
  if (iso) return `${iso[1]}-${iso[2]}-${iso[3]}`;

  const ru = clean.match(/^(\d{1,2})[./](\d{1,2})[./](\d{2,4})$/);
  if (ru) {
    const day = ru[1].padStart(2, "0");
    const month = ru[2].padStart(2, "0");
    const year = ru[3].length === 2 ? `20${ru[3]}` : ru[3];
    return `${year}-${month}-${day}`;
  }

  return "";
}

function isDateInRange(date: string | undefined, start: string, end: string) {
  if (!date) return false;
  return date >= start && date <= end;
}

function dedupeTasks(items: TaskItem[]) {
  const seen = new Set<string>();
  const result: TaskItem[] = [];

  for (const item of items) {
    const title = normalizeTask(item.title);
    const key = title.toLowerCase();

    if (!title || seen.has(key) || isIgnoredRow(title)) continue;

    seen.add(key);
    result.push({ ...item, title });
  }

  return result;
}

function toFutureTask(task: string) {
  const rules: Array<[RegExp, string]> = [
    [/^проверила\b/i, "проверить"],
    [/^проверил\b/i, "проверить"],
    [/^контролировала\b/i, "проконтролировать"],
    [/^контролировал\b/i, "проконтролировать"],
    [/^обновила\b/i, "обновить"],
    [/^обновил\b/i, "обновить"],
    [/^сделала\b/i, "сделать"],
    [/^сделал\b/i, "сделать"],
    [/^работала над\b/i, "поработать над"],
    [/^работал над\b/i, "поработать над"],
    [/^работала с\b/i, "поработать с"],
    [/^работал с\b/i, "поработать с"],
    [/^опубликовала\b/i, "опубликовать"],
    [/^опубликовал\b/i, "опубликовать"],
    [/^выложила\b/i, "выложить"],
    [/^выложил\b/i, "выложить"],
    [/^написала\b/i, "написать"],
    [/^написал\b/i, "написать"],
    [/^подготовила\b/i, "подготовить"],
    [/^подготовил\b/i, "подготовить"],
    [/^переводила\b/i, "перевести"],
    [/^переводил\b/i, "перевести"],
    [/^локализовала\b/i, "локализовать"],
    [/^локализовал\b/i, "локализовать"],
    [/^собрала\b/i, "собрать"],
    [/^собрал\b/i, "собрать"],
    [/^запустила\b/i, "запустить"],
    [/^запустил\b/i, "запустить"],
  ];

  for (const [pattern, replacement] of rules) {
    if (pattern.test(task)) return task.replace(pattern, replacement);
  }

  return task;
}

function parseManualTasks(raw: string): TaskItem[] {
  return dedupeTasks(
    raw
      .split("\n")
      .map((line) => normalizeTask(line))
      .filter(Boolean)
      .filter((line) => !/^задач[аи]?:?\s*\d+/i.test(line))
      .filter((line) => !/^даты:/i.test(line))
      .map((title) => ({ title, source: "manual" as const })),
  );
}

function extractSheetId(url: string) {
  return url.match(/\/spreadsheets\/d\/([a-zA-Z0-9-_]+)/)?.[1] || "";
}

function extractGid(url: string) {
  return url.match(/[?&]gid=(\d+)/)?.[1] || "0";
}

function parseCsv(csv: string) {
  const rows: string[][] = [];
  let row: string[] = [];
  let cell = "";
  let quoted = false;

  for (let i = 0; i < csv.length; i += 1) {
    const char = csv[i];
    const next = csv[i + 1];

    if (char === '"' && quoted && next === '"') {
      cell += '"';
      i += 1;
      continue;
    }

    if (char === '"') {
      quoted = !quoted;
      continue;
    }

    if (char === "," && !quoted) {
      row.push(cell);
      cell = "";
      continue;
    }

    if ((char === "\n" || char === "\r") && !quoted) {
      if (cell || row.length) {
        row.push(cell);
        rows.push(row);
        row = [];
        cell = "";
      }
      continue;
    }

    cell += char;
  }

  if (cell || row.length) {
    row.push(cell);
    rows.push(row);
  }

  return rows;
}

function parseSheetRows(csv: string): TaskItem[] {
  const rows = parseCsv(csv);

  return dedupeTasks(
    rows.map((row) => {
      const title = normalizeTask(row[0] || "");
      const date = normalizeDate(row[1] || "");

      return {
        title,
        date: date || undefined,
        source: "sheet" as const,
      };
    }),
  );
}

function formatCopyText(params: {
  name: string;
  reportTasks: TaskItem[];
  planTasks: TaskItem[];
  reportStart: string;
  reportEnd: string;
  planStart: string;
  planEnd: string;
}) {
  const { name, reportTasks, planTasks, reportStart, reportEnd, planStart, planEnd } = params;

  return [
    `Неделя с ${toShortDate(reportStart)} по ${toShortDate(reportEnd)}`,
    "",
    name,
    `Задачи: ${reportTasks.length}`,
    ...reportTasks.map((task, index) => `${index + 1}. ${task.title}`),
    "",
    `План на неделю с ${toShortDate(planStart)} по ${toShortDate(planEnd)}`,
    "",
    name,
    `Задачи: ${planTasks.length}`,
    ...planTasks.map((task, index) => `${index + 1}. ${task.title}`),
  ].join("\n").trim();
}

export default function HomePage() {
  const baseDate = useMemo(() => new Date(todayIso()), []);

  const [name, setName] = useState("Паша");
  const [raw, setRaw] = useState("");
  const [sheetUrl, setSheetUrl] = useState("");
  const [sheetTasks, setSheetTasks] = useState<TaskItem[]>([]);
  const [routines, setRoutines] = useState<TaskItem[]>([]);
  const [movedTasks, setMovedTasks] = useState<TaskItem[]>([]);
  const [copied, setCopied] = useState(false);
  const [sheetStatus, setSheetStatus] = useState("");

  const [reportStart, setReportStart] = useState(addDays(baseDate, -7).toISOString().slice(0, 10));
  const [reportEnd, setReportEnd] = useState(addDays(baseDate, -3).toISOString().slice(0, 10));
  const [planStart, setPlanStart] = useState(todayIso());
  const [planEnd, setPlanEnd] = useState(addDays(baseDate, 3).toISOString().slice(0, 10));

  useEffect(() => {
    setName(window.localStorage.getItem(NAME_KEY) || "Паша");
    setSheetUrl(window.localStorage.getItem(SHEET_KEY) || "");

    const savedRoutines = window.localStorage.getItem(ROUTINE_KEY) || "";
    setRoutines(
      savedRoutines
        .split("\n")
        .map((title) => normalizeTask(title))
        .filter(Boolean)
        .map((title) => ({ title, source: "routine" as const })),
    );
  }, []);

  useEffect(() => {
    window.localStorage.setItem(NAME_KEY, name);
  }, [name]);

  const manualTasks = useMemo(() => parseManualTasks(raw), [raw]);
  const allSourceTasks = useMemo(() => dedupeTasks([...manualTasks, ...sheetTasks]), [manualTasks, sheetTasks]);

  const reportTasks = useMemo(() => {
    const withDates = allSourceTasks.filter((task) => task.date);
    const withoutDates = allSourceTasks.filter((task) => !task.date);

    const datedReport = withDates.filter((task) => isDateInRange(task.date, reportStart, reportEnd));

    return dedupeTasks([...datedReport, ...withoutDates]);
  }, [allSourceTasks, reportStart, reportEnd]);

  const planTasks = useMemo(() => {
    const sheetPlan = allSourceTasks
      .filter((task) => task.date)
      .filter((task) => isDateInRange(task.date, planStart, planEnd))
      .map((task) => ({ ...task, title: toFutureTask(task.title) }));

    const autoPlan = movedTasks.length
      ? movedTasks
      : reportTasks.map((task) => ({
          ...task,
          title: toFutureTask(task.title),
          source: "moved" as const,
        }));

    return dedupeTasks([...sheetPlan, ...autoPlan, ...routines]);
  }, [allSourceTasks, movedTasks, reportTasks, routines, planStart, planEnd]);

  const copyText = useMemo(
    () =>
      formatCopyText({
        name,
        reportTasks,
        planTasks,
        reportStart,
        reportEnd,
        planStart,
        planEnd,
      }),
    [name, reportTasks, planTasks, reportStart, reportEnd, planStart, planEnd],
  );

  const quote = quotes[new Date().getDate() % quotes.length];

  async function copyOutput() {
    await navigator.clipboard.writeText(copyText);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1500);
  }

  function moveToPlan(task: TaskItem) {
    setMovedTasks((current) =>
      dedupeTasks([
        ...current,
        {
          ...task,
          title: toFutureTask(task.title),
          source: "moved",
        },
      ]),
    );
  }

  async function loadFromGoogleSheets() {
    setSheetStatus("Загружаю таблицу...");

    try {
      const id = extractSheetId(sheetUrl);
      const gid = extractGid(sheetUrl);

      if (!id) {
        setSheetStatus("Не вижу ID таблицы. Проверь ссылку.");
        return;
      }

      const url = `https://docs.google.com/spreadsheets/d/${id}/gviz/tq?tqx=out:csv&gid=${gid}`;
      const response = await fetch(url);

      if (!response.ok) {
        setSheetStatus("Не удалось открыть таблицу. Нужен доступ: Anyone with the link can view.");
        return;
      }

      const csv = await response.text();
      const tasks = parseSheetRows(csv);

      setSheetTasks(tasks);
      setSheetStatus(`Загружено из вкладки: ${tasks.length} задач`);
    } catch {
      setSheetStatus("Ошибка загрузки. Проверь доступ к таблице и ссылку на нужную вкладку.");
    }
  }

  return (
    <main className="min-h-screen overflow-hidden bg-[#F1F5F9] text-[#0F172A]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_18%_12%,rgba(124,58,237,.14),transparent_28%),radial-gradient(circle_at_88%_14%,rgba(132,204,22,.16),transparent_24%),radial-gradient(circle_at_50%_100%,rgba(249,115,22,.12),transparent_28%)]" />

      {copied ? (
        <div className="fixed right-5 top-5 z-50 rounded-[14px] border border-[#84CC16]/30 bg-white px-4 py-3 text-[13px] font-bold text-[#3F6212] shadow-[0_18px_60px_rgba(132,204,22,.25)]">
          Готово. Текст скопирован.
        </div>
      ) : null}

      <section className="relative mx-auto flex h-screen max-w-7xl flex-col px-5 py-4">
        <header className="mb-3 flex h-[54px] items-center justify-between">
          <div className="group flex items-center gap-3">
            <div className="grid size-11 place-items-center rounded-[14px] bg-[#F97316] shadow-[0_10px_30px_rgba(249,115,22,.28)] transition duration-150 group-hover:-translate-y-0.5 group-hover:shadow-[0_16px_45px_rgba(249,115,22,.38)]">
              <span className="font-serif text-[30px] font-black leading-none text-[#B6FF2E] drop-shadow-[0_0_8px_rgba(182,255,46,.45)]">П</span>
            </div>
            <div>
              <div className="text-[19px] font-black tracking-[-.02em]">ПЛАНИФИКАТОР-3000</div>
              <div className="text-[12px] font-medium text-slate-500">Не придумывай. Не угадывай. Не усложняй.</div>
            </div>
          </div>

          <Link
            href="/settings"
            aria-label="Настройки"
            className="grid size-11 place-items-center rounded-[14px] border border-slate-900/10 bg-white text-[20px] shadow-sm transition duration-150 hover:-translate-y-0.5 hover:border-[#7C3AED]/30 hover:shadow-[0_14px_45px_rgba(124,58,237,.18)]"
          >
            ⚙
          </Link>
        </header>

        <div className="mb-3 grid gap-3 md:grid-cols-4">
          <Metric label="Сделано за неделю" value={reportTasks.length} tone="lime" />
          <Metric label="Сделано за месяц" value={reportTasks.length * 4} tone="violet" />
          <Metric label="Сделано за 2 месяца" value={reportTasks.length * 8} tone="orange" />
          <Metric label="План на неделю" value={planTasks.length} tone="sky" />
        </div>

        <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[.96fr_1.04fr]">
          <section className="flex min-h-0 flex-col rounded-[14px] border border-slate-900/10 bg-white/90 p-4 shadow-[0_18px_80px_rgba(15,23,42,.08)] backdrop-blur transition duration-150 hover:shadow-[0_22px_90px_rgba(124,58,237,.12)]">
            <div className="mb-3 grid gap-3 md:grid-cols-[1fr_1.4fr]">
              <Field label="Имя">
                <input value={name} onChange={(event) => setName(event.target.value)} className="input" />
              </Field>

              <Field label="Даты отчёта">
                <div className="grid grid-cols-2 gap-2">
                  <input type="date" value={reportStart} onChange={(event) => setReportStart(event.target.value)} className="input date-input" />
                  <input type="date" value={reportEnd} onChange={(event) => setReportEnd(event.target.value)} className="input date-input" />
                </div>
              </Field>
            </div>

            <div className="mb-3 flex flex-wrap items-center gap-2">
              <button onClick={loadFromGoogleSheets} className="btn-secondary">
                Загрузить из Google Sheets
              </button>
              <span className="text-[11px] font-semibold text-slate-500">{sheetStatus}</span>
            </div>

            <textarea
              value={raw}
              onChange={(event) => setRaw(event.target.value)}
              placeholder="Можно вставить черновик вручную. Если загружаешь таблицу: берём столбец A, дату из столбца B, ссылки из C игнорируем."
              className="h-[145px] resize-none rounded-[14px] border border-slate-900/10 bg-[#F8FAFC] p-4 text-[13px] leading-6 outline-none transition duration-150 focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
            />

            <TaskPanel
              title="Отчёт за неделю"
              subtitle={`Задачи: ${reportTasks.length}`}
              tasks={reportTasks}
              actionLabel="→"
              onAction={moveToPlan}
            />
          </section>

          <section className="flex min-h-0 flex-col rounded-[14px] border border-slate-900/10 bg-white/90 p-4 shadow-[0_18px_80px_rgba(15,23,42,.08)] backdrop-blur transition duration-150 hover:shadow-[0_22px_90px_rgba(132,204,22,.14)]">
            <div className="mb-3 grid gap-3 md:grid-cols-[1fr_auto]">
              <Field label="Даты плана">
                <div className="grid grid-cols-2 gap-2">
                  <input type="date" value={planStart} onChange={(event) => setPlanStart(event.target.value)} className="input date-input" />
                  <input type="date" value={planEnd} onChange={(event) => setPlanEnd(event.target.value)} className="input date-input" />
                </div>
              </Field>

              <div className="flex items-end">
                <button onClick={copyOutput} className="btn-primary">Скопировать</button>
              </div>
            </div>

            <TaskPanel
              title="План на неделю"
              subtitle={`Задачи: ${planTasks.length}`}
              tasks={planTasks}
            />

            <details className="mt-3 rounded-[14px] border border-slate-900/10 bg-[#F8FAFC] p-3">
              <summary className="cursor-pointer text-[12px] font-bold text-slate-500">Текст для копирования</summary>
              <pre className="mt-3 max-h-[170px] overflow-auto whitespace-pre-wrap rounded-[10px] bg-white p-3 text-[12px] leading-5 text-slate-700">
                {copyText}
              </pre>
            </details>
          </section>
        </div>

        <footer className="mt-3 flex h-[34px] items-center justify-center rounded-[999px] bg-white/70 px-4 text-center text-[12px] font-semibold text-slate-500 shadow-sm backdrop-blur">
          {quote}
        </footer>
      </section>

      <style jsx global>{`
        .input {
          width: 100%;
          border-radius: 10px;
          border: 1px solid rgba(15, 23, 42, 0.1);
          background: #f8fafc;
          padding: 9px 10px;
          font-size: 12px;
          font-weight: 700;
          outline: none;
          transition: 0.15s ease;
        }

        .date-input {
          min-width: 140px;
        }

        .input:focus {
          border-color: #7c3aed;
          background: #fff;
          box-shadow: 0 0 0 4px rgba(124, 58, 237, 0.1);
        }

        .btn-primary {
          border-radius: 10px;
          background: #7c3aed;
          color: #fff;
          padding: 10px 16px;
          font-size: 13px;
          font-weight: 800;
          transition: 0.15s ease;
          box-shadow: 0 10px 30px rgba(124, 58, 237, 0.22);
        }

        .btn-primary:hover {
          transform: translateY(-2px);
          box-shadow: 0 18px 55px rgba(124, 58, 237, 0.34);
        }

        .btn-secondary {
          border-radius: 10px;
          border: 1px solid rgba(15, 23, 42, 0.1);
          background: #fff;
          padding: 9px 13px;
          font-size: 12px;
          font-weight: 800;
          transition: 0.15s ease;
        }

        .btn-secondary:hover {
          transform: translateY(-1px);
          box-shadow: 0 12px 35px rgba(15, 23, 42, 0.1);
        }
      `}</style>
    </main>
  );
}

function Field({ label, children }: { label: string; children: ReactNode }) {
  return (
    <label className="block">
      <span className="mb-1 block text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">{label}</span>
      {children}
    </label>
  );
}

function TaskPanel({
  title,
  subtitle,
  tasks,
  actionLabel,
  onAction,
}: {
  title: string;
  subtitle: string;
  tasks: TaskItem[];
  actionLabel?: string;
  onAction?: (task: TaskItem) => void;
}) {
  return (
    <section className="mt-3 min-h-0 flex-1 overflow-hidden rounded-[14px] border border-slate-900/10 bg-[#F8FAFC]">
      <div className="flex items-center justify-between border-b border-slate-900/10 bg-white px-4 py-3">
        <div>
          <div className="text-[14px] font-black tracking-[-.02em]">{title}</div>
          <div className="text-[11px] font-bold text-slate-400">{subtitle}</div>
        </div>
      </div>

      <ol className="h-full max-h-[360px] space-y-2 overflow-auto p-3">
        {tasks.length ? (
          tasks.map((task, index) => (
            <li
              key={`${task.title}-${index}`}
              className="group flex items-start gap-3 rounded-[10px] border border-slate-900/10 bg-white p-3 shadow-sm transition duration-150 hover:-translate-y-0.5 hover:border-[#7C3AED]/20 hover:shadow-[0_14px_45px_rgba(124,58,237,.14)]"
            >
              <span className="grid size-6 shrink-0 place-items-center rounded-full bg-[#7C3AED]/10 text-[11px] font-black text-[#7C3AED]">
                {index + 1}
              </span>

              <div className="min-w-0 flex-1">
                <div className="text-[13px] font-bold leading-5 text-slate-800">{task.title}</div>
                {task.date ? (
                  <div className="mt-1 text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">
                    дата: {task.date}
                  </div>
                ) : null}
              </div>

              {onAction && actionLabel ? (
                <button
                  onClick={() => onAction(task)}
                  className="rounded-[8px] bg-[#84CC16]/15 px-2 py-1 text-[13px] font-black text-[#3F6212] transition hover:-translate-y-0.5 hover:bg-[#84CC16] hover:text-white hover:shadow-[0_10px_30px_rgba(132,204,22,.25)]"
                >
                  {actionLabel}
                </button>
              ) : null}
            </li>
          ))
        ) : (
          <li className="rounded-[10px] border border-dashed border-slate-900/10 bg-white p-4 text-[13px] font-medium text-slate-400">
            Пока нет задач.
          </li>
        )}
      </ol>
    </section>
  );
}

function Metric({ label, value, tone }: { label: string; value: number; tone: "lime" | "violet" | "orange" | "sky" }) {
  const tones = {
    lime: "bg-[#84CC16]/15 text-[#3F6212] shadow-[0_12px_40px_rgba(132,204,22,.16)]",
    violet: "bg-[#7C3AED]/10 text-[#7C3AED] shadow-[0_12px_40px_rgba(124,58,237,.14)]",
    orange: "bg-[#F97316]/10 text-[#C2410C] shadow-[0_12px_40px_rgba(249,115,22,.14)]",
    sky: "bg-[rgba(14,165,233,.08)] text-[#0369A1] shadow-[0_12px_40px_rgba(14,165,233,.12)]",
  };

  return (
    <div className="rounded-[14px] border border-slate-900/10 bg-white p-3 transition duration-150 hover:-translate-y-0.5 hover:shadow-[0_18px_60px_rgba(15,23,42,.12)]">
      <div className="text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">{label}</div>
      <div className={`mt-1 inline-flex rounded-[8px] px-3 py-1 text-[24px] font-black tracking-[-.02em] ${tones[tone]}`}>
        {value}
      </div>
    </div>
  );
}
