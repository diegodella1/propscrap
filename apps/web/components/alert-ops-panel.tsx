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
        credentials: "include",
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
          <span className="section-kicker">Jobs</span>
          <h2>Enriquecer, generar y despachar</h2>
        </div>
        <p>El orden recomendado es simple: enrichment, generación de alertas y después dispatch.</p>
      </div>

      <div className="admin-job-stack">
        <article className="admin-job-card">
          <strong>1. Enrichment</strong>
          <p>Completa resumen, requisitos y señales antes de alertar.</p>
        </article>
        <article className="admin-job-card">
          <strong>2. Generación</strong>
          <p>Construye alertas por usuario según perfil y preferencias.</p>
        </article>
        <article className="admin-job-card">
          <strong>3. Dispatch</strong>
          <p>Envía lo pendiente al canal configurado.</p>
        </article>
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

      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
