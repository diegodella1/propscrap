"use client";

import { useState, useTransition } from "react";

import { formatFastApiDetail, type User } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function alertPriorityFromMinScore(value: number | undefined) {
  if ((value ?? 60) >= 75) return "alta";
  if ((value ?? 60) <= 0) return "todas";
  return "media";
}

export function AccountSettingsForm({ user }: { user: User }) {
  const [form, setForm] = useState({
    full_name: user.full_name,
    cuit: user.cuit ?? "",
    company_name: user.company_name ?? "",
    whatsapp_number: user.whatsapp_number ?? "",
    whatsapp_opt_in: user.whatsapp_opt_in,
    email_opt_in: user.alert_preferences_json?.channels?.includes("email") ?? false,
    alert_priority: alertPriorityFromMinScore(user.alert_preferences_json?.min_score),
    receive_relevant: user.alert_preferences_json?.receive_relevant ?? true,
    receive_deadlines: user.alert_preferences_json?.receive_deadlines ?? true,
  });
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function updateField<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function save() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/me`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(form),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(formatFastApiDetail(payload ?? { detail: "No se pudo guardar tu perfil." }));
        return;
      }
      setMessage("Perfil guardado.");
    });
  }

  return (
    <div className="auth-form-card auth-form-card-upgraded">
      <div className="signup-form-header">
        <span className="section-kicker">Preferencias personales</span>
        <h2>Canal e intensidad de alertas</h2>
        <p>Definí cómo te avisa la plataforma y con qué nivel de filtro.</p>
      </div>
      <div className="signup-stage-strip">
        <span className="mini-pill">Identidad</span>
        <span className="mini-pill">Canal</span>
        <span className="mini-pill">Prioridad</span>
        <span className="mini-pill">Recordatorios</span>
      </div>
      <div className="field">
        <label htmlFor="account-name">Tu nombre</label>
        <input
          id="account-name"
          name="full_name"
          value={form.full_name}
          onChange={(event) => updateField("full_name", event.target.value)}
          autoComplete="name"
        />
      </div>
      <div className="field">
        <label htmlFor="account-company">Empresa</label>
        <input
          id="account-company"
          name="company_name"
          value={form.company_name}
          onChange={(event) => updateField("company_name", event.target.value)}
          autoComplete="organization"
        />
      </div>
      <div className="field">
        <label htmlFor="account-cuit">CUIT</label>
        <input
          id="account-cuit"
          name="cuit"
          value={form.cuit}
          onChange={(event) => updateField("cuit", event.target.value)}
          autoComplete="off"
          inputMode="numeric"
          placeholder="30712345678…"
        />
      </div>
      <div className="field">
        <label htmlFor="account-whatsapp">Tu WhatsApp</label>
        <input
          id="account-whatsapp"
          name="whatsapp_number"
          type="tel"
          value={form.whatsapp_number}
          onChange={(event) => updateField("whatsapp_number", event.target.value)}
          autoComplete="tel"
          inputMode="tel"
          placeholder="+5491123456789…"
        />
      </div>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.email_opt_in}
          onChange={(event) => updateField("email_opt_in", event.target.checked)}
        />
        <span>Quiero recibir alertas por email</span>
      </label>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.whatsapp_opt_in}
          onChange={(event) => updateField("whatsapp_opt_in", event.target.checked)}
        />
        <span>Quiero recibir alertas por WhatsApp</span>
      </label>

      <div className="field">
        <label htmlFor="account-priority">Qué tan filtradas querés las alertas</label>
        <select
          id="account-priority"
          value={form.alert_priority}
          onChange={(event) =>
            updateField("alert_priority", event.target.value as "alta" | "media" | "todas")
          }
        >
          <option value="alta">Solo alta prioridad</option>
          <option value="media">Media o alta</option>
          <option value="todas">Todas</option>
        </select>
      </div>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.receive_relevant}
          onChange={(event) => updateField("receive_relevant", event.target.checked)}
        />
        <span>Avisarme cuando aparezca una licitación relevante</span>
      </label>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.receive_deadlines}
          onChange={(event) => updateField("receive_deadlines", event.target.checked)}
        />
        <span>Recordarme los vencimientos</span>
      </label>

      <button type="button" onClick={save} disabled={isPending} className="button-primary button-block">
        {isPending ? "Guardando…" : "Guardar preferencias"}
      </button>

      <div className="signup-confidence-bar">
        <span>Identidad</span>
        <span>Canal</span>
        <span>Ruido útil</span>
        <span>Seguimiento</span>
      </div>

      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
