import type { Metadata } from "next";
import type { ReactNode } from "react";

import { APP_NAME } from "@planner3000/shared";

import "./globals.css";

export const metadata: Metadata = {
  title: APP_NAME,
  description: "AI-ready planning workspace for teams that execute.",
};

export default function RootLayout({ children }: Readonly<{ children: ReactNode }>) {
  return (
    <html lang="ru">
      <body>{children}</body>
    </html>
  );
}
