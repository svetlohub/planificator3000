"use client";

import { motion } from "framer-motion";
import { CalendarCheck2, Network, Rocket } from "lucide-react";

import { APP_NAME } from "@planner3000/shared";
import { Button } from "@planner3000/ui";

const features = [
  {
    title: "Стратегия без хаоса",
    description: "Собирайте цели, ограничения и ресурсы в единую карту решений.",
    icon: Network,
  },
  {
    title: "Планы, готовые к запуску",
    description: "Превращайте инициативы в дорожные карты с понятными владельцами.",
    icon: CalendarCheck2,
  },
  {
    title: "Скорость исполнения",
    description: "Отслеживайте прогресс и быстро перестраивайте план под реальность.",
    icon: Rocket,
  },
] as const;

export default function HomePage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-6xl flex-col px-6 py-10">
      <header className="flex items-center justify-between">
        <div className="text-lg font-black tracking-tight">{APP_NAME}</div>
        <Button variant="ghost">Документация</Button>
      </header>

      <section className="grid flex-1 items-center gap-12 py-20 lg:grid-cols-[1.15fr_0.85fr]">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ duration: 0.55, ease: "easeOut" }}
          className="space-y-8"
        >
          <div className="inline-flex rounded-full border bg-card/70 px-4 py-2 text-sm text-muted-foreground shadow-sm backdrop-blur">
            Production-ready foundation · Next.js 15 · FastAPI
          </div>
          <div className="space-y-5">
            <h1 className="max-w-3xl text-5xl font-black tracking-tight md:text-7xl">
              Планируй невозможное. Исполняй системно.
            </h1>
            <p className="max-w-2xl text-lg leading-8 text-muted-foreground">
              {APP_NAME} — монорепозиторий для современного продукта: строгий TypeScript,
              типизированный Python API, единые пакеты UI и shared-контрактов.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Button size="lg">Начать планирование</Button>
            <Button size="lg" variant="outline">
              Проверить API
            </Button>
          </div>
        </motion.div>

        <motion.div
          initial={{ opacity: 0, scale: 0.96 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ delay: 0.15, duration: 0.55, ease: "easeOut" }}
          className="rounded-3xl border bg-card/85 p-4 shadow-2xl backdrop-blur"
        >
          <div className="rounded-2xl bg-foreground p-6 text-primary-foreground">
            <div className="mb-6 flex items-center justify-between">
              <span className="text-sm opacity-70">Mission Control</span>
              <span className="rounded-full bg-primary px-3 py-1 text-xs">LIVE</span>
            </div>
            <div className="space-y-4">
              {features.map((feature) => (
                <div key={feature.title} className="rounded-2xl bg-white/10 p-4">
                  <feature.icon className="mb-3 size-5 text-primary" />
                  <h2 className="font-bold">{feature.title}</h2>
                  <p className="mt-1 text-sm leading-6 opacity-70">{feature.description}</p>
                </div>
              ))}
            </div>
          </div>
        </motion.div>
      </section>
    </main>
  );
}
