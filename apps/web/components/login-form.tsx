"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

import { formatFastApiDetail } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

type LoginVariant = "company" | "superadmin";

type Props = {
  variant?: LoginVariant;
};

const VARIANT_COPY: Record<
  LoginVariant,
  {
    eyebrow: string;
    title: string;
    description: string;
    submitLabel: string;
    pendingLabel: string;
    hint: string[];
    demoEmail: string;
    demoPassword: string;
    invalidRoleMessage: string;
  }
> = {
  company: {
    eyebrow: "Acceso empresa",
    title: "Entrá al workspace comercial",
    description: "Usá tu email de trabajo para volver a oportunidades, seguimiento y alertas de la prueba.",
    submitLabel: "Ingresar como cliente",
    pendingLabel: "Ingresando cliente…",
    hint: ["Oportunidades", "Seguimiento", "Empresa"],
    demoEmail: "manager@licitacionesia.local",
    demoPassword: "Manager1234",
    invalidRoleMessage: "Esta entrada es para clientes. Usá el acceso de superadmin.",
  },
  superadmin: {
    eyebrow: "Acceso plataforma",
    title: "Entrá a la consola superadmin",
    description: "Usá la cuenta de plataforma para gobernar fuentes, automatización, alertas y usuarios del piloto.",
    submitLabel: "Ingresar como superadmin",
    pendingLabel: "Ingresando superadmin…",
    hint: ["Fuentes", "Automatización", "Usuarios"],
    demoEmail: "admin@propscrap.local",
    demoPassword: "Admin1234",
    invalidRoleMessage: "Esta entrada es sólo para superadmin.",
  },
};

export function LoginForm({ variant = "company" }: Props) {
  const router = useRouter();
  const copy = VARIANT_COPY[variant];
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function submit() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({ email, password }),
      });
      const payload = await response.json().catch(() => null);
      if (!response.ok) {
        setMessage(formatFastApiDetail(payload ?? { detail: "No se pudo iniciar sesión." }));
        return;
      }

      const role = payload?.user?.role;
      if (variant === "superadmin" && role !== "admin") {
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: "POST",
          credentials: "include",
        }).catch(() => null);
        setMessage(copy.invalidRoleMessage);
        return;
      }

      if (variant === "company" && role === "admin") {
        await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
          method: "POST",
          credentials: "include",
        }).catch(() => null);
        setMessage(copy.invalidRoleMessage);
        return;
      }

      const target =
        role === "admin" ? "/admin/platform" : role === "manager" ? "/admin/company" : "/dashboard";
      router.push(target);
      router.refresh();
    });
  }

  return (
    <div className="auth-form-card auth-form-card-upgraded login-form-card">
      <div className="signup-form-header">
        <span className="section-kicker">{copy.eyebrow}</span>
        <h2>{copy.title}</h2>
        <p>{copy.description}</p>
      </div>
      <div className="detail-note-card login-demo-card">
        <span className="section-kicker">Credenciales demo</span>
        <p>
          <strong>Email:</strong> {copy.demoEmail}
        </p>
        <p>
          <strong>Contraseña:</strong> {copy.demoPassword}
        </p>
      </div>
      <div className="field">
        <label htmlFor="login-email">Email</label>
        <input
          id="login-email"
          name="email"
          type="email"
          value={email}
          onChange={(event) => setEmail(event.target.value)}
          autoComplete="email"
          spellCheck={false}
          placeholder="nombre@empresa.com…"
        />
      </div>
      <div className="field">
        <label htmlFor="login-password">Contraseña</label>
        <input
          id="login-password"
          name="password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
          autoComplete="current-password"
          placeholder="Tu contraseña…"
        />
      </div>
      <button type="button" onClick={submit} disabled={isPending} className="button-primary button-block">
        {isPending ? copy.pendingLabel : copy.submitLabel}
      </button>
      <div className="signup-confidence-bar">
        {copy.hint.map((item) => (
          <span key={item}>{item}</span>
        ))}
      </div>
      {message ? <p className="form-message form-message-block" aria-live="polite">{message}</p> : null}
    </div>
  );
}
