/* global navigator */
"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";

type TaskStatus = "done" | "progress" | "planned" | "backlog";

type ParsedTask = {
  title: string;
  date?: string;
  owner?: string;
  status: TaskStatus;
  estimate: number;
};

const placeholder = `Пример:
2026-06-03 анализ статей блога за второе полугодие 2025
обновление данных по рейтингам за январь
написание статей Alternatives в новом формате
поиск новых упоминаний бренда по региону
публикации в Linkedin
Reels / Shorts
готово: еженедельный отчет
в работе: исследование конкурентов
бэклог: обновление старых Alternatives`;

function detectStatus(line: string, section: TaskStatus): TaskStatus {
  const lower = line.toLowerCase();

  if (lower.includes("готово") || lower.includes("сделано") || lower.includes("done") || lower.includes("completed")) {
    return "done";
  }

  if (lower.includes("в работе") || lower.includes("делаю") || lower.includes("progress") || lower.includes("doing")) {
    return "progress";
  }

  if (lower.includes("бэклог") || lower.includes("backlog") || lower.includes("потом") || lower.includes("отлож")) {
    return "backlog";
  }

  return section;
}

function cleanTitle(line: string): string {
  return line
    .replace(/^[-*•]\s*/, "")
    .replace(/^\d+\.\s*/, "")
    .replace(/\b\d{4}-\d{2}-\d{2}\b/g, "")
    .replace(/\b\d+(?:\.\d+)?\s*(h|ч|час|часа|часов)\b/gi, "")
    .replace(/^(готово|сделано|в работе|бэклог|план|задача)\s*[:—-]\s*/i, "")
    .replace(/\s+/g, " ")
    .trim();
}

function parseTasks(raw: string): ParsedTask[] {
  let currentSection: TaskStatus = "planned";

  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter(Boolean)
    .flatMap((line) => {
      const lower = line.toLowerCase();

      if (["готово", "сделано", "прошлая неделя", "previous week", "completed tasks"].some((word) => lower.includes(word)) && line.length < 35) {
        currentSection = "done";
        return [];
      }

      if (["новая неделя", "план", "next week", "new week"].some((word) => lower.includes(word)) && line.length < 35) {
        currentSection = "planned";
        return [];
      }

      if (["бэклог", "backlog", "отложено"].some((word) => lower.includes(word)) && line.length < 35) {
        currentSection = "backlog";
        return [];
      }

      const date = line.match(/\d{4}-\d{2}-\d{2}/)?.[0];
      const estimateMatch = line.match(/(\d+(?:\.\d+)?)\s*(h|ч|час|часа|часов)/i);
      const title = cleanTitle(line);

      if (!title || title.length < 3) {
        return [];
      }

      return [
        {
          title,
          date,
          status: detectStatus(line, currentSection),
          estimate: estimateMatch ? Number(estimateMatch[1]) : 2,
        },
      ];
    });
}

function byStatus(tasks: ParsedTask[], status: TaskStatus) {
  return tasks.filter((task) => task.status === status);
}

export default function HomePage() {
  const [raw, setRaw] = useState("");

  const tasks = useMemo(() => parseTasks(raw), [raw]);
  const done = byStatus(tasks, "done");
  const progress = byStatus(tasks, "progress");
  const planned = byStatus(tasks, "planned");
  const backlog = byStatus(tasks, "backlog");

  const plannedHours = planned.reduce((sum, task) => sum + task.estimate, 0);
  const doneHours = done.reduce((sum, task) => sum + task.estimate, 0);

  return (
    <main className="min-h-screen bg-[#F1F5F9] text-[#0F172A]">
      <section className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6 rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-sm">
          <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">
            <div className="flex items-center gap-3">
              <div className="grid size-10 place-items-center rounded-[10px] bg-[#84CC16] font-black text-white">П</div>
              <div>
                <p className="text-[19px] font-extrabold tracking-[-.02em]">ПЛАНИФИКАТОР-3000</p>
                <p className="text-xs font-medium text-slate-500">Простой помощник для недельного планирования</p>
              </div>
            </div>

            <div className="flex flex-wrap gap-2 text-[11px] font-bold">
              <span className="rounded-full bg-[#7C3AED]/10 px-3 py-2 text-[#7C3AED]">Порядок в задачах</span>
              <span className="rounded-full bg-[#84CC16]/15 px-3 py-2 text-[#3F6212]">Фокус на работе</span>
              <span className="rounded-full bg-[#F97316]/10 px-3 py-2 text-[#C2410C]">План без хаоса</span>
            </div>
          </div>
        </header>

        <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
          <section className="rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-sm">
            <p className="text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Шаг 1</p>
            <h1 className="mt-1 text-[34px] font-extrabold tracking-[-.02em]">Вставь список задач</h1>
            <p className="mt-2 text-[13px] leading-6 text-slate-500">
              Можно вставить обычный текст: задачи, даты, статусы, часы. Система сама соберёт понятный отчёт и план.
            </p>

            <textarea
              value={raw}
              onChange={(event) => setRaw(event.target.value)}
              placeholder={placeholder}
              className="mt-5 min-h-[520px] w-full resize-none rounded-[10px] border border-slate-900/10 bg-slate-50 p-4 text-[13px] leading-6 outline-none transition focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
            />

            <div className="mt-4 flex flex-wrap gap-3">
              <button
                onClick={() => setRaw("")}
                className="rounded-[10px] border border-slate-900/10 bg-white px-4 py-3 text-[13px] font-bold transition hover:-translate-y-0.5"
              >
                Очистить
              </button>
              <button
                onClick={() => navigator.clipboard.writeText(raw)}
                className="rounded-[10px] bg-[#F97316] px-4 py-3 text-[13px] font-bold text-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
              >
                Скопировать исходник
              </button>
            </div>
          </section>

          <section className="space-y-5">
            <section className="rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-sm">
              <p className="text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Шаг 2</p>
              <h2 className="mt-1 text-[34px] font-extrabold tracking-[-.02em]">Отчёт и план</h2>

              <div className="mt-5 grid gap-3 md:grid-cols-4">
                <Metric label="Найдено задач" value={tasks.length} tone="violet" />
                <Metric label="Готово" value={done.length} tone="lime" />
                <Metric label="План, часов" value={`${plannedHours}ч`} tone="orange" />
                <Metric label="Бэклог" value={backlog.length} tone="red" />
              </div>
            </section>

            <ReportCard title="Итоги недели" subtitle={`${done.length} готово · примерно ${doneHours}ч работы`}>
              {done.length ? done.map((task) => <TaskRow key={task.title} task={task} />) : <Empty text="Пока нет задач со статусом «готово»." />}
              {progress.length ? (
                <>
                  <Divider label="В работе" />
                  {progress.map((task) => <TaskRow key={task.title} task={task} />)}
                </>
              ) : null}
            </ReportCard>

            <ReportCard title="План на следующую неделю" subtitle={`${planned.length} задач · примерно ${plannedHours}ч`}>
              {planned.length ? planned.map((task) => <TaskRow key={task.title} task={task} />) : <Empty text="Вставь список задач — план появится здесь." />}
            </ReportCard>

            <ReportCard title="Отложенные задачи" subtitle={`${backlog.length} задач в бэклоге`}>
              {backlog.length ? backlog.map((task) => <TaskRow key={task.title} task={task} />) : <Empty text="Отложенных задач не найдено." />}
            </ReportCard>
          </section>
        </div>
      </section>
    </main>
  );
}

function Metric({ label, value, tone }: { label: string; value: string | number; tone: "violet" | "lime" | "orange" | "red" }) {
  const tones = {
    violet: "bg-[#7C3AED]/10 text-[#7C3AED]",
    lime: "bg-[#84CC16]/15 text-[#3F6212]",
    orange: "bg-[#F97316]/10 text-[#C2410C]",
    red: "bg-[#EF4444]/10 text-[#B91C1C]",
  };

  return (
    <div className="rounded-[10px] border border-slate-900/10 bg-white p-4">
      <p className="text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">{label}</p>
      <p className={`mt-2 inline-flex rounded-[8px] px-3 py-2 text-[24px] font-extrabold tracking-[-.02em] ${tones[tone]}`}>
        {value}
      </p>
    </div>
  );
}

function ReportCard({ title, subtitle, children }: { title: string; subtitle: string; children: ReactNode }) {
  return (
    <section className="rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-sm">
      <div className="mb-4 flex items-start justify-between gap-4">
        <div>
          <h3 className="text-[20px] font-extrabold tracking-[-.02em]">{title}</h3>
          <p className="text-[12px] font-medium text-slate-500">{subtitle}</p>
        </div>
        <span className="rounded-full bg-[#7C3AED]/10 px-3 py-2 text-[11px] font-bold text-[#7C3AED]">собрано автоматически</span>
      </div>
      <div className="space-y-2">{children}</div>
    </section>
  );
}

function TaskRow({ task }: { task: ParsedTask }) {
  const colors = {
    done: "bg-[#84CC16]/15 text-[#3F6212]",
    progress: "bg-[rgba(14,165,233,0.08)] text-[#0369A1]",
    planned: "bg-[#7C3AED]/10 text-[#7C3AED]",
    backlog: "bg-[#F97316]/10 text-[#C2410C]",
  };

  const labels = {
    done: "готово",
    progress: "в работе",
    planned: "в план",
    backlog: "бэклог",
  };

  return (
    <div className="rounded-[10px] border border-slate-900/10 bg-slate-50 p-4 transition hover:-translate-y-0.5 hover:bg-white hover:shadow-md">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-[13px] font-bold">{task.title}</p>
        <span className={`rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-[.7px] ${colors[task.status]}`}>
          {labels[task.status]}
        </span>
      </div>
      <div className="mt-2 flex flex-wrap gap-2 text-[11px] font-medium text-slate-500">
        {task.date ? <span>{task.date}</span> : null}
        <span>{task.estimate}ч</span>
      </div>
    </div>
  );
}

function Divider({ label }: { label: string }) {
  return <p className="pt-3 text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">{label}</p>;
}

function Empty({ text }: { text: string }) {
  return <div className="rounded-[10px] border border-dashed border-slate-900/10 p-4 text-[13px] text-slate-400">{text}</div>;
}
