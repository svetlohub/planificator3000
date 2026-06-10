/* global window */
"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

const NAME_KEY = "planner3000:name";
const ROUTINE_KEY = "planner3000:routines";
const SHEET_KEY = "planner3000:sheetUrl";

export default function SettingsPage() {
  const [name, setName] = useState("");
  const [sheetUrl, setSheetUrl] = useState("");
  const [routines, setRoutines] = useState("");

  useEffect(() => {
    setName(window.localStorage.getItem(NAME_KEY) || "Паша");
    setSheetUrl(window.localStorage.getItem(SHEET_KEY) || "");
    setRoutines(window.localStorage.getItem(ROUTINE_KEY) || "");
  }, []);

  function save() {
    window.localStorage.setItem(NAME_KEY, name);
    window.localStorage.setItem(SHEET_KEY, sheetUrl);
    window.localStorage.setItem(ROUTINE_KEY, routines);
  }

  return (
    <main className="min-h-screen bg-[#F1F5F9] text-[#0F172A]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_20%_10%,rgba(124,58,237,.14),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(132,204,22,.18),transparent_24%)]" />

      <section className="relative mx-auto max-w-3xl px-5 py-5">
        <header className="mb-5 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="grid size-11 place-items-center rounded-[14px] bg-[#F97316] text-[24px] font-black text-[#B6FF2E] shadow-[0_10px_30px_rgba(249,115,22,.28)]">
              П
            </div>
            <div>
              <div className="text-[19px] font-black tracking-[-.02em]">ПЛАНИФИКАТОР-3000</div>
              <div className="text-[12px] font-medium text-slate-500">Настройки</div>
            </div>
          </Link>

          <Link
            href="/"
            className="rounded-[10px] border border-slate-900/10 bg-white px-4 py-2 text-[13px] font-bold shadow-sm transition hover:-translate-y-0.5 hover:shadow-[0_12px_35px_rgba(15,23,42,.1)]"
          >
            Назад
          </Link>
        </header>

        <div className="space-y-4">
          <section className="rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-[0_18px_80px_rgba(15,23,42,.08)]">
            <h1 className="text-[24px] font-black tracking-[-.02em]">Основные настройки</h1>
            <p className="mt-1 text-[13px] leading-6 text-slate-500">
              Эти данные сохраняются в браузере. Ничего не отправляется на сервер без вашего действия.
            </p>

            <label className="mt-4 block">
              <span className="mb-1 block text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Ваше имя</span>
              <input
                value={name}
                onChange={(event) => setName(event.target.value)}
                className="w-full rounded-[10px] border border-slate-900/10 bg-slate-50 px-3 py-3 text-[13px] font-semibold outline-none transition focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
              />
            </label>

            <label className="mt-4 block">
              <span className="mb-1 block text-[10px] font-bold uppercase tracking-[.7px] text-slate-400">Google Sheets</span>
              <input
                value={sheetUrl}
                onChange={(event) => setSheetUrl(event.target.value)}
                placeholder="Ссылка на таблицу"
                className="w-full rounded-[10px] border border-slate-900/10 bg-slate-50 px-3 py-3 text-[13px] font-semibold outline-none transition focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
              />
              <p className="mt-2 text-[12px] leading-5 text-slate-500">
                Следующий backend-шаг: брать задачи из столбика A, смотреть дату добавления и включать задачи в отчёт недели.
              </p>
            </label>
          </section>

          <section className="rounded-[14px] border border-slate-900/10 bg-white p-5 shadow-[0_18px_80px_rgba(15,23,42,.08)]">
            <h2 className="text-[20px] font-black tracking-[-.02em]">Рутинные задачи</h2>
            <p className="mt-1 text-[13px] leading-6 text-slate-500">
              Каждая строка — одна постоянная задача. Они автоматически добавляются в план на следующую неделю.
            </p>

            <textarea
              value={routines}
              onChange={(event) => setRoutines(event.target.value)}
              placeholder={"Пост в социальных сетях\nРабота с Пиаром\nПоиск упоминаний\nРабота над Google Ads"}
              className="mt-4 min-h-[220px] w-full resize-none rounded-[14px] border border-slate-900/10 bg-slate-50 p-4 text-[13px] leading-6 outline-none transition focus:border-[#7C3AED] focus:bg-white focus:ring-4 focus:ring-[#7C3AED]/10"
            />

            <button
              onClick={save}
              className="mt-4 rounded-[10px] bg-[#7C3AED] px-5 py-3 text-[13px] font-bold text-white shadow-[0_10px_30px_rgba(124,58,237,.22)] transition hover:-translate-y-0.5 hover:shadow-[0_18px_55px_rgba(124,58,237,.34)]"
            >
              Сохранить настройки
            </button>
          </section>
        </div>
      </section>
    </main>
  );
}
