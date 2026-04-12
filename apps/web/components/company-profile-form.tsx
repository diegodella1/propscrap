"use client";

import { useMemo, useState, useTransition } from "react";

import type { CompanyProfile } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function toCsv(values: string[] | null | undefined) {
  return (values ?? []).join(", ");
}

function fromCsv(value: string) {
  return value
    .split(",")
    .map((item) => item.trim())
    .filter(Boolean);
}

export function CompanyProfileForm({
  profile,
  saveUrl,
  matchUrl,
}: {
  profile: CompanyProfile;
  saveUrl: string;
  matchUrl: string;
}) {
  const [form, setForm] = useState({
    cuit: profile.cuit ?? "",
    company_name: profile.company_name,
    legal_name: profile.legal_name ?? "",
    company_description: profile.company_description,
    sectors: toCsv(profile.sectors),
    include_keywords: toCsv(profile.include_keywords),
    exclude_keywords: toCsv(profile.exclude_keywords),
    jurisdictions: toCsv(profile.jurisdictions),
    preferred_buyers: toCsv(profile.preferred_buyers),
    min_amount: profile.min_amount ?? "",
    max_amount: profile.max_amount ?? "",
    min_score: String(profile.alert_preferences_json?.min_score ?? 60),
  });
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  const summary = useMemo(() => {
    return [
      `${fromCsv(form.include_keywords).length} keywords positivas`,
      `${fromCsv(form.exclude_keywords).length} keywords negativas`,
      `${fromCsv(form.jurisdictions).length} jurisdicciones`,
      `${fromCsv(form.preferred_buyers).length} compradores`,
    ].join(" · ");
  }, [form.exclude_keywords, form.include_keywords, form.jurisdictions, form.preferred_buyers]);

  function updateField<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function saveProfile() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}${saveUrl}`, {
        method: "PUT",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          cuit: form.cuit || null,
          company_name: form.company_name,
          legal_name: form.legal_name || null,
          company_description: form.company_description,
          sectors: fromCsv(form.sectors),
          include_keywords: fromCsv(form.include_keywords),
          exclude_keywords: fromCsv(form.exclude_keywords),
          jurisdictions: fromCsv(form.jurisdictions),
          preferred_buyers: fromCsv(form.preferred_buyers),
          min_amount: form.min_amount || null,
          max_amount: form.max_amount || null,
          alert_preferences_json: { min_score: Number(form.min_score || 60) },
          tax_status_json: profile.tax_status_json,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setMessage(payload?.detail ?? "No se pudo guardar el perfil.");
        return;
      }

      const matchResponse = await fetch(`${API_BASE_URL}${matchUrl}`, {
        method: "POST",
        credentials: "include",
      });

      if (!matchResponse.ok) {
        setMessage("Perfil guardado, pero no se pudo recalcular el matching.");
        return;
      }

      setMessage("Perfil guardado y matching recalculado.");
    });
  }

  return (
    <div className="company-profile-form">
      <div className="profile-summary-bar">{summary}</div>
      <div className="signup-form-header">
        <span className="section-kicker">Perfil</span>
        <h2>Empresa y reglas de matching</h2>
        <p>Completá identidad, keywords, compradores y alcance de búsqueda.</p>
      </div>

      <div className="field">
        <label htmlFor="company-name">Empresa</label>
        <input
          id="company-name"
          value={form.company_name}
          onChange={(event) => updateField("company_name", event.target.value)}
        />
      </div>
      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="company-cuit">CUIT</label>
          <input id="company-cuit" value={form.cuit} disabled />
        </div>
        <div className="field">
          <label htmlFor="company-legal-name">Razón social</label>
          <input
            id="company-legal-name"
            value={form.legal_name}
            onChange={(event) => updateField("legal_name", event.target.value)}
          />
        </div>
      </div>
      {profile.company_data_source ? (
        <div className="detail-note-card">
          <span className="section-kicker">Fuente legal</span>
          <p>
            {profile.company_data_source}
            {profile.company_data_updated_at ? ` · ${new Date(profile.company_data_updated_at).toLocaleString("es-AR")}` : ""}
          </p>
        </div>
      ) : null}

      <div className="field">
        <label htmlFor="company-description">Descripción de la empresa</label>
        <textarea
          id="company-description"
          rows={5}
          value={form.company_description}
          onChange={(event) => updateField("company_description", event.target.value)}
          placeholder="Qué vende, a quién le vende, cómo compite y qué documentación suele presentar…"
        />
      </div>

      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="company-sectors">Sectores</label>
          <input
            id="company-sectors"
            value={form.sectors}
            onChange={(event) => updateField("sectors", event.target.value)}
            placeholder="software, salud, infraestructura IT"
          />
        </div>
        <div className="field">
          <label htmlFor="profile-min-score">Umbral de alerta</label>
          <input
            id="profile-min-score"
            value={form.min_score}
            onChange={(event) => updateField("min_score", event.target.value)}
            placeholder="60"
          />
        </div>
      </div>

      <div className="field">
        <label htmlFor="include-keywords">Keywords positivas</label>
        <textarea
          id="include-keywords"
          rows={4}
          value={form.include_keywords}
          onChange={(event) => updateField("include_keywords", event.target.value)}
          placeholder="software, licencias, soporte, digitalizacion, mantenimiento, mesa de ayuda…"
        />
      </div>

      <div className="field">
        <label htmlFor="exclude-keywords">Keywords negativas</label>
        <textarea
          id="exclude-keywords"
          rows={3}
          value={form.exclude_keywords}
          onChange={(event) => updateField("exclude_keywords", event.target.value)}
          placeholder="textiles, panificados, avícolas"
        />
      </div>

      <div className="field">
        <label htmlFor="jurisdictions">Jurisdicciones preferidas</label>
        <input
          id="jurisdictions"
          value={form.jurisdictions}
          onChange={(event) => updateField("jurisdictions", event.target.value)}
          placeholder="Nación, Provincia de Buenos Aires"
        />
      </div>

      <div className="field">
        <label htmlFor="preferred-buyers">Compradores preferidos</label>
        <textarea
          id="preferred-buyers"
          rows={3}
          value={form.preferred_buyers}
          onChange={(event) => updateField("preferred_buyers", event.target.value)}
          placeholder="Ministerio de Salud, ANSES, Hospital"
        />
      </div>

      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="min-amount">Monto mínimo</label>
          <input
            id="min-amount"
            value={form.min_amount}
            onChange={(event) => updateField("min_amount", event.target.value)}
            placeholder="1000000"
          />
        </div>
        <div className="field">
          <label htmlFor="max-amount">Monto máximo</label>
          <input
            id="max-amount"
            value={form.max_amount}
            onChange={(event) => updateField("max_amount", event.target.value)}
            placeholder="100000000"
          />
        </div>
      </div>

      <button type="button" onClick={saveProfile} disabled={isPending} className="button-primary button-block">
        {isPending ? "Guardando y recalculando…" : "Guardar perfil y recalcular relevancia"}
      </button>

      <div className="signup-confidence-bar">
        <span>Fit comercial</span>
        <span>Buyers</span>
        <span>Jurisdicción</span>
        <span>Umbral</span>
      </div>

      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
