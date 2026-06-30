"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { GlobalLoading } from "@/components/global-loading";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api/v1";

const HEALTH_URL = API_BASE_URL.replace("/api/v1", "") + "/health";

/** Timeout (ms) for a single health-check fetch attempt. */
const FETCH_TIMEOUT_MS = 12_000;

/** Maximum ms between retry attempts. */
const MAX_RETRY_DELAY_MS = 10_000;

type BackendStatus = "checking" | "ready";

async function pingHealth(): Promise<void> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), FETCH_TIMEOUT_MS);
  try {
    const res = await fetch(HEALTH_URL, { signal: controller.signal });
    if (!res.ok) throw new Error(`Health check returned ${res.status}`);
  } finally {
    clearTimeout(timer);
  }
}

export function BackendGate({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const [elapsedSeconds, setElapsedSeconds] = useState(0);
  const retryTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);
  const tickInterval = useRef<ReturnType<typeof setInterval> | null>(null);

  useEffect(() => {
    let cancelled = false;
    let attempt = 0;

    // Tick up elapsed seconds while checking
    tickInterval.current = setInterval(() => {
      setElapsedSeconds((s) => s + 1);
    }, 1000);

    const checkHealth = async () => {
      attempt += 1;
      try {
        await pingHealth();
        if (cancelled) return;
        if (tickInterval.current) clearInterval(tickInterval.current);
        setStatus("ready");
      } catch {
        if (cancelled) return;
        const delayMs = Math.min(2000 + attempt * 1000, MAX_RETRY_DELAY_MS);
        retryTimeout.current = setTimeout(checkHealth, delayMs);
      }
    };

    checkHealth();

    return () => {
      cancelled = true;
      if (retryTimeout.current) clearTimeout(retryTimeout.current);
      if (tickInterval.current) clearInterval(tickInterval.current);
    };
  }, []);

  if (status !== "ready") {
    const message =
      elapsedSeconds < 5
        ? "Connecting to backend"
        : elapsedSeconds < 20
        ? `Waking up backend server (${elapsedSeconds}s)`
        : `Still waking up\u2026 this can take ~30s on first load (${elapsedSeconds}s)`;

    return <GlobalLoading message={message} />;
  }

  return <>{children}</>;
}
