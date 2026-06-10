"use client";

import type { ReactNode } from "react";
import { useMemo, useState } from "react";

type ParsedTask = {
  title: string;
  date?: string;
  owner?: string;
  status: "done" | "progress" | "planned" | "backlog";
  estimate: number;
};

const demoText = `Completed Tasks
- 2026-06-03 Paulo - Internet Marketing Report - done - 4h
- 2026-06-04 Ana - Social Media Release Announcement - done - 3h
- 2026-06-06 Lucas - Google Ads Operations - progress - 6h

New Week
- 2026-06-10 Paulo - Monthly Report June 2026 - planned - 5h
- 2026-06-11 Marina - PR outreach list - planned - 4h
- 2026-06-12 Ana - Social Media Report - planned - 3h
- 2026-06-13 Lucas - Campaign optimization - planned - 6h

Backlog
- Partnership landing update
- Customer story refresh`;

function parseTasks(raw: string): ParsedTask[] {
  return raw
    .split("\n")
    .map((line) => line.trim())
    .filter((line) => line.startsWith("-") || line.startsWith("*"))
    .map((line) => {
      const clean = line.replace(/^[-*]\s*/, "");
      const estimateMatch = clean.match(/(\d+(?:\.\d+)?)\s*h/i);
      const dateMatch = clean.match(/\d{4}-\d{2}-\d{2}/);
      const lower = clean.toLowerCase();

      const status =
        lower.includes("done") || lower.includes("completed")
          ? "done"
          : lower.includes("progress") || lower.includes("doing")
            ? "progress"
            : lower.includes("backlog") || lower.includes("deferred")
              ? "backlog"
              : "planned";

      const parts = clean.split(" - ").map((part) => part.trim());

      return {
        title: parts.at(-2)?.match(/\d+h/i) ? parts.at(-3) || clean : parts.at(-2) || parts.at(-1) || clean,
        date: dateMatch?.[0],
        owner: parts.length >= 3 ? parts[1] : undefined,
        status,
        estimate: estimateMatch ? Number(estimateMatch[1]) : 2,
      };
    });
}

function groupByStatus(tasks: ParsedTask[], status: ParsedTask["status"]) {
  return tasks.filter((task) => task.status === status);
}

export default function HomePage() {
  const [raw, setRaw] = useState(demoText);

  const tasks = useMemo(() => parseTasks(raw), [raw]);
  const done = groupByStatus(tasks, "done");
  const progress = groupByStatus(tasks, "progress");
  const planned = groupByStatus(tasks, "planned");
  const backlog = groupByStatus(tasks, "backlog");

  const plannedHours = planned.reduce((sum, task) => sum + task.estimate, 0);
  const completedHours = done.reduce((sum, task) => sum + task.estimate, 0);

  return (
    <main className="min-h-screen bg-[#F1F5F9] text-[#0F172A]">
      <section className="mx-auto max-w-7xl px-5 py-6">
        <header className="mb-6 flex flex-col gap-4 rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-sm md:flex-row md:items-center md:justify-between">
          <div>
            <div className="flex items-center gap-3">
              <div className="grid size-10 place-items-center rounded-[10px] bg-[#84CC16] font-black text-white">
                P
              </div>
              <div>
                <p className="font-syne text-[19px] font-extrabold tracking-[-.02em]">PLANIFICATOR-3000</p>
                <p className="text-xs font-medium text-slate-500">Weekly planning assistant</p>
              </div>
            </div>
          </div>

          <div className="flex flex-wrap gap-2 text-[11px] font-bold">
            <span className="rounded-full bg-[#7C3AED]/10 px-3 py-2 text-[#7C3AED]">Care: structured plan</span>
            <span className="rounded-full bg-[#84CC16]/15 px-3 py-2 text-[#3F6212]">Energy: execution</span>
            <span className="rounded-full bg-[#F97316]/10 px-3 py-2 text-[#C2410C]">Optimism: next week</span>
          </div>
        </header>

        <div className="grid gap-5 lg:grid-cols-[0.9fr_1.1fr]">
          <section className="rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-sm">
            <div className="mb-4">
              <p className="text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Step 1</p>
              <h1 className="font-syne text-[34px] font-extrabold tracking-[-.02em]">Paste raw work data</h1>
              <p className="mt-2 text-[13px] leading-6 text-slate-500">
                Вставь задачи в любом простом виде: строки, даты, имена, статусы, часы. Планировщик распознает всё локально.
              </p>
            </div>

            <textarea
              value={raw}
              onChange={(event) => setRaw(event.target.value)}
              className="min-h-[520px] w-full resize-none rounded-[10px] border border-slate-900/10 bg-slate-50 p-4 font-mono text-[12px] leading-6 outline-none transition focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
            />

            <div className="mt-4 flex gap-3">
              <button
                onClick={() => setRaw(demoText)}
                className="rounded-[10px] bg-[#F97316] px-4 py-3 text-[13px] font-bold text-white shadow-sm transition hover:-translate-y-0.5 hover:shadow-lg"
              >
                Load demo
              </button>
              <button
                onClick={() => setRaw("")}
                className="rounded-[10px] border border-slate-900/10 bg-white px-4 py-3 text-[13px] font-bold transition hover:-translate-y-0.5"
              >
                Clear
              </button>
            </div>
          </section>

          <section className="space-y-5">
            <div className="rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-sm">
              <p className="text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Step 2</p>
              <h2 className="font-syne text-[34px] font-extrabold tracking-[-.02em]">Weekly report</h2>

              <div className="mt-5 grid gap-3 md:grid-cols-4">
                <Metric label="Tasks parsed" value={tasks.length} tone="violet" />
                <Metric label="Completed" value={done.length} tone="lime" />
                <Metric label="Planned hours" value={`${plannedHours}h`} tone="orange" />
                <Metric label="Backlog" value={backlog.length} tone="red" />
              </div>
            </div>

            <ReportCard title="Previous Week" subtitle={`${done.length} completed · ${completedHours}h delivered`}>
              {done.length ? done.map((task) => <TaskRow key={task.title} task={task} />) : <Empty text="No completed tasks detected." />}
              {progress.length ? (
                <>
                  <Divider label="In progress" />
                  {progress.map((task) => <TaskRow key={task.title} task={task} />)}
                </>
              ) : null}
            </ReportCard>

            <ReportCard title="New Week Plan" subtitle={`${planned.length} planned · ${plannedHours}h estimated`}>
              {planned.length ? planned.map((task) => <TaskRow key={task.title} task={task} />) : <Empty text="No planned tasks detected." />}
            </ReportCard>

            <ReportCard title="Backlog" subtitle={`${backlog.length} deferred tasks`}>
              {backlog.length ? backlog.map((task) => <TaskRow key={task.title} task={task} />) : <Empty text="No backlog detected." />}
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
      <p className={`mt-2 inline-flex rounded-[8px] px-3 py-2 font-syne text-[24px] font-extrabold tracking-[-.02em] ${tones[tone]}`}>
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
          <h3 className="font-syne text-[20px] font-extrabold tracking-[-.02em]">{title}</h3>
          <p className="text-[12px] font-medium text-slate-500">{subtitle}</p>
        </div>
        <span className="rounded-full bg-[#7C3AED]/10 px-3 py-2 text-[11px] font-bold text-[#7C3AED]">auto-generated</span>
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

  return (
    <div className="rounded-[10px] border border-slate-900/10 bg-slate-50 p-4 transition hover:-translate-y-0.5 hover:bg-white hover:shadow-md">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <p className="text-[13px] font-bold">{task.title}</p>
        <span className={`rounded-full px-3 py-1 text-[10px] font-bold uppercase tracking-[.7px] ${colors[task.status]}`}>
          {task.status}
        </span>
      </div>
      <div className="mt-2 flex flex-wrap gap-2 text-[11px] font-medium text-slate-500">
        {task.date ? <span>{task.date}</span> : null}
        {task.owner ? <span>Owner: {task.owner}</span> : null}
        <span>{task.estimate}h</span>
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
