"use client";

import { useState, useTransition } from "react";

import type { AutomationSettings } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

type Props = {
  settings: AutomationSettings;
};

export function AutomationSettingsPanel({ settings }: Props) {
  const [isEnabled, setIsEnabled] = useState(settings.is_enabled);
  const [intervalHours, setIntervalHours] = useState(String(settings.ingestion_interval_hours));
  const [openaiApiKey, setOpenaiApiKey] = useState("");
  const [openaiModel, setOpenaiModel] = useState(settings.openai_model ?? "gpt-4.1-mini");
  const [masterPrompt, setMasterPrompt] = useState(settings.llm_master_prompt ?? "");
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function saveSettings() {
    startTransition(async () => {
      setMessage("");
      const parsedInterval = Number(intervalHours);
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/automation`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          is_enabled: isEnabled,
          ingestion_interval_hours: parsedInterval,
          openai_api_key: openaiApiKey || undefined,
          openai_model: openaiModel,
          llm_master_prompt: masterPrompt,
        }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(payload?.detail ?? "No se pudo guardar la automatización.");
        return;
      }
      setIntervalHours(String(payload.ingestion_interval_hours));
      setIsEnabled(payload.is_enabled);
      setOpenaiApiKey("");
      setOpenaiModel(payload.openai_model ?? "gpt-4.1-mini");
      setMasterPrompt(payload.llm_master_prompt ?? "");
      setMessage("Automatización guardada.");
    });
  }

  function runNow() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/automation/run`, {
        method: "POST",
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(payload?.detail ?? "No se pudo ejecutar el ciclo.");
        return;
      }
      const sourcesIngested = payload?.ingestion_results?.length ?? payload?.sources_ingested ?? 0;
      setMessage(`Ciclo ejecutado. Fuentes corridas: ${sourcesIngested}.`);
    });
  }

  return (
    <div className="source-form">
      <div className="results-header">
        <div>
          <span className="section-kicker">Automatización</span>
          <h2>Ingesta automática</h2>
        </div>
        <p>Por defecto corre cada 1 hora. Desde acá podés dejarla activa o cambiar cada cuántas horas se vuelve a ejecutar.</p>
      </div>

      <label className="form-field">
        <span>Estado</span>
        <select value={isEnabled ? "on" : "off"} onChange={(event) => setIsEnabled(event.target.value === "on")}>
          <option value="on">Activa</option>
          <option value="off">Pausada</option>
        </select>
      </label>

      <label className="form-field">
        <span>Repetir cada cuántas horas</span>
        <input
          type="number"
          min={1}
          max={168}
          value={intervalHours}
          onChange={(event) => setIntervalHours(event.target.value)}
        />
      </label>

      <div className="source-edit-grid">
        <label className="form-field">
          <span>API key de OpenAI</span>
          <input
            type="password"
            value={openaiApiKey}
            onChange={(event) => setOpenaiApiKey(event.target.value)}
            placeholder={settings.openai_api_key_configured ? "Cargada. Escribí una nueva para reemplazar." : "sk-..."}
          />
        </label>

        <label className="form-field">
          <span>Modelo</span>
          <input value={openaiModel} onChange={(event) => setOpenaiModel(event.target.value)} placeholder="gpt-4.1-mini" />
        </label>
      </div>

      <label className="form-field">
        <span>Master prompt</span>
        <textarea
          rows={6}
          value={masterPrompt}
          onChange={(event) => setMasterPrompt(event.target.value)}
          placeholder="Instrucción base para resumir, extraer requisitos y riesgos."
        />
      </label>

      <div className="hero-actions">
        <button type="button" onClick={saveSettings} disabled={isPending} className="button-primary">
          Guardar automatización
        </button>
        <button type="button" onClick={runNow} disabled={isPending} className="button-secondary">
          Ejecutar ahora
        </button>
      </div>

      <div className="priority-list compact-priority-list">
        <article className="priority-item">
          <div className="priority-body">
            <div className="meta">
              <span className="badge">{isEnabled ? "active" : "paused"}</span>
              <span className={`badge ${settings.openai_api_key_configured ? "tone-success" : "tone-warning"}`}>
                {settings.openai_api_key_configured ? "OpenAI listo" : "OpenAI sin key"}
              </span>
            </div>
            <h3>Última corrida</h3>
            <p>{settings.last_run_started_at ? new Date(settings.last_run_started_at).toLocaleString("es-AR") : "Todavía no ejecutó."}</p>
          </div>
        </article>
        <article className="priority-item">
          <div className="priority-body">
            <h3>Modelo activo</h3>
            <p>{openaiModel || "Usando default del servidor."}</p>
          </div>
        </article>
      </div>

      <p className="muted" style={{ marginTop: -4 }}>
        La API key no se muestra después de guardarla. Si escribís una nueva, reemplaza la actual.
      </p>

      {settings.last_error_message ? (
        <p className="form-message form-message-block">{`Último error: ${settings.last_error_message}`}</p>
      ) : null}
      {message ? <p className="form-message form-message-block">{message}</p> : null}
    </div>
  );
}
