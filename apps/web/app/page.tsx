/* global process, fetch */
"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { AlertTriangle, CheckCircle2, RefreshCw } from "lucide-react";

import { APP_NAME } from "@planner3000/shared";
import { Button } from "@planner3000/ui";

type ApiHealth = {
  status: string;
  service: string;
  environment?: string;
  sheets_configured?: boolean;
  sheets_healthy?: boolean | null;
};

type Smoke = {
  status: string;
  service: string;
  timestamp: string;
  endpoints: Record<string, string>;
};

const apiBaseUrl = (process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000").replace(/\/$/, "");

const workload = [
  { name: "Paulo", role: "Marketing", load: 92, hours: "36h" },
  { name: "Ana", role: "Content", load: 74, hours: "29h" },
  { name: "Lucas", role: "Performance", load: 108, hours: "43h" },
  { name: "Marina", role: "PR", load: 61, hours: "24h" },
];

const planned = [
  "Internet Marketing Report",
  "Social Media Release Announcement",
  "Monthly Report May 2026",
  "Google Ads Operations",
  "Release West Launch",
];

const backlog = ["Partnership landing update", "Customer story refresh", "Q3 planning memo"];

export default function HomePage() {
  const [health, setHealth] = useState<ApiHealth | null>(null);
  const [smoke, setSmoke] = useState<Smoke | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function refreshStatus() {
    setError(null);

    try {
      const [healthResponse, smokeResponse] = await Promise.all([
        fetch(`${apiBaseUrl}/api/health`, { cache: "no-store" }),
        fetch(`${apiBaseUrl}/api/smoke`, { cache: "no-store" }),
      ]);

      if (!healthResponse.ok) {
        throw new Error(`Health failed: HTTP ${healthResponse.status}`);
      }

      if (!smokeResponse.ok) {
        throw new Error(`Smoke failed: HTTP ${smokeResponse.status}`);
      }

      setHealth((await healthResponse.json()) as ApiHealth);
      setSmoke((await smokeResponse.json()) as Smoke);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unknown API connection error");
    }
  }

  useEffect(() => {
    void refreshStatus();
  }, []);

  return (
    <main className="relative min-h-screen overflow-hidden px-5 py-5 md:px-8">
      <div className="pointer-events-none absolute left-0 top-0 h-96 w-96 rounded-full bg-lime-300/40 blur-3xl" />
      <div className="pointer-events-none absolute right-0 top-20 h-96 w-96 rounded-full bg-orange-300/35 blur-3xl" />

      <section className="relative mx-auto max-w-7xl">
        <nav className="mb-6 flex items-center justify-between rounded-full border border-white/70 bg-white/70 px-5 py-4 shadow-xl backdrop-blur-2xl">
          <div>
            <div className="text-lg font-black tracking-tight">{APP_NAME}</div>
            <div className="text-xs font-bold text-neutral-500">Production Demo Console</div>
          </div>

          <Button onClick={() => void refreshStatus()} variant="outline">
            <RefreshCw className="mr-2 size-4" />
            Refresh API
          </Button>
        </nav>

        <div className="grid gap-6 lg:grid-cols-[1.08fr_0.92fr]">
          <motion.section
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.55, ease: "easeOut" }}
            className="rounded-[3rem] border border-white/70 bg-white/70 p-8 shadow-2xl backdrop-blur-2xl md:p-12"
          >
            <div className="mb-8 inline-flex rounded-full border border-black/10 bg-white/75 px-4 py-2 text-sm font-black text-neutral-700">
              Railway-ready MVP · FastAPI · Google Sheets · Next.js
            </div>

            <h1 className="max-w-4xl text-5xl font-black tracking-[-0.06em] md:text-7xl">
              Weekly planning without chaos.
            </h1>

            <p className="mt-6 max-w-2xl text-lg leading-8 text-neutral-600">
              Production dashboard для демонстрации MVP: загрузка команды, capacity,
              backlog, API health и smoke checks в одном красивом интерфейсе.
            </p>

            <div className="mt-8 flex flex-wrap gap-3">
              <a
                href={`${apiBaseUrl}/api/health`}
                target="_blank"
                className="rounded-full bg-black px-6 py-4 text-sm font-black text-white shadow-xl"
              >
                Проверить /api/health
              </a>
              <a
                href={`${apiBaseUrl}/api/smoke`}
                target="_blank"
                className="rounded-full border border-black/10 bg-white/80 px-6 py-4 text-sm font-black text-black shadow-xl"
              >
                Smoke test
              </a>
            </div>

            {error ? (
              <div className="mt-8 rounded-3xl border border-orange-200 bg-orange-100 p-5 font-bold text-orange-950">
                API warning: {error}. Проверь NEXT_PUBLIC_API_URL и CORS_ORIGINS.
              </div>
            ) : null}

            <div className="mt-10 grid gap-4 md:grid-cols-3">
              <div className="rounded-[2rem] bg-lime-200 p-6 shadow-lg">
                <p className="text-sm font-black text-neutral-600">API status</p>
                <p className="mt-3 flex items-center gap-2 text-4xl font-black">
                  {health?.status === "ok" ? <CheckCircle2 className="size-8" /> : null}
                  {health?.status ?? "..."}
                </p>
              </div>

              <div className="rounded-[2rem] bg-orange-200 p-6 shadow-lg">
                <p className="text-sm font-black text-neutral-600">Smoke test</p>
                <p className="mt-3 text-4xl font-black">{smoke?.status ?? "..."}</p>
              </div>

              <div className="rounded-[2rem] bg-white/85 p-6 shadow-lg">
                <p className="text-sm font-black text-neutral-600">Sheets</p>
                <p className="mt-3 text-4xl font-black">
                  {health?.sheets_configured === undefined
                    ? "..."
                    : health.sheets_configured
                      ? "ON"
                      : "OFF"}
                </p>
              </div>
            </div>
          </motion.section>

          <motion.section
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.08, duration: 0.55, ease: "easeOut" }}
            className="rounded-[3rem] border border-white/70 bg-white/70 p-7 shadow-2xl backdrop-blur-2xl"
          >
            <div className="mb-6 flex items-center justify-between">
              <div>
                <p className="text-sm font-black uppercase tracking-[0.2em] text-neutral-500">
                  Mission Control
                </p>
                <h2 className="mt-2 text-3xl font-black tracking-tight">Team workload</h2>
              </div>
              <span className="rounded-full bg-black px-4 py-2 text-xs font-black text-white">
                LIVE
              </span>
            </div>

            <div className="grid gap-4">
              {workload.map((person) => (
                <div key={person.name} className="rounded-3xl border border-black/10 bg-white/70 p-5">
                  <div className="mb-3 flex items-center justify-between">
                    <div>
                      <p className="font-black">{person.name}</p>
                      <p className="text-sm font-bold text-neutral-500">{person.role}</p>
                    </div>
                    <span
                      className={
                        person.load > 100
                          ? "rounded-full bg-orange-200 px-3 py-1 text-sm font-black text-orange-950"
                          : "rounded-full bg-lime-200 px-3 py-1 text-sm font-black text-lime-950"
                      }
                    >
                      {person.load}%
                    </span>
                  </div>

                  <div className="h-3 overflow-hidden rounded-full bg-black/10">
                    <div
                      className={
                        person.load > 100
                          ? "h-full rounded-full bg-orange-400"
                          : "h-full rounded-full bg-lime-400"
                      }
                      style={{ width: `${Math.min(person.load, 120)}%` }}
                    />
                  </div>

                  <p className="mt-2 text-xs font-bold text-neutral-500">
                    {person.hours} allocated this week
                  </p>
                </div>
              ))}
            </div>
          </motion.section>
        </div>

        <div className="mt-6 grid gap-6 lg:grid-cols-[1fr_0.8fr]">
          <section className="rounded-[3rem] border border-white/70 bg-white/70 p-7 shadow-2xl backdrop-blur-2xl">
            <p className="text-sm font-black uppercase tracking-[0.2em] text-neutral-500">
              New Week Plan
            </p>
            <h2 className="mt-2 text-3xl font-black">Planned work</h2>

            <div className="mt-6 grid gap-3">
              {planned.map((task, index) => (
                <div
                  key={task}
                  className="flex items-center gap-4 rounded-3xl border border-black/10 bg-white/75 p-4 font-black"
                >
                  <span className="flex size-8 items-center justify-center rounded-full bg-lime-200 text-sm">
                    {index + 1}
                  </span>
                  {task}
                </div>
              ))}
            </div>
          </section>

          <section className="rounded-[3rem] border border-white/70 bg-white/70 p-7 shadow-2xl backdrop-blur-2xl">
            <p className="text-sm font-black uppercase tracking-[0.2em] text-neutral-500">
              Deferred
            </p>
            <h2 className="mt-2 flex items-center gap-2 text-3xl font-black">
              <AlertTriangle className="size-7 text-orange-500" />
              Backlog
            </h2>

            <div className="mt-6 grid gap-3">
              {backlog.map((task) => (
                <div key={task} className="rounded-3xl bg-orange-100 p-4 font-black text-orange-950">
                  {task}
                </div>
              ))}
            </div>
          </section>
        </div>
      </section>
    </main>
  );
}
