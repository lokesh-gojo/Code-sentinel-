"use client";

import React, { useEffect, useState } from "react";
import { api } from "@/lib/api";
import { AlertCircle, CheckCircle2, RefreshCw } from "lucide-react";

export const WakeUpBanner: React.FC = () => {
  const [status, setStatus] = useState<"checking" | "online" | "waking">("checking");

  useEffect(() => {
    let isMounted = true;
    api
      .checkHealth()
      .then(() => {
        if (isMounted) setStatus("online");
      })
      .catch(() => {
        if (isMounted) setStatus("waking");
      });
    return () => {
      isMounted = false;
    };
  }, []);

  if (status === "online") return null;

  return (
    <div className="bg-amber-500/10 border-b border-amber-500/20 px-4 py-2.5 text-xs text-amber-300 flex items-center justify-between">
      <div className="flex items-center gap-2">
        {status === "checking" ? (
          <RefreshCw className="w-3.5 h-3.5 animate-spin text-amber-400" />
        ) : (
          <AlertCircle className="w-3.5 h-3.5 text-amber-400" />
        )}
        <span>
          {status === "checking"
            ? "Connecting to FastAPI backend..."
            : "Backend container is spinning up (free-tier cold start). Initial scans may take 15–30s."}
        </span>
      </div>
    </div>
  );
};
