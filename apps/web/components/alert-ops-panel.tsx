"use client";

import { useState, useTransition } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export function AlertOpsPanel() {
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function runJob(path: string, successLabel: string) {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(payload?.detail ?? "No se pudo ejecutar el job.");
        return;
      }
      setMessage(`${successLabel}: ${JSON.stringify(payload)}`);
    });
  }

  return (
    <div className="source-form">
      <div className="results-header">
        <div>
          <span className="section-kicker">Alerting</span>
          <h2>Generar y despachar</h2>
        </div>
        <p>Primero genera alerts por usuario y después despacha los pendientes de WhatsApp.</p>
      </div>

      <div className="hero-actions">
        <button
          type="button"
          onClick={() => runJob("/api/v1/jobs/enrich-pending", "Enrichment ejecutado")}
          disabled={isPending}
          className="button-secondary"
        >
          Enriquecer pendientes
        </button>
        <button
          type="button"
          onClick={() => runJob("/api/v1/jobs/alerts/generate", "Generación ejecutada")}
          disabled={isPending}
          className="button-primary"
        >
          Generar alerts
        </button>
        <button
          type="button"
          onClick={() => runJob("/api/v1/jobs/alerts/dispatch", "Dispatch ejecutado")}
          disabled={isPending}
          className="button-secondary"
        >
          Despachar WhatsApp
        </button>
      </div>

      {message ? <p className="form-message form-message-block">{message}</p> : null}
    </div>
  );
}
