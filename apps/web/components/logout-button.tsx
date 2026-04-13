"use client";

import { useTransition } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

export function LogoutButton() {
  const [isPending, startTransition] = useTransition();

  function logout() {
    startTransition(async () => {
      await fetch(`${API_BASE_URL}/api/v1/auth/logout`, {
        method: "POST",
        credentials: "include",
        cache: "no-store",
      });
      window.location.assign("/login");
    });
  }

  return (
    <button type="button" onClick={logout} disabled={isPending} className="button-secondary">
      {isPending ? "Saliendo..." : "Cerrar sesión"}
    </button>
  );
}
