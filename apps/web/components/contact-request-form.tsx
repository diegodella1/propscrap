"use client";

import { useMemo, useState } from "react";

import type { PublicPlatformSettings } from "../lib/api";

type FormState = {
  fullName: string;
  companyName: string;
  email: string;
  cuit: string;
  role: string;
  message: string;
};

const INITIAL_FORM: FormState = {
  fullName: "",
  companyName: "",
  email: "",
  cuit: "",
  role: "",
  message: "",
};

type Props = {
  platformSettings: PublicPlatformSettings;
};

function buildMailtoHref(form: FormState, contactEmail: string) {
  const subject = `Solicitud de demo - ${form.companyName || form.fullName || "EasyTaciones"}`;
  const body = [
    `Nombre: ${form.fullName || "-"}`,
    `Empresa: ${form.companyName || "-"}`,
    `Email: ${form.email || "-"}`,
    `CUIT: ${form.cuit || "-"}`,
    `Rol: ${form.role || "-"}`,
    "",
    "Contexto operativo:",
    form.message || "-",
  ].join("\n");

  return `mailto:${encodeURIComponent(contactEmail)}?subject=${encodeURIComponent(subject)}&body=${encodeURIComponent(body)}`;
}

export function ContactRequestForm({ platformSettings }: Props) {
  const [form, setForm] = useState(INITIAL_FORM);
  const [message, setMessage] = useState("");
  const contactEmail = platformSettings.contact_email ?? "";

  const mailtoHref = useMemo(() => buildMailtoHref(form, contactEmail), [contactEmail, form]);

  function update<K extends keyof FormState>(key: K, value: FormState[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function submit() {
    if (!form.fullName || !form.companyName || !form.email || !form.message) {
      setMessage("Completá nombre, empresa, email y contexto operativo para pedir la demo.");
      return;
    }

    if (!contactEmail) {
      setMessage("Falta configurar el email comercial desde superadmin para activar la solicitud de demo.");
      return;
    }

    setMessage("");
    window.location.href = mailtoHref;
  }

  return (
    <article className="auth-form-card auth-form-card-upgraded contact-request-card contact-request-card--surface">
      <div className="signup-form-header">
        <span className="section-kicker">Solicitud de demo</span>
        <h2>Contanos cómo trabaja hoy tu empresa.</h2>
        <p>
          La demo sirve más cuando entra con contexto real: equipo, proceso actual y dónde se pierde tiempo hoy.
        </p>
      </div>

      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="contact-full-name">Nombre</label>
          <input
            id="contact-full-name"
            value={form.fullName}
            onChange={(event) => update("fullName", event.target.value)}
            placeholder="Ej. María López"
          />
        </div>
        <div className="field">
          <label htmlFor="contact-company-name">Empresa</label>
          <input
            id="contact-company-name"
            value={form.companyName}
            onChange={(event) => update("companyName", event.target.value)}
            placeholder="Ej. Acme SA"
          />
        </div>
      </div>

      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="contact-email">Email</label>
          <input
            id="contact-email"
            type="email"
            value={form.email}
            onChange={(event) => update("email", event.target.value)}
            placeholder="nombre@empresa.com"
          />
        </div>
        <div className="field">
          <label htmlFor="contact-cuit">CUIT</label>
          <input
            id="contact-cuit"
            value={form.cuit}
            onChange={(event) => update("cuit", event.target.value)}
            inputMode="numeric"
            placeholder="30712345678"
          />
        </div>
      </div>

      <div className="field">
        <label htmlFor="contact-role">Rol</label>
        <input
          id="contact-role"
          value={form.role}
          onChange={(event) => update("role", event.target.value)}
          placeholder="Ej. Gerente comercial / Responsable de licitaciones"
        />
      </div>

      <div className="field">
        <label htmlFor="contact-message">Contexto operativo</label>
        <textarea
          id="contact-message"
          rows={6}
          value={form.message}
          onChange={(event) => update("message", event.target.value)}
          placeholder="Ej. Hoy revisamos 8 portales, guardamos links en planillas y dependemos de una persona para seguir cierres y pliegos."
        />
      </div>

      <div className="signup-confidence-bar">
        <span>Contexto</span>
        <span>CUIT</span>
        <span>Demo enfocada</span>
        <span>Siguiente paso claro</span>
      </div>

      <button type="button" onClick={submit} className="button-primary button-block">
        Solicitar demo
      </button>

      {contactEmail ? (
        <p className="form-message form-message-block">
          La solicitud se abre sobre <strong>{contactEmail}</strong> para enviar el brief comercial.
        </p>
      ) : (
        <p className="form-message form-message-block">
          Configurá el email comercial desde superadmin para activar este flujo.
        </p>
      )}

      {message ? <p className="form-message form-message-block">{message}</p> : null}
    </article>
  );
}
