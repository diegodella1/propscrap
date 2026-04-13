"use client";

import { useMemo, useState, useTransition } from "react";

import { formatFastApiDetail, type SourceAccess } from "../lib/api";

type Props = {
  access: SourceAccess;
  endpoint: string;
  title?: string;
  compact?: boolean;
};

export function CompanySourceAccessForm({ access, endpoint, title, compact = false }: Props) {
  const [mode, setMode] = useState<"all_active" | "custom">(access.source_scope_mode);
  const [selected, setSelected] = useState<number[]>(access.selected_source_ids);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isPending, startTransition] = useTransition();

  const orderedSources = useMemo(() => {
    return [...access.sources].sort((a, b) => {
      const aActive = a.is_active ? 0 : 1;
      const bActive = b.is_active ? 0 : 1;
      if (aActive !== bActive) return aActive - bActive;
      return a.name.localeCompare(b.name, "es");
    });
  }, [access.sources]);

  function toggleSource(sourceId: number) {
    setSelected((current) =>
      current.includes(sourceId) ? current.filter((value) => value !== sourceId) : [...current, sourceId].sort((a, b) => a - b),
    );
  }

  function handleSubmit(formData: FormData) {
    const nextMode = String(formData.get("source_scope_mode")) as "all_active" | "custom";
    setError(null);
    setMessage(null);
    startTransition(async () => {
      try {
        const response = await fetch(endpoint, {
          method: "PUT",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            source_scope_mode: nextMode,
            source_ids: nextMode === "custom" ? selected : [],
          }),
        });
        if (!response.ok) {
          const payload = await response.json().catch(() => null);
          throw new Error(formatFastApiDetail(payload));
        }
        setMessage("Alcance de fuentes actualizado.");
      } catch (err) {
        setError(err instanceof Error ? err.message : "No se pudo actualizar el alcance de fuentes.");
      }
    });
  }

  return (
    <form action={handleSubmit} className="stack-gap-md">
      <div className="stack-gap-xs">
        <span className="section-kicker">{title ?? "Fuentes habilitadas"}</span>
        <h3>{access.company_name}</h3>
        <p>
          Modo actual: <strong>{mode === "all_active" ? "Todas las activas" : "Selección custom"}</strong>. Efectivas hoy: {access.effective_source_ids.length}.
        </p>
        <p>
          El super admin define qué fuentes existen y cuáles quedan activas a nivel plataforma. Desde acá la empresa decide si hereda ese universo completo o si habilita solo algunas para su equipo.
        </p>
      </div>

      <div className="admin-overview-grid">
        <label className="panel admin-overview-card">
          <input
            type="radio"
            name="source_scope_mode"
            value="all_active"
            checked={mode === "all_active"}
            onChange={() => setMode("all_active")}
          />
          <span className="section-kicker">Modo</span>
          <h3>Todas las activas</h3>
          <p>La empresa hereda automáticamente toda fuente global activa publicada en el inventario principal.</p>
        </label>
        <label className="panel admin-overview-card">
          <input
            type="radio"
            name="source_scope_mode"
            value="custom"
            checked={mode === "custom"}
            onChange={() => setMode("custom")}
          />
          <span className="section-kicker">Modo</span>
          <h3>Selección custom</h3>
          <p>La empresa usa sólo las fuentes elegidas abajo, siempre que sigan activas globalmente por superadmin.</p>
        </label>
      </div>

      <div className={compact ? "admin-status-list" : "admin-quick-list"}>
        {orderedSources.map((source) => {
          const implemented = Boolean(source.connector_available || source.config_json?.implemented);
          const globallyActive = source.is_active;
          const checked = selected.includes(source.id);
          return (
            <label key={source.id} className="panel admin-overview-card" style={{ opacity: globallyActive ? 1 : 0.72 }}>
              <input
                type="checkbox"
                checked={checked}
                disabled={mode !== "custom"}
                onChange={() => toggleSource(source.id)}
              />
              <span className="section-kicker">{String(source.config_json?.tier ?? source.source_type)}</span>
              <h3>{source.name}</h3>
              <p>
                {globallyActive ? "Global activa" : "Global inactiva"} · {implemented ? "implementada" : "catálogo"}
              </p>
            </label>
          );
        })}
      </div>

      {error ? <p className="form-error">{error}</p> : null}
      {message ? <p className="form-success">{message}</p> : null}

      <div className="hero-actions">
        <button type="submit" className="button-primary" disabled={isPending}>
          {isPending ? "Guardando..." : "Guardar alcance"}
        </button>
      </div>
    </form>
  );
}
