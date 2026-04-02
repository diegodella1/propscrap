"use client";

import { useState, useTransition } from "react";

import type { Source } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

type DraftState = Record<number, Source>;

export function SourceEditorList({ sources }: { sources: Source[] }) {
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
        body: JSON.stringify({
          name: source.name,
          slug: source.slug,
          source_type: source.source_type,
          base_url: source.base_url,
          is_active: source.is_active,
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setMessages((current) => ({ ...current, [sourceId]: payload?.detail ?? "No se pudo guardar." }));
        return;
      }

      const saved = (await response.json()) as Source;
      setDrafts((current) => ({ ...current, [sourceId]: saved }));
      setMessages((current) => ({ ...current, [sourceId]: "Fuente actualizada." }));
    });
  }

  return (
    <div className="source-edit-stack">
      {sources.map((source) => {
        const draft = drafts[source.id];

        return (
          <article key={source.id} className="source-card">
            <div className="source-edit-grid">
              <div className="field">
                <label htmlFor={`source-name-${source.id}`}>Nombre</label>
                <input
                  id={`source-name-${source.id}`}
                  value={draft.name}
                  onChange={(event) => updateSource(source.id, { name: event.target.value })}
                />
              </div>
              <div className="field">
                <label htmlFor={`source-slug-${source.id}`}>Slug</label>
                <input
                  id={`source-slug-${source.id}`}
                  value={draft.slug}
                  onChange={(event) => updateSource(source.id, { slug: event.target.value })}
                />
              </div>
            </div>

            <div className="source-edit-grid">
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
                <label htmlFor={`source-url-${source.id}`}>Base URL</label>
                <input
                  id={`source-url-${source.id}`}
                  value={draft.base_url}
                  onChange={(event) => updateSource(source.id, { base_url: event.target.value })}
                />
              </div>
            </div>

            <div className="source-edit-actions">
              <div className="meta">
                <span className={`badge ${draft.is_active ? "tone-success" : "tone-muted"}`}>
                  {draft.is_active ? "activa" : "inactiva"}
                </span>
                <span className={`badge ${draft.connector_available ? "tone-calm" : "tone-warning"}`}>
                  {draft.connector_available ? "conector listo" : "sin conector"}
                </span>
              </div>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={draft.is_active}
                  onChange={(event) => updateSource(source.id, { is_active: event.target.checked })}
                />
                <span>Activa para seguimiento</span>
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

            {messages[source.id] ? <p className="form-message form-message-block">{messages[source.id]}</p> : null}
          </article>
        );
      })}
    </div>
  );
}
