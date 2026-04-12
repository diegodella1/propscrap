"use client";

import { useState, useTransition } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const DEADLINE_OPTIONS = [
  { hours: 168, label: "7 días" },
  { hours: 72, label: "3 días" },
  { hours: 24, label: "24h" },
];

export function SavedTenderAlertOverrides({
  tenderId,
  state,
  notes,
  alertOverrides,
}: {
  tenderId: number;
  state: string;
  notes: string | null;
  alertOverrides: {
    inherit_company_defaults?: boolean;
    receive_deadlines?: boolean;
    deadline_offsets_hours?: number[];
  } | null;
}) {
  const [form, setForm] = useState({
    inherit_company_defaults: alertOverrides?.inherit_company_defaults ?? true,
    receive_deadlines: alertOverrides?.receive_deadlines ?? true,
    deadline_offsets_hours: alertOverrides?.deadline_offsets_hours ?? [168, 72, 24],
  });
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function toggleOffset(hours: number) {
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
      const response = await fetch(`${API_BASE_URL}/api/v1/tenders/${tenderId}/state`, {
        method: "POST",
        credentials: "include",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          state,
          notes,
          alert_overrides_json: {
            inherit_company_defaults: form.inherit_company_defaults,
            receive_deadlines: form.receive_deadlines,
            deadline_offsets_hours: form.deadline_offsets_hours,
          },
        }),
      });
      if (!response.ok) {
        setMessage("No se pudo guardar el override de alertas.");
        return;
      }
      setMessage("Override guardado.");
    });
  }

  return (
    <details className="admin-disclosure">
      <summary className="admin-disclosure-summary">
        <strong>Overrides de alertas</strong>
      </summary>
      <div className="admin-disclosure-panel">
        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.inherit_company_defaults}
            onChange={(event) => setForm((current) => ({ ...current, inherit_company_defaults: event.target.checked }))}
          />
          <span>Usar reglas default de la empresa</span>
        </label>

        <label className="checkbox-row">
          <input
            type="checkbox"
            checked={form.receive_deadlines}
            onChange={(event) => setForm((current) => ({ ...current, receive_deadlines: event.target.checked }))}
            disabled={form.inherit_company_defaults}
          />
          <span>Recibir alertas de fechas para esta licitación</span>
        </label>

        <div className="state-form-suggestions">
          {DEADLINE_OPTIONS.map((option) => (
            <label key={option.hours} className="checkbox-row">
              <input
                type="checkbox"
                checked={form.deadline_offsets_hours.includes(option.hours)}
                onChange={() => toggleOffset(option.hours)}
                disabled={form.inherit_company_defaults}
              />
              <span>{option.label} antes</span>
            </label>
          ))}
        </div>

        <button type="button" className="button-secondary" onClick={save} disabled={isPending}>
          {isPending ? "Guardando…" : "Guardar override"}
        </button>
        {message ? <p className="form-message">{message}</p> : null}
      </div>
    </details>
  );
}
