"use client";

import { useEffect, useRef, useState, type ReactNode } from "react";
import { api } from "@/lib/api";
import { GlobalLoading } from "@/components/global-loading";

type BackendStatus = "checking" | "ready";

export function BackendGate({ children }: { children: ReactNode }) {
  const [status, setStatus] = useState<BackendStatus>("checking");
  const retryTimeout = useRef<ReturnType<typeof setTimeout> | null>(null);

  useEffect(() => {
    let cancelled = false;
    let attempt = 0;

    const checkHealth = async () => {
      attempt += 1;
      try {
        const result = await api.healthCheck();
        if (cancelled) return;
        setStatus("ready");
      } catch (error) {
        if (cancelled) return;

        const delayMs = Math.min(2000 + attempt * 1000, 10000);
        retryTimeout.current = setTimeout(checkHealth, delayMs);
      }
    };

    checkHealth();

    return () => {
      cancelled = true;
      if (retryTimeout.current) {
        clearTimeout(retryTimeout.current);
      }
    };
  }, []);

  if (status !== "ready") {
    return <GlobalLoading message="Loading" />;
  }

  return <>{children}</>;
}
