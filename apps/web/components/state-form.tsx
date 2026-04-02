"use client";

import { useState, useTransition } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

const STATES = ["new", "seen", "saved", "discarded", "evaluating", "presenting"];

function formatStateLabel(value: string) {
  switch (value) {
    case "new":
      return "Nuevo";
    case "seen":
      return "Visto";
    case "saved":
      return "Guardado";
    case "discarded":
      return "Descartado";
    case "evaluating":
      return "En evaluación";
    case "presenting":
      return "Presentando";
    default:
      return value;
  }
}

export function StateForm({
  tenderId,
  initialState,
}: {
  tenderId: number;
  initialState?: string;
}) {
  const [state, setState] = useState(initialState ?? "new");
  const [notes, setNotes] = useState("");
  const [message, setMessage] = useState<string>("");
  const [isPending, startTransition] = useTransition();

  function submit() {
    startTransition(async () => {
      setMessage("");
      const response = await fetch(`${API_BASE_URL}/api/v1/tenders/${tenderId}/state`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ state, notes }),
      });
      if (!response.ok) {
        setMessage("No se pudo guardar el estado.");
        return;
      }
      setMessage("Estado actualizado.");
    });
  }

  return (
    <div className="state-form">
      <select value={state} onChange={(event) => setState(event.target.value)}>
        {STATES.map((item) => (
          <option key={item} value={item}>
            {formatStateLabel(item)}
          </option>
        ))}
      </select>
      <textarea
        value={notes}
        onChange={(event) => setNotes(event.target.value)}
        placeholder="Nota breve para contexto interno o próximo paso"
        rows={4}
      />
      <button type="button" onClick={submit} disabled={isPending} className="button-primary button-block">
        {isPending ? "Guardando..." : "Guardar estado"}
      </button>
      {message ? <span className="form-message">{message}</span> : null}
    </div>
  );
}
