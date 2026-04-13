"use client";

import { useState, useTransition } from "react";

import { formatFastApiDetail, type Source } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

type DraftState = Record<number, Source>;
type SourceRunSummary = {
  lastStartedAt: string | null;
  lastFinishedAt: string | null;
  lastStatus: string | null;
  lastItemsFound: number | null;
  lastItemsNew: number | null;
  lastErrorMessage: string | null;
};

export function SourceEditorList({
  sources,
  runSummaryBySourceId = {},
}: {
  sources: Source[];
  runSummaryBySourceId?: Record<number, SourceRunSummary>;
}) {
  const [drafts, setDrafts] = useState<DraftState>(
    Object.fromEntries(sources.map((source) => [source.id, { ...source }])),
  );
  const [messages, setMessages] = useState<Record<number, string>>({});
  const [isPending, startTransition] = useTransition();

  function updateSource(sourceId: number, patch: Partial<Source>) {
    setDrafts((current) => ({
      ...current,
      [sourceId]: {
        ...current[sourceId],
        ...patch,
      },
    }));
  }

  function saveSource(sourceId: number) {
    const source = drafts[sourceId];
    startTransition(async () => {
      setMessages((current) => ({ ...current, [sourceId]: "" }));
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/sources/${sourceId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        credentials: "include",
        body: JSON.stringify({
          name: source.name,
          slug: source.slug,
          source_type: source.source_type,
          scraping_mode: source.scraping_mode,
          connector_slug: source.connector_slug,
          base_url: source.base_url,
          config_json: source.config_json ?? {},
          is_active: source.is_active,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setMessages((current) => ({
          ...current,
          [sourceId]: formatFastApiDetail(payload ?? { detail: "No se pudo guardar." }),
        }));
        return;
      }

      const saved = (await response.json()) as Source;
      setDrafts((current) => ({ ...current, [sourceId]: saved }));
      setMessages((current) => ({ ...current, [sourceId]: "Fuente actualizada." }));
    });
  }

  return (
    <div className="source-edit-stack">
      <article className="panel admin-overview-card">
        <span className="section-kicker">Gobierno de fuentes</span>
        <h3>Registro maestro y habilitación por capas</h3>
        <p>
          Toda fuente nueva se registra primero en el catálogo global. Después el super admin decide si queda activa a nivel plataforma y cada admin de empresa puede heredar todas las activas o elegir un subset propio.
        </p>
      </article>
      {sources.map((source) => {
        const draft = drafts[source.id];
        const runSummary = runSummaryBySourceId[source.id];

        return (
          <article key={source.id} className="source-card">
            <details className="admin-disclosure" open={source.id === sources[0]?.id}>
              <summary className="admin-disclosure-summary">
                <div className="source-card-header">
                  <div>
                    <strong>{draft.name}</strong>
                    <p>{draft.base_url || "Sin URL base cargada."}</p>
                  </div>
                  <div className="meta">
                    <span className="badge">#{draft.id}</span>
                    <span className={`badge ${draft.is_active ? "tone-success" : "tone-muted"}`}>
                      {draft.is_active ? "Activa" : "Inactiva"}
                    </span>
                    <span className={`badge ${draft.connector_available ? "tone-calm" : "tone-warning"}`}>
                      {draft.connector_available ? "Conector listo" : "Sin conector"}
                    </span>
                  </div>
                </div>
              </summary>

              <div className="admin-disclosure-panel">
                <div className="source-edit-grid">
                  <div className="field">
                    <label htmlFor={`source-name-${source.id}`}>Nombre</label>
                    <input
                      id={`source-name-${source.id}`}
                      name={`source-name-${source.id}`}
                      value={draft.name}
                      onChange={(event) => updateSource(source.id, { name: event.target.value })}
                    />
                  </div>
                  <div className="field">
                    <label htmlFor={`source-slug-${source.id}`}>Slug</label>
                    <input
                      id={`source-slug-${source.id}`}
                      name={`source-slug-${source.id}`}
                      value={draft.slug}
                      onChange={(event) => updateSource(source.id, { slug: event.target.value })}
                    />
                  </div>
                </div>

                <div className="source-edit-grid source-edit-grid-compact">
                  <div className="field">
                    <label htmlFor={`source-type-${source.id}`}>Tipo</label>
                    <select
                      id={`source-type-${source.id}`}
                      value={draft.source_type}
                      onChange={(event) => updateSource(source.id, { source_type: event.target.value })}
                    >
                      <option value="portal">portal</option>
                      <option value="boletin">boletin</option>
                      <option value="marketplace">marketplace</option>
                      <option value="manual">manual</option>
                    </select>
                  </div>
                  <div className="field">
                    <label htmlFor={`source-mode-${source.id}`}>Modo</label>
                    <select
                      id={`source-mode-${source.id}`}
                      value={draft.scraping_mode}
                      onChange={(event) => updateSource(source.id, { scraping_mode: event.target.value })}
                    >
                      <option value="coded">coded</option>
                      <option value="api">api</option>
                      <option value="html">html</option>
                      <option value="pdf">pdf</option>
                      <option value="hybrid">hybrid</option>
                    </select>
                  </div>
                  <div className="field">
                    <label htmlFor={`source-connector-${source.id}`}>Conector</label>
                    <input
                      id={`source-connector-${source.id}`}
                      name={`source-connector-${source.id}`}
                      value={draft.connector_slug ?? ""}
                      onChange={(event) => updateSource(source.id, { connector_slug: event.target.value })}
                      placeholder="comprar…"
                    />
                  </div>
                  <div className="field">
                    <label htmlFor={`source-url-${source.id}`}>Base URL</label>
                    <input
                      id={`source-url-${source.id}`}
                      name={`source-url-${source.id}`}
                      type="url"
                      value={draft.base_url}
                      onChange={(event) => updateSource(source.id, { base_url: event.target.value })}
                    />
                  </div>
                </div>

                <div className="admin-status-list">
                  <article>
                    <strong>Visibilidad</strong>
                    <p>
                      {draft.is_active
                        ? "Disponible para que las empresas la hereden o la seleccionen en modo custom."
                        : "Oculta para empresas y usuarios finales hasta que el super admin la reactive."}
                    </p>
                  </article>
                  <article>
                    <strong>Ultima corrida</strong>
                    <p>
                      {runSummary?.lastStartedAt
                        ? `${new Date(runSummary.lastStartedAt).toLocaleString("es-AR")} · ${runSummary.lastStatus ?? "n/d"}`
                        : draft.last_run_at
                          ? `${new Date(draft.last_run_at).toLocaleString("es-AR")} · sin detalle reciente`
                          : "Sin corridas registradas"}
                    </p>
                  </article>
                  <article>
                    <strong>Resultado</strong>
                    <p>
                      {runSummary?.lastItemsFound != null && runSummary?.lastItemsNew != null
                        ? `${runSummary.lastItemsNew} nuevos / ${runSummary.lastItemsFound} encontrados`
                        : "Todavia no hay metricas de corrida"}
                    </p>
                  </article>
                  <article>
                    <strong>Incidente</strong>
                    <p>{runSummary?.lastErrorMessage || "Sin error reciente registrado"}</p>
                  </article>
                </div>

                <div className="field">
                  <label htmlFor={`source-config-${source.id}`}>Config JSON</label>
                  <textarea
                    id={`source-config-${source.id}`}
                    className="code-textarea"
                    rows={6}
                    value={JSON.stringify(draft.config_json ?? {}, null, 2)}
                    onChange={(event) => {
                      try {
                        updateSource(source.id, { config_json: JSON.parse(event.target.value) });
                        setMessages((current) => ({ ...current, [source.id]: "" }));
                      } catch {
                        setMessages((current) => ({ ...current, [source.id]: "El config JSON no es válido." }));
                      }
                    }}
                  />
                </div>

                <div className="source-edit-actions">
                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={draft.is_active}
                      onChange={(event) => updateSource(source.id, { is_active: event.target.checked })}
                    />
                    <span>Activa globalmente en el top de licitaciones</span>
                  </label>

                  <button
                    type="button"
                    onClick={() => saveSource(source.id)}
                    disabled={isPending}
                    className="button-secondary"
                  >
                    Guardar cambios
                  </button>
                </div>

                {messages[source.id] ? (
                  <p className="form-message form-message-block" aria-live="polite">{messages[source.id]}</p>
                ) : null}
              </div>
            </details>
          </article>
        );
      })}
    </div>
  );
}
