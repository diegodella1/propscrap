"use client";

import { useState, useTransition } from "react";

import type { User } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function alertPriorityFromMinScore(value: number | undefined) {
  if ((value ?? 60) >= 75) return "alta";
  if ((value ?? 60) <= 0) return "todas";
  return "media";
}

export function AccountSettingsForm({ user }: { user: User }) {
  const [form, setForm] = useState({
    full_name: user.full_name,
    company_name: user.company_name ?? "",
    whatsapp_number: user.whatsapp_number ?? "",
    whatsapp_opt_in: user.whatsapp_opt_in,
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
        setMessage(payload?.detail ?? "No se pudo guardar tu perfil.");
        return;
      }
      setMessage("Perfil guardado.");
    });
  }

  return (
    <div className="auth-form-card">
      <div className="field">
        <label htmlFor="account-name">Tu nombre</label>
        <input
          id="account-name"
          value={form.full_name}
          onChange={(event) => updateField("full_name", event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="account-company">Empresa</label>
        <input
          id="account-company"
          value={form.company_name}
          onChange={(event) => updateField("company_name", event.target.value)}
        />
      </div>
      <div className="field">
        <label htmlFor="account-whatsapp">Tu WhatsApp</label>
        <input
          id="account-whatsapp"
          value={form.whatsapp_number}
          onChange={(event) => updateField("whatsapp_number", event.target.value)}
          placeholder="+5491123456789"
        />
      </div>

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
        {isPending ? "Guardando..." : "Guardar preferencias"}
      </button>

      {message ? <p className="form-message form-message-block">{message}</p> : null}
    </div>
  );
}
