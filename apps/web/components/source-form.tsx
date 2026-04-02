"use client";

import { useState, useTransition } from "react";

import type { SourceCreateInput } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const INITIAL_FORM: SourceCreateInput = {
  name: "",
  slug: "",
  source_type: "portal",
  base_url: "",
  is_active: true,
};

export function SourceForm() {
  const [form, setForm] = useState<SourceCreateInput>(INITIAL_FORM);
  const [message, setMessage] = useState("");
  const [isPending, startTransition] = useTransition();

  function updateField<K extends keyof SourceCreateInput>(key: K, value: SourceCreateInput[K]) {
    setForm((current) => ({ ...current, [key]: value }));
  }

  function submit() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/sources`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(form),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setMessage(payload?.detail ?? "No se pudo guardar la fuente.");
        return;
      }

      setForm(INITIAL_FORM);
      setMessage("Fuente guardada. Refrescá la vista para verla en el inventario.");
    });
  }

  return (
    <div className="source-form">
      <div className="field">
        <label htmlFor="source-name">Nombre</label>
        <input
          id="source-name"
          value={form.name}
          onChange={(event) => updateField("name", event.target.value)}
          placeholder="Ej. Boletín Oficial CABA"
        />
      </div>

      <div className="source-form-grid">
        <div className="field">
          <label htmlFor="source-slug">Slug</label>
          <input
            id="source-slug"
            value={form.slug}
            onChange={(event) => updateField("slug", event.target.value)}
            placeholder="boletin-caba"
          />
        </div>
        <div className="field">
          <label htmlFor="source-type">Tipo</label>
          <select
            id="source-type"
            value={form.source_type}
            onChange={(event) => updateField("source_type", event.target.value)}
          >
            <option value="portal">portal</option>
            <option value="boletin">boletin</option>
            <option value="marketplace">marketplace</option>
            <option value="manual">manual</option>
          </select>
        </div>
      </div>

      <div className="field">
        <label htmlFor="source-url">Base URL</label>
        <input
          id="source-url"
          value={form.base_url}
          onChange={(event) => updateField("base_url", event.target.value)}
          placeholder="https://ejemplo.gob.ar"
        />
      </div>

      <label className="checkbox-row">
        <input
          type="checkbox"
          checked={form.is_active}
          onChange={(event) => updateField("is_active", event.target.checked)}
        />
        <span>Activar esta fuente para seguimiento</span>
      </label>

      <button type="button" onClick={submit} disabled={isPending} className="button-primary button-block">
        {isPending ? "Guardando fuente..." : "Guardar fuente"}
      </button>

      {message ? <p className="form-message form-message-block">{message}</p> : null}
    </div>
  );
}
