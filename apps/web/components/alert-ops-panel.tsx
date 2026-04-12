"use client";

import { useState, useTransition } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function summarizeJobResult(path: string, payload: Record<string, unknown> | null) {
  if (!payload) {
    return "Job ejecutado.";
  }

  if (path.includes("enrich-pending")) {
    const enriched =
      typeof payload.enriched_count === "number"
        ? payload.enriched_count
        : typeof payload.processed === "number"
          ? payload.processed
          : 0;
    return `Enrichment ejecutado. Pendientes enriquecidos: ${enriched}.`;
  }

  if (path.includes("alerts/generate")) {
    const generated =
      typeof payload.generated_count === "number"
        ? payload.generated_count
        : typeof payload.created === "number"
          ? payload.created
          : typeof payload.alerts_generated === "number"
            ? payload.alerts_generated
            : 0;
    return `Generación ejecutada. Alertas creadas: ${generated}.`;
  }

  if (path.includes("alerts/dispatch")) {
    const dispatched =
      typeof payload.dispatched_count === "number"
        ? payload.dispatched_count
        : typeof payload.sent === "number"
          ? payload.sent
          : typeof payload.processed === "number"
            ? payload.processed
            : 0;
    return `Dispatch ejecutado. Entregas procesadas: ${dispatched}.`;
  }

  return "Job ejecutado.";
}

export function AlertOpsPanel() {
  const [message, setMessage] = useState("");
  const [lastResult, setLastResult] = useState<Record<string, unknown> | null>(null);
  const [isPending, startTransition] = useTransition();

  function runJob(path: string) {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}${path}`, {
        method: "POST",
        credentials: "include",
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(payload?.detail ?? "No se pudo ejecutar el job.");
        setLastResult(null);
        return;
      }
      setLastResult(payload && typeof payload === "object" ? (payload as Record<string, unknown>) : null);
      setMessage(summarizeJobResult(path, payload && typeof payload === "object" ? (payload as Record<string, unknown>) : null));
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

      <div className="detail-note-card">
        <span className="section-kicker">Orden recomendado</span>
        <p>Corré enrichment cuando entró contenido nuevo. Después generá alertas. Dispatch va último, cuando el contenido ya está listo para salir.</p>
      </div>

      <div className="hero-actions">
        <button
          type="button"
          onClick={() => runJob("/api/v1/jobs/enrich-pending")}
          disabled={isPending}
          className="button-secondary"
        >
          Enriquecer pendientes
        </button>
        <button
          type="button"
          onClick={() => runJob("/api/v1/jobs/alerts/generate")}
          disabled={isPending}
          className="button-primary"
        >
          Generar alerts
        </button>
        <button
          type="button"
          onClick={() => runJob("/api/v1/jobs/alerts/dispatch")}
          disabled={isPending}
          className="button-secondary"
        >
          Despachar WhatsApp
        </button>
      </div>

      {lastResult ? (
        <div className="job-run-summary">
          <span className="section-kicker">Último resultado</span>
          <pre>{JSON.stringify(lastResult, null, 2)}</pre>
        </div>
      ) : null}

      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
