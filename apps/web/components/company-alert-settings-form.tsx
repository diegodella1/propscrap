"use client";

import { useState, useTransition } from "react";

import { formatFastApiDetail, type CompanyProfile } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const DEADLINE_OPTIONS = [
  { hours: 168, label: "7 días antes" },
  { hours: 72, label: "3 días antes" },
  { hours: 24, label: "24 horas antes" },
];

export function CompanyAlertSettingsForm({ profile }: { profile: CompanyProfile }) {
  const alertPreferences = profile.alert_preferences_json ?? {};
  const [form, setForm] = useState({
    min_score: String(alertPreferences.min_score ?? 60),
    receive_relevant: alertPreferences.receive_relevant ?? true,
    receive_deadlines: alertPreferences.receive_deadlines ?? true,
    deadline_only_for_saved: alertPreferences.deadline_only_for_saved ?? true,
    deadline_offsets_hours: alertPreferences.deadline_offsets_hours ?? [168, 72, 24],
  });
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function toggleDeadlineOffset(hours: number) {
    setForm((current) => ({
      ...current,
      deadline_offsets_hours: current.deadline_offsets_hours.includes(hours)
        ? current.deadline_offsets_hours.filter((value) => value !== hours)
        : [...current.deadline_offsets_hours, hours].sort((a, b) => b - a),
    }));
  }

  function save() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/me/company-profile`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          cuit: profile.cuit,
          company_name: profile.company_name,
          legal_name: profile.legal_name,
          company_description: profile.company_description,
          sectors: profile.sectors,
          include_keywords: profile.include_keywords,
          exclude_keywords: profile.exclude_keywords,
          jurisdictions: profile.jurisdictions,
          preferred_buyers: profile.preferred_buyers,
          min_amount: profile.min_amount,
          max_amount: profile.max_amount,
          tax_status_json: profile.tax_status_json,
          alert_preferences_json: {
            min_score: Number(form.min_score || 60),
            receive_relevant: form.receive_relevant,
            receive_deadlines: form.receive_deadlines,
            deadline_only_for_saved: form.deadline_only_for_saved,
            deadline_offsets_hours: form.deadline_offsets_hours,
          },
        }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(formatFastApiDetail(payload ?? { detail: "No se pudo guardar la configuración de alertas." }));
        return;
      }
      setMessage("Reglas de alertas de empresa guardadas.");
    });
  }

  return (
    <div className="auth-form-card auth-form-card-upgraded auth-form-card--surface">
      <div className="signup-form-header">
        <span className="section-kicker">Alertas por empresa</span>
        <h2>WhatsApp y reglas default de alertas</h2>
        <p>
          Estas reglas definen qué se considera relevante para la empresa y cuándo conviene avisar sobre licitaciones ya guardadas.
        </p>
      </div>

      <div className="field">
        <label htmlFor="company-alert-min-score">Nueva licitación con score mayor o igual a</label>
        <input
          id="company-alert-min-score"
          value={form.min_score}
          onChange={(event) => setForm((current) => ({ ...current, min_score: event.target.value }))}
          inputMode="numeric"
          placeholder="60"
        />
      </div>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.receive_relevant}
          onChange={(event) => setForm((current) => ({ ...current, receive_relevant: event.target.checked }))}
        />
        <span>Activar alertas de nuevas licitaciones relevantes</span>
      </label>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.receive_deadlines}
          onChange={(event) => setForm((current) => ({ ...current, receive_deadlines: event.target.checked }))}
        />
        <span>Activar recordatorios de fechas detectadas automáticamente</span>
      </label>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.deadline_only_for_saved}
          onChange={(event) => setForm((current) => ({ ...current, deadline_only_for_saved: event.target.checked }))}
        />
        <span>Enviar recordatorios solo sobre licitaciones guardadas o en seguimiento</span>
      </label>

      <div className="field">
        <label>Cuándo avisar por fechas críticas</label>
        <div className="state-form-suggestions">
          {DEADLINE_OPTIONS.map((option) => (
            <label key={option.hours} className="checkbox-row">
              <input
                type="checkbox"
                checked={form.deadline_offsets_hours.includes(option.hours)}
                onChange={() => toggleDeadlineOffset(option.hours)}
              />
              <span>{option.label}</span>
            </label>
          ))}
        </div>
      </div>

      <div className="detail-note-card">
        <span className="section-kicker">Cómo funciona</span>
        <p>
          La empresa define la regla base. Después cada usuario de la empresa puede elegir sus canales y activar su propio WhatsApp o Telegram desde su cuenta.
        </p>
      </div>

      <div className="signup-confidence-bar">
        <span>Discovery por score</span>
        <span>Fechas detectadas</span>
        <span>Solo guardadas</span>
        <span>Canales por usuario</span>
      </div>

      <button type="button" onClick={save} disabled={isPending} className="button-primary button-block">
        {isPending ? "Guardando reglas…" : "Guardar reglas de alertas"}
      </button>

      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
