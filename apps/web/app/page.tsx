/* global window, navigator */
"use client";

import Link from "next/link";
import type { ReactNode } from "react";
import { useEffect, useMemo, useState } from "react";

type PersonBlock = {
  name: string;
  tasks: string[];
};

const DEFAULT_NAME = "Паша";
const ROUTINE_KEY = "planner3000:routines";
const NAME_KEY = "planner3000:name";

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

function looksLikeName(line: string) {
  const clean = normalizeTask(line);
  if (!clean) return false;
  if (clean.length > 28) return false;
  if (clean.includes(":")) return false;
  if (/задач|неделя|план|важно|даты/i.test(clean)) return false;
  return /^[А-ЯA-ZЁ][а-яa-zё]+(?:\s+[А-ЯA-ZЁ][а-яa-zё]+)?$/.test(clean);
}

function isContextLine(line: string) {
  return /важно|выходной|сокращ|отпуск|больнич|срочн|дедлайн|контекст/i.test(line);
}

function dedupe(items: string[]) {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const item of items) {
    const clean = normalizeTask(item);
    const key = clean.toLowerCase();
    if (!clean || seen.has(key)) continue;
    seen.add(key);
    result.push(clean);
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

function parseInput(raw: string, fallbackName: string, routines: string[]) {
  const lines = raw.split("\n").map((line) => line.trim()).filter(Boolean);
  const reportMap = new Map<string, string[]>();
  const planMap = new Map<string, string[]>();
  const context: string[] = [];

  let mode: "report" | "plan" = "report";
  let currentName = fallbackName;

  function addTask(name: string, task: string, target: "report" | "plan") {
    const clean = normalizeTask(task);
    if (!clean) return;

    const map = target === "report" ? reportMap : planMap;
    const existing = map.get(name) ?? [];
    existing.push(clean);
    map.set(name, existing);
  }

  for (const line of lines) {
    const normalized = normalizeTask(line);
    const lower = normalized.toLowerCase();

    if (isContextLine(normalized)) {
      context.push(normalized);
      continue;
    }

    if (/план на неделю|новая неделя|следующ/i.test(lower)) {
      mode = "plan";
      continue;
    }

    if (/отч[её]тная неделя|неделя с|прошл/i.test(lower)) {
      mode = "report";
      continue;
    }

    if (/^задач[аи]?:?\s*\d+/i.test(lower) || /^даты:/i.test(lower)) {
      continue;
    }

    if (looksLikeName(normalized)) {
      currentName = normalized;
      if (!reportMap.has(currentName)) reportMap.set(currentName, []);
      if (!planMap.has(currentName)) planMap.set(currentName, []);
      continue;
    }

    addTask(currentName, normalized, mode);
  }

  if (!raw.trim() && fallbackName) {
    reportMap.set(fallbackName, []);
  }

  const report = Array.from(reportMap.entries()).map(([name, tasks]) => ({
    name,
    tasks: dedupe(tasks),
  }));

  const plan = Array.from(planMap.entries()).map(([name, tasks]) => ({
    name,
    tasks: dedupe([...tasks, ...routines]).map(toFutureTask),
  }));

  if (plan.length === 0 && report.length > 0) {
    for (const person of report) {
      plan.push({
        name: person.name,
        tasks: dedupe([...person.tasks.map(toFutureTask), ...routines]),
      });
    }
  }

  return {
    report,
    plan,
    context: dedupe(context),
  };
}

function formatOutput(data: { report: PersonBlock[]; plan: PersonBlock[]; context: string[] }, reportStart: string, reportEnd: string, planStart: string, planEnd: string) {
  const reportParts = [
    `Неделя с ${toShortDate(reportStart)} по ${toShortDate(reportEnd)}`,
    "",
    ...data.report.flatMap((person) => [
      person.name,
      `Задачи: ${person.tasks.length}`,
      ...person.tasks.map((task, index) => `${index + 1}. ${task}`),
      "",
    ]),
  ];

  const contextParts = data.context.length
    ? ["Важно:", ...data.context.map((item) => `• ${item}`), ""]
    : [];

  const planParts = [
    `План на неделю с ${toShortDate(planStart)} по ${toShortDate(planEnd)}`,
    "",
    ...data.plan.flatMap((person) => [
      person.name,
      `Задачи: ${person.tasks.length}`,
      ...person.tasks.map((task, index) => `${index + 1}. ${task}`),
      "",
    ]),
  ];

  return [...reportParts, ...contextParts, ...planParts].join("\n").trim();
}

export default function HomePage() {
  const baseDate = useMemo(() => new Date(todayIso()), []);
  const [name, setName] = useState(DEFAULT_NAME);
  const [raw, setRaw] = useState("");
  const [routines, setRoutines] = useState<string[]>([]);
  const [reportStart, setReportStart] = useState(addDays(baseDate, -7).toISOString().slice(0, 10));
  const [reportEnd, setReportEnd] = useState(addDays(baseDate, -3).toISOString().slice(0, 10));
  const [planStart, setPlanStart] = useState(todayIso());
  const [planEnd, setPlanEnd] = useState(addDays(baseDate, 3).toISOString().slice(0, 10));
  const [copied, setCopied] = useState(false);

  useEffect(() => {
    const savedName = window.localStorage.getItem(NAME_KEY);
    const savedRoutines = window.localStorage.getItem(ROUTINE_KEY);

    if (savedName) setName(savedName);
    if (savedRoutines) setRoutines(savedRoutines.split("\n").map(normalizeTask).filter(Boolean));
  }, []);

  useEffect(() => {
    window.localStorage.setItem(NAME_KEY, name);
  }, [name]);

  const data = useMemo(() => parseInput(raw, name, routines), [raw, name, routines]);

  const output = useMemo(
    () => formatOutput(data, reportStart, reportEnd, planStart, planEnd),
    [data, reportStart, reportEnd, planStart, planEnd],
  );

  const doneWeek = data.report.reduce((sum, person) => sum + person.tasks.length, 0);
  const plannedWeek = data.plan.reduce((sum, person) => sum + person.tasks.length, 0);
  const doneMonth = doneWeek * 4;
  const doneTwoMonths = doneWeek * 8;
  const quote = quotes[new Date().getDate() % quotes.length];

  async function copyOutput() {
    await navigator.clipboard.writeText(output);
    setCopied(true);
    window.setTimeout(() => setCopied(false), 1600);
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
        <header className="mb-4 flex h-[54px] items-center justify-between">
          <div className="group flex items-center gap-3">
            <div className="grid size-11 place-items-center rounded-[14px] bg-[#F97316] text-[24px] font-black text-[#B6FF2E] shadow-[0_10px_30px_rgba(249,115,22,.28)] transition duration-150 group-hover:-translate-y-0.5 group-hover:shadow-[0_16px_45px_rgba(249,115,22,.38)]">
              П
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

        <div className="mb-4 grid gap-3 md:grid-cols-4">
          <Metric label="Сделано за неделю" value={doneWeek} tone="lime" />
          <Metric label="Сделано за месяц" value={doneMonth} tone="violet" />
          <Metric label="Сделано за 2 месяца" value={doneTwoMonths} tone="orange" />
          <Metric label="План на неделю" value={plannedWeek} tone="sky" />
        </div>

        <div className="grid min-h-0 flex-1 gap-4 lg:grid-cols-[.92fr_1.08fr]">
          <section className="flex min-h-0 flex-col rounded-[14px] border border-slate-900/10 bg-white/90 p-4 shadow-[0_18px_80px_rgba(15,23,42,.08)] backdrop-blur transition duration-150 hover:shadow-[0_22px_90px_rgba(124,58,237,.12)]">
            <div className="mb-3 grid gap-3 md:grid-cols-[1fr_1fr_1fr]">
              <Field label="Имя">
                <input value={name} onChange={(event) => setName(event.target.value)} className="input" />
              </Field>
              <Field label="Отчёт">
                <div className="grid grid-cols-2 gap-2">
                  <input type="date" value={reportStart} onChange={(event) => setReportStart(event.target.value)} className="input" />
                  <input type="date" value={reportEnd} onChange={(event) => setReportEnd(event.target.value)} className="input" />
                </div>
              </Field>
              <Field label="План">
                <div className="grid grid-cols-2 gap-2">
                  <input type="date" value={planStart} onChange={(event) => setPlanStart(event.target.value)} className="input" />
                  <input type="date" value={planEnd} onChange={(event) => setPlanEnd(event.target.value)} className="input" />
                </div>
              </Field>
            </div>

            <textarea
              value={raw}
              onChange={(event) => setRaw(event.target.value)}
              placeholder="Вставь сюда черновик из чата, отчёт прошлой недели, правила команды или контекст: отпуска, выходные, срочные проекты."
              className="min-h-0 flex-1 resize-none rounded-[14px] border border-slate-900/10 bg-[#F8FAFC] p-4 text-[13px] leading-6 outline-none transition duration-150 focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
            />

            <div className="mt-3 flex items-center justify-between">
              <span className="rounded-full bg-[#7C3AED]/10 px-3 py-2 text-[11px] font-bold text-[#7C3AED]">
                Найдено: {doneWeek} задач
              </span>
              <button onClick={() => setRaw("")} className="btn-secondary">Очистить</button>
            </div>
          </section>

          <section className="flex min-h-0 flex-col rounded-[14px] border border-slate-900/10 bg-white/90 p-4 shadow-[0_18px_80px_rgba(15,23,42,.08)] backdrop-blur transition duration-150 hover:shadow-[0_22px_90px_rgba(132,204,22,.14)]">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <div className="text-[20px] font-black tracking-[-.02em]">Готовый документ</div>
                <div className="text-[12px] font-medium text-slate-500">Отчётная неделя + план на следующую неделю</div>
              </div>
              <button onClick={copyOutput} className="btn-primary">Скопировать</button>
            </div>

            <pre className="min-h-0 flex-1 overflow-auto whitespace-pre-wrap rounded-[14px] border border-slate-900/10 bg-[#F8FAFC] p-5 text-[13px] leading-6 text-slate-900 shadow-inner">
              {output}
            </pre>
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
          padding: 10px 14px;
          font-size: 13px;
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

function Metric({ label, value, tone }: { label: string; value: number; tone: "lime" | "violet" | "orange" | "sky" }) {
  const tones = {
    lime: "bg-[#84CC16]/15 text-[#3F6212] shadow-[0_12px_40px_rgba(132,204,22,.16)]",
    violet: "bg-[#7C3AED]/10 text-[#7C3AED] shadow-[0_12px_40px_rgba(124,58,237,.14)]",
    orange: "bg-[#F97316]/10 text-[#C2410C] shadow-[0_12px_40px_rgba(249,115,22,.14)]",
    sky: "bg-[rgba(14,165,233,.08)] text-[#0369A1] shadow-[0_12px_40px_rgba(14,165,233,.12)]",
  };

  return (
    <div className="rounded-[14px] border border-slate-900/10 bg-white p-4 transition duration-150 hover:-translate-y-0.5 hover:shadow-[0_18px_60px_rgba(15,23,42,.12)]">
      <div className="text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">{label}</div>
      <div className={`mt-2 inline-flex rounded-[8px] px-3 py-1 text-[26px] font-black tracking-[-.02em] ${tones[tone]}`}>
        {value}
      </div>
    </div>
  );
}
