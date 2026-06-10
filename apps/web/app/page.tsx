/* global window, navigator */
"use client";

import { useEffect, useMemo, useState } from "react";

type OutputMode = "report" | "plan";

const DEFAULT_NAME = "Саша";

function todayIso() {
  return new Date().toISOString().slice(0, 10);
}

function addDays(date: Date, days: number) {
  const next = new Date(date);
  next.setDate(next.getDate() + days);
  return next;
}

function toRuDate(value: string) {
  if (!value) return "";
  const [year, month, day] = value.split("-");
  return `${day}.${month}.${year}`;
}

function shortRuDate(value: string) {
  if (!value) return "";
  const [, month, day] = value.split("-");
  return `${day}.${month}`;
}

function normalizeLine(line: string) {
  return line
    .replace(/^[-*•]\s*/, "")
    .replace(/^\d+[).]\s*/, "")
    .replace(/\s+/g, " ")
    .trim();
}

function dedupeTasks(lines: string[]) {
  const seen = new Set<string>();
  const result: string[] = [];

  for (const line of lines) {
    const task = normalizeLine(line);
    const key = task.toLowerCase();

    if (!task || seen.has(key)) continue;

    seen.add(key);
    result.push(task);
  }

  return result;
}

function toFutureTask(task: string) {
  const replacements: Array<[RegExp, string]> = [
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
  ];

  for (const [pattern, replacement] of replacements) {
    if (pattern.test(task)) return task.replace(pattern, replacement);
  }

  return task;
}

function formatOutput(params: {
  name: string;
  tasks: string[];
  mode: OutputMode;
  startDate: string;
  endDate: string;
}) {
  const { name, tasks, mode, startDate, endDate } = params;
  const finalTasks = mode === "plan" ? tasks.map(toFutureTask) : tasks;

  const title =
    mode === "report"
      ? `Отчётная неделя:\nДаты: ${toRuDate(startDate)} – ${toRuDate(endDate)}\n${name}\nЗадач было в работе: ${finalTasks.length}`
      : `План на неделю:\nДаты: ${shortRuDate(startDate)} до ${shortRuDate(endDate)}\n${name}\nЗадач запланировано: ${finalTasks.length}`;

  const list = finalTasks.map((task, index) => `${index + 1}. ${task}`).join("\n");

  return list ? `${title}\n${list}` : title;
}

export default function HomePage() {
  const baseDate = useMemo(() => new Date(todayIso()), []);
  const defaultReportStart = addDays(baseDate, -7).toISOString().slice(0, 10);
  const defaultReportEnd = addDays(baseDate, -1).toISOString().slice(0, 10);
  const defaultPlanStart = todayIso();
  const defaultPlanEnd = addDays(baseDate, 6).toISOString().slice(0, 10);

  const [raw, setRaw] = useState("");
  const [name, setName] = useState(DEFAULT_NAME);
  const [sheetUrl, setSheetUrl] = useState("");
  const [mode, setMode] = useState<OutputMode>("report");
  const [reportStart, setReportStart] = useState(defaultReportStart);
  const [reportEnd, setReportEnd] = useState(defaultReportEnd);
  const [planStart, setPlanStart] = useState(defaultPlanStart);
  const [planEnd, setPlanEnd] = useState(defaultPlanEnd);

  useEffect(() => {
    const savedName = window.localStorage.getItem("planner3000:name");
    const savedSheetUrl = window.localStorage.getItem("planner3000:sheetUrl");

    if (savedName) setName(savedName);
    if (savedSheetUrl) setSheetUrl(savedSheetUrl);
  }, []);

  useEffect(() => {
    window.localStorage.setItem("planner3000:name", name);
  }, [name]);

  useEffect(() => {
    window.localStorage.setItem("planner3000:sheetUrl", sheetUrl);
  }, [sheetUrl]);

  const tasks = useMemo(() => dedupeTasks(raw.split("\n")), [raw]);

  const output = useMemo(
    () =>
      formatOutput({
        name,
        tasks,
        mode,
        startDate: mode === "report" ? reportStart : planStart,
        endDate: mode === "report" ? reportEnd : planEnd,
      }),
    [name, tasks, mode, reportStart, reportEnd, planStart, planEnd],
  );

  async function copyOutput() {
    await navigator.clipboard.writeText(output);
  }

  return (
    <main className="min-h-screen bg-[#F1F5F9] text-[#0F172A]">
      <section className="mx-auto flex min-h-screen max-w-7xl flex-col px-5 py-5">
        <header className="mb-4 flex items-center justify-between">
          <div className="flex items-center gap-3">
            <div className="grid size-10 place-items-center rounded-[12px] bg-[#F97316] text-[22px] font-black text-[#84CC16] shadow-sm">
              П
            </div>
            <div>
              <div className="text-[19px] font-black tracking-[-.02em]">ПЛАНИФИКАТОР-3000</div>
              <div className="text-[12px] font-medium text-slate-500">Не придумывай. Не угадывай. Не усложняй.</div>
            </div>
          </div>
        </header>

        <div className="grid flex-1 gap-4 lg:grid-cols-2">
          <section className="flex min-h-[720px] flex-col rounded-[14px] border border-slate-900/10 bg-white p-4 shadow-sm">
            <div className="mb-3 grid gap-3 md:grid-cols-[1fr_1fr]">
              <label className="block">
                <span className="mb-1 block text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Имя</span>
                <input
                  value={name}
                  onChange={(event) => setName(event.target.value)}
                  className="w-full rounded-[10px] border border-slate-900/10 bg-slate-50 px-3 py-2 text-[13px] font-semibold outline-none focus:border-[#7C3AED] focus:ring-4 focus:ring-[#7C3AED]/10"
                />
              </label>

              <label className="block">
                <span className="mb-1 block text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Режим</span>
                <select
                  value={mode}
                  onChange={(event) => setMode(event.target.value as OutputMode)}
                  className="w-full rounded-[10px] border border-slate-900/10 bg-slate-50 px-3 py-2 text-[13px] font-semibold outline-none focus:border-[#7C3AED] focus:ring-4 focus:ring-[#7C3AED]/10"
                >
                  <option value="report">Отчёт за неделю</option>
                  <option value="plan">План на неделю</option>
                </select>
              </label>
            </div>

            <div className="mb-3 grid gap-3 md:grid-cols-2">
              <label className="block">
                <span className="mb-1 block text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Начало</span>
                <input
                  type="date"
                  value={mode === "report" ? reportStart : planStart}
                  onChange={(event) => (mode === "report" ? setReportStart(event.target.value) : setPlanStart(event.target.value))}
                  className="w-full rounded-[10px] border border-slate-900/10 bg-slate-50 px-3 py-2 text-[13px] font-semibold outline-none focus:border-[#7C3AED] focus:ring-4 focus:ring-[#7C3AED]/10"
                />
              </label>

              <label className="block">
                <span className="mb-1 block text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Конец</span>
                <input
                  type="date"
                  value={mode === "report" ? reportEnd : planEnd}
                  onChange={(event) => (mode === "report" ? setReportEnd(event.target.value) : setPlanEnd(event.target.value))}
                  className="w-full rounded-[10px] border border-slate-900/10 bg-slate-50 px-3 py-2 text-[13px] font-semibold outline-none focus:border-[#7C3AED] focus:ring-4 focus:ring-[#7C3AED]/10"
                />
              </label>
            </div>

            <details className="mb-3 rounded-[10px] border border-slate-900/10 bg-slate-50 px-3 py-2">
              <summary className="cursor-pointer text-[12px] font-bold text-slate-600">Настройки и Google Таблица</summary>
              <input
                value={sheetUrl}
                onChange={(event) => setSheetUrl(event.target.value)}
                placeholder="Ссылка на Google Таблицу — пока хранится как настройка"
                className="mt-3 w-full rounded-[10px] border border-slate-900/10 bg-white px-3 py-2 text-[13px] outline-none focus:border-[#7C3AED] focus:ring-4 focus:ring-[#7C3AED]/10"
              />
            </details>

            <textarea
              value={raw}
              onChange={(event) => setRaw(event.target.value)}
              placeholder="Вставь сюда черновик из чата, старый отчёт, правила команды или контекст недели."
              className="flex-1 resize-none rounded-[14px] border border-slate-900/10 bg-slate-50 p-4 text-[14px] leading-7 outline-none transition focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
            />

            <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
              <div className="text-[12px] font-semibold text-slate-500">Найдено задач: {tasks.length}</div>
              <button
                onClick={() => setRaw("")}
                className="rounded-[10px] border border-slate-900/10 bg-white px-4 py-2 text-[13px] font-bold transition hover:-translate-y-0.5"
              >
                Очистить
              </button>
            </div>
          </section>

          <section className="flex min-h-[720px] flex-col rounded-[14px] border border-slate-900/10 bg-white p-4 shadow-sm">
            <div className="mb-3 flex items-center justify-between gap-3">
              <div>
                <div className="text-[20px] font-black tracking-[-.02em]">
                  {mode === "report" ? "Готовый отчёт" : "Готовый план"}
                </div>
                <div className="text-[12px] font-medium text-slate-500">Задача = действие + объект + контекст</div>
              </div>

              <button
                onClick={copyOutput}
                className="rounded-[10px] bg-[#7C3AED] px-4 py-2 text-[13px] font-bold text-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
              >
                Скопировать
              </button>
            </div>

            <pre className="flex-1 whitespace-pre-wrap rounded-[14px] border border-slate-900/10 bg-[#F8FAFC] p-5 text-[14px] leading-7 text-slate-900">
              {output}
            </pre>
          </section>
        </div>
      </section>
    </main>
  );
}
