"use client";

import { useState, useTransition } from "react";
import { useRouter } from "next/navigation";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export function LoginForm() {
  const router = useRouter();
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
        setMessage(payload?.detail ?? "No se pudo iniciar sesión.");
        return;
      }
      router.push("/mi-cuenta");
      router.refresh();
    });
  }

  return (
    <div className="auth-form-card">
      <div className="field">
        <label htmlFor="login-email">Email</label>
        <input id="login-email" value={email} onChange={(event) => setEmail(event.target.value)} />
      </div>
      <div className="field">
        <label htmlFor="login-password">Contraseña</label>
        <input
          id="login-password"
          type="password"
          value={password}
          onChange={(event) => setPassword(event.target.value)}
        />
      </div>
      <button type="button" onClick={submit} disabled={isPending} className="button-primary button-block">
        {isPending ? "Ingresando..." : "Ingresar"}
      </button>
      {message ? <p className="form-message form-message-block">{message}</p> : null}
    </div>
  );
}
