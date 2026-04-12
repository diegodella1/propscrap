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
  const [resendApiKey, setResendApiKey] = useState("");
  const [openaiModel, setOpenaiModel] = useState(settings.openai_model ?? "gpt-4.1-mini");
  const [masterPrompt, setMasterPrompt] = useState(settings.llm_master_prompt ?? "");
  const [contactEmail, setContactEmail] = useState(settings.contact_email ?? "");
  const [contactWhatsappNumber, setContactWhatsappNumber] = useState(settings.contact_whatsapp_number ?? "");
  const [contactTelegramHandle, setContactTelegramHandle] = useState(settings.contact_telegram_handle ?? "");
  const [demoBookingUrl, setDemoBookingUrl] = useState(settings.demo_booking_url ?? "");
  const [resendFromEmail, setResendFromEmail] = useState(settings.resend_from_email ?? "");
  const [emailDeliveryEnabled, setEmailDeliveryEnabled] = useState(settings.email_delivery_enabled);
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();
  const lastRunLabel = settings.last_run_started_at
    ? new Date(settings.last_run_started_at).toLocaleString("es-AR")
    : "Todavía no ejecutó";
  const lastSuccessLabel = settings.last_success_at
    ? new Date(settings.last_success_at).toLocaleString("es-AR")
    : "Sin éxito registrado";

  function saveSettings() {
    startTransition(async () => {
      setMessage("");
      const parsedInterval = Number(intervalHours);
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/automation`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          is_enabled: isEnabled,
          ingestion_interval_hours: parsedInterval,
          openai_api_key: openaiApiKey || undefined,
          openai_model: openaiModel,
          llm_master_prompt: masterPrompt,
          contact_email: contactEmail,
          contact_whatsapp_number: contactWhatsappNumber,
          contact_telegram_handle: contactTelegramHandle,
          demo_booking_url: demoBookingUrl,
          resend_api_key: resendApiKey || undefined,
          resend_from_email: resendFromEmail,
          email_delivery_enabled: emailDeliveryEnabled,
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
      setResendApiKey("");
      setOpenaiModel(payload.openai_model ?? "gpt-4.1-mini");
      setMasterPrompt(payload.llm_master_prompt ?? "");
      setContactEmail(payload.contact_email ?? "");
      setContactWhatsappNumber(payload.contact_whatsapp_number ?? "");
      setContactTelegramHandle(payload.contact_telegram_handle ?? "");
      setDemoBookingUrl(payload.demo_booking_url ?? "");
      setResendFromEmail(payload.resend_from_email ?? "");
      setEmailDeliveryEnabled(Boolean(payload.email_delivery_enabled));
      setMessage("Automatización guardada.");
    });
  }

  function runNow() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/automation/run`, {
        method: "POST",
        credentials: "include",
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
          <h2>Control del ciclo</h2>
        </div>
        <p>Primero definí si el ciclo está activo. Después ajustá IA, captación pública y email transaccional.</p>
      </div>

      <div className="admin-form-intro">
        <p>Las claves no vuelven a mostrarse después de guardarlas. Si cargás una nueva, reemplaza la actual.</p>
      </div>

      <div className="admin-overview-grid">
        <article className="admin-overview-card">
          <span className="section-kicker">Estado</span>
          <h3>{isEnabled ? "Ciclo activo" : "Ciclo pausado"}</h3>
          <p>Última corrida: {lastRunLabel}</p>
        </article>
        <article className="admin-overview-card">
          <span className="section-kicker">IA</span>
          <h3>{settings.openai_api_key_configured ? "OpenAI listo" : "OpenAI incompleto"}</h3>
          <p>Modelo actual: {openaiModel}</p>
        </article>
        <article className="admin-overview-card">
          <span className="section-kicker">Email</span>
          <h3>{emailDeliveryEnabled ? "Email activo" : "Email pausado"}</h3>
          <p>{settings.resend_api_key_configured ? "Resend configurado." : "Falta configurar Resend."}</p>
        </article>
        <article className="admin-overview-card">
          <span className="section-kicker">Contacto</span>
          <h3>Canales públicos</h3>
          <p>{contactEmail || contactWhatsappNumber || contactTelegramHandle || "Todavía no configurados."}</p>
        </article>
      </div>

      <div className="ops-readiness-grid">
        <article className="ops-readiness-card">
          <span className="section-kicker">Readiness</span>
          <h3>Motor de IA</h3>
          <p>{settings.openai_api_key_configured ? "Listo para enriquecer y resumir." : "Falta API key de OpenAI."}</p>
        </article>
        <article className="ops-readiness-card">
          <span className="section-kicker">Readiness</span>
          <h3>Email</h3>
          <p>{settings.resend_api_key_configured && emailDeliveryEnabled ? "Listo para delivery transaccional." : "Canal incompleto o pausado."}</p>
        </article>
        <article className="ops-readiness-card">
          <span className="section-kicker">Ejecución</span>
          <h3>Último éxito</h3>
          <p>{lastSuccessLabel}</p>
        </article>
      </div>

      <section className="admin-settings-section">
        <div className="results-header">
          <div>
            <span className="section-kicker">Ciclo</span>
            <h2>Frecuencia y ejecución</h2>
          </div>
        </div>
        <div className="source-edit-grid source-edit-grid-compact">
          <label className="form-field">
            <span>Estado</span>
            <select value={isEnabled ? "on" : "off"} onChange={(event) => setIsEnabled(event.target.value === "on")}>
              <option value="on">Activa</option>
              <option value="off">Pausada</option>
            </select>
          </label>

          <label className="form-field">
            <span>Cada cuántas horas</span>
            <input
              type="number"
              min={1}
              max={168}
              value={intervalHours}
              onChange={(event) => setIntervalHours(event.target.value)}
            />
          </label>
        </div>
      </section>

      <section className="admin-settings-section">
        <div className="results-header">
          <div>
            <span className="section-kicker">IA</span>
            <h2>Modelo y prompt maestro</h2>
          </div>
        </div>
        <div className="source-edit-grid source-edit-grid-compact">
          <label className="form-field">
            <span>API key de OpenAI</span>
            <input
              type="password"
              value={openaiApiKey}
              onChange={(event) => setOpenaiApiKey(event.target.value)}
              placeholder={settings.openai_api_key_configured ? "Cargada. Escribí una nueva para reemplazar." : "sk-…"}
            />
          </label>

          <label className="form-field">
            <span>Modelo</span>
            <input value={openaiModel} onChange={(event) => setOpenaiModel(event.target.value)} placeholder="gpt-4.1-mini" />
          </label>
        </div>
        <div className="detail-note-card">
          <span className="section-kicker">Qué controla esto</span>
          <p>El modelo y el master prompt impactan resúmenes, requisitos, riesgos y explicaciones de match en toda la plataforma.</p>
        </div>

        <label className="form-field">
          <span>Master prompt</span>
          <textarea
            rows={5}
            value={masterPrompt}
            onChange={(event) => setMasterPrompt(event.target.value)}
            placeholder="Instrucción base para resumir, extraer requisitos y riesgos."
          />
        </label>
      </section>

      <section className="admin-settings-section">
        <div className="results-header">
          <div>
            <span className="section-kicker">Canales comerciales</span>
            <h2>Contacto y captación pública</h2>
          </div>
        </div>
        <div className="source-edit-grid source-edit-grid-compact">
          <label className="form-field">
            <span>Email comercial</span>
            <input value={contactEmail} onChange={(event) => setContactEmail(event.target.value)} placeholder="ventas@easytaciones.com" />
          </label>
          <label className="form-field">
            <span>URL para agendar demo</span>
            <input value={demoBookingUrl} onChange={(event) => setDemoBookingUrl(event.target.value)} placeholder="https://cal.com/…" />
          </label>
          <label className="form-field">
            <span>WhatsApp comercial</span>
            <input value={contactWhatsappNumber} onChange={(event) => setContactWhatsappNumber(event.target.value)} placeholder="+54911…" />
          </label>
          <label className="form-field">
            <span>Telegram</span>
            <input value={contactTelegramHandle} onChange={(event) => setContactTelegramHandle(event.target.value)} placeholder="@easytaciones" />
          </label>
        </div>
      </section>

      <section className="admin-settings-section">
        <div className="results-header">
          <div>
            <span className="section-kicker">Email transaccional</span>
            <h2>Delivery por email</h2>
          </div>
        </div>
        <div className="source-edit-grid source-edit-grid-compact">
          <label className="form-field">
            <span>Estado del canal email</span>
            <select
              value={emailDeliveryEnabled ? "on" : "off"}
              onChange={(event) => setEmailDeliveryEnabled(event.target.value === "on")}
            >
              <option value="off">Pausado</option>
              <option value="on">Activo</option>
            </select>
          </label>
          <label className="form-field">
            <span>API key de Resend</span>
            <input
              type="password"
              value={resendApiKey}
              onChange={(event) => setResendApiKey(event.target.value)}
              placeholder={settings.resend_api_key_configured ? "Cargada. Escribí una nueva para reemplazar." : "re_…"}
            />
          </label>
          <label className="form-field">
            <span>From email</span>
            <input value={resendFromEmail} onChange={(event) => setResendFromEmail(event.target.value)} placeholder="alerts@easytaciones.com" />
          </label>
        </div>
      </section>

      <div className="hero-actions">
        <button type="button" onClick={saveSettings} disabled={isPending} className="button-primary">
          Guardar automatización
        </button>
        <button type="button" onClick={runNow} disabled={isPending} className="button-secondary">
          Ejecutar ahora
        </button>
      </div>
      {settings.last_error_message ? (
        <p className="form-message form-message-block">{`Último error: ${settings.last_error_message}`}</p>
      ) : null}
      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
