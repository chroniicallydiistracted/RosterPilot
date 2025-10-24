import "../styles/globals.css";
import type { Metadata } from "next";
import { ReactNode } from "react";

import { AppShell } from "@/components/layout/AppShell";
import { AppProviders } from "@/components/providers/AppProviders";
import { fetchRuntimeConfig } from "@/lib/api-client";
import { readPublicEnv } from "@/lib/env";

export const metadata: Metadata = {
  title: "RosterPilot",
  description: "Yahoo Fantasy Football companion powered by PyESPN data"
};

export default async function RootLayout({ children }: { children: ReactNode }) {
  const env = readPublicEnv();
  const runtimeConfig = await fetchRuntimeConfig(env);

  return (
    <html lang="en">
      <body>
        <AppProviders env={env} runtimeConfig={runtimeConfig}>
          <AppShell>{children}</AppShell>
        </AppProviders>
      </body>
    </html>
  );
}
