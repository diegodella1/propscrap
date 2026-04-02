"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export function SignupForm() {
  const router = useRouter();
  const [form, setForm] = useState({
    full_name: "",
    company_name: "",
    email: "",
    password: "",
  });
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function updateField<K extends keyof typeof form>(key: K, value: (typeof form)[K]) {
    setForm((current) => ({ ...current, [key]: value }));
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

  return (
    <div className="auth-form-card">
      <div className="field">
        <label htmlFor="signup-name">Tu nombre</label>
        <input
          id="signup-name"
          value={form.full_name}
          onChange={(event) => updateField("full_name", event.target.value)}
          placeholder="Ej. María López"
        />
      </div>
      <div className="field">
        <label htmlFor="signup-company">Empresa</label>
        <input
          id="signup-company"
          value={form.company_name}
          onChange={(event) => updateField("company_name", event.target.value)}
          placeholder="Ej. Equipamiento Médico del Sur"
        />
      </div>
      <div className="field">
        <label htmlFor="signup-email">Email</label>
        <input
          id="signup-email"
          value={form.email}
          onChange={(event) => updateField("email", event.target.value)}
          placeholder="nombre@empresa.com"
        />
      </div>
      <div className="field">
        <label htmlFor="signup-password">Contraseña</label>
        <input
          id="signup-password"
          type="password"
          value={form.password}
          onChange={(event) => updateField("password", event.target.value)}
          placeholder="Mínimo 8 caracteres"
        />
      </div>
      <button type="button" onClick={submit} disabled={isPending} className="button-primary button-block">
        {isPending ? "Creando cuenta..." : "Crear cuenta"}
      </button>
      {message ? <p className="form-message form-message-block">{message}</p> : null}
    </div>
  );
}
