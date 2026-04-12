"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import type { CompanyLookup } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

function renderTaxStatus(lookup: CompanyLookup | null) {
  if (!lookup?.tax_status_json) {
    return [];
  }

  return Object.entries(lookup.tax_status_json)
    .filter(([, value]) => value !== null && value !== "" && value !== false)
    .slice(0, 4);
}

export function SignupForm() {
  const router = useRouter();
  const [form, setForm] = useState({
    full_name: "",
    cuit: "",
    company_name: "",
    email: "",
    password: "",
  });
  const [companyLookup, setCompanyLookup] = useState<CompanyLookup | null>(null);
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function updateField<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function lookupCompany() {
    startTransition(async () => {
      setMessage("");
      setCompanyLookup(null);
      const response = await fetch(`${API_BASE_URL}/api/v1/company-lookup/cuit/${encodeURIComponent(form.cuit)}`, {
        credentials: "include",
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(payload?.detail ?? "No pudimos consultar ese CUIT.");
        return;
      }
      const lookup = payload as CompanyLookup;
      setCompanyLookup(lookup);
      setForm((current) => ({
        ...current,
        company_name: lookup.company_name,
      }));
    });
  }

  function submit() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/signup`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify(form),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(payload?.detail ?? "No se pudo crear la cuenta.");
        return;
      }
      router.push("/mi-cuenta?onboarding=1");
      router.refresh();
    });
  }

  const taxStatus = renderTaxStatus(companyLookup);

  return (
    <div className="auth-form-card auth-form-card-upgraded">
      <div className="signup-form-header">
        <span className="section-kicker">Paso 1 · Identidad legal</span>
        <h2>Ingresá el CUIT y empezá con una base empresarial confiable.</h2>
        <p>
          El onboarding está pensado para llegar rápido a valor real: identificar la empresa, confirmar el perfil base
          y pasar a una operación ya orientada.
        </p>
      </div>

      <div className="signup-stage-strip">
        <span className="mini-pill">CUIT</span>
        <span className="mini-pill">Empresa</span>
        <span className="mini-pill">Perfil inicial</span>
        <span className="mini-pill">Workspace</span>
      </div>

      <div className="field">
        <label htmlFor="signup-cuit">CUIT de la empresa</label>
        <div className="source-edit-actions">
          <input
            id="signup-cuit"
            name="cuit"
            value={form.cuit}
            onChange={(event) => updateField("cuit", event.target.value)}
            autoComplete="off"
            inputMode="numeric"
            placeholder="30712345678…"
          />
          <button type="button" onClick={lookupCompany} disabled={isPending} className="button-secondary">
            {isPending ? "Consultando…" : "Validar CUIT"}
          </button>
        </div>
      </div>

      {companyLookup ? (
        <article className="detail-note-card signup-lookup-card signup-lookup-card-rich">
          <div className="results-header">
            <div>
              <span className="section-kicker">Empresa encontrada</span>
              <h2>{companyLookup.legal_name}</h2>
            </div>
            <span className="badge tone-success">Fuente legal {companyLookup.company_data_source}</span>
          </div>
          <div className="signup-lookup-grid">
            <article>
              <span>CUIT</span>
              <strong>{companyLookup.cuit}</strong>
            </article>
            <article>
              <span>Nombre comercial base</span>
              <strong>{companyLookup.company_name}</strong>
            </article>
            <article>
              <span>Actualización</span>
              <strong>{new Date(companyLookup.company_data_updated_at).toLocaleString("es-AR")}</strong>
            </article>
          </div>
          {taxStatus.length ? (
            <div className="meta">
              {taxStatus.map(([key, value]) => (
                <span key={key} className="badge">
                  {key}: {String(value)}
                </span>
              ))}
            </div>
          ) : null}
        </article>
      ) : null}

      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="signup-name">Tu nombre</label>
          <input
            id="signup-name"
            name="full_name"
            value={form.full_name}
            onChange={(event) => updateField("full_name", event.target.value)}
            autoComplete="name"
            placeholder="Ej. María López…"
          />
        </div>
        <div className="field">
          <label htmlFor="signup-company">Empresa</label>
          <input
            id="signup-company"
            name="company_name"
            value={form.company_name}
            onChange={(event) => updateField("company_name", event.target.value)}
            autoComplete="organization"
            placeholder="Razón social o nombre visible…"
          />
        </div>
      </div>

      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="signup-email">Email</label>
          <input
            id="signup-email"
            name="email"
            type="email"
            value={form.email}
            onChange={(event) => updateField("email", event.target.value)}
            autoComplete="email"
            spellCheck={false}
            placeholder="nombre@empresa.com…"
          />
        </div>
        <div className="field">
          <label htmlFor="signup-password">Contraseña</label>
          <input
            id="signup-password"
            name="password"
            type="password"
            value={form.password}
            onChange={(event) => updateField("password", event.target.value)}
            autoComplete="new-password"
            placeholder="Mínimo 8 caracteres…"
          />
        </div>
      </div>

      <div className="signup-confidence-bar">
        <span>Datos legales</span>
        <span>Empresa inicial</span>
        <span>Perfil comercial base</span>
        <span>Workspace listo</span>
      </div>

      <button type="button" onClick={submit} disabled={isPending} className="button-primary button-block">
        {isPending ? "Creando workspace…" : "Crear cuenta y abrir workspace"}
      </button>

      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
