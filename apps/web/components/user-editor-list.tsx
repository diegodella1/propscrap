"use client";

import { useState, useTransition } from "react";

import type { User } from "../lib/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "";

type DraftUser = User & {
  min_score: string;
  channels_csv: string;
  receive_relevant: boolean;
  receive_deadlines: boolean;
  whatsapp_verified: boolean;
};

type DraftState = Record<number, DraftUser>;

function toDraft(user: User): DraftUser {
  return {
    ...user,
    min_score: String(user.alert_preferences_json?.min_score ?? 60),
    channels_csv: (user.alert_preferences_json?.channels ?? ["dashboard"]).join(", "),
    receive_relevant: user.alert_preferences_json?.receive_relevant ?? true,
    receive_deadlines: user.alert_preferences_json?.receive_deadlines ?? true,
    whatsapp_verified: Boolean(user.whatsapp_verified_at),
  };
}

function formatRoleLabel(value: string) {
  if (value === "analyst") return "Analista";
  if (value === "manager") return "Manager";
  if (value === "admin") return "Admin";
  return value;
}

function parseChannels(value: string) {
  return value
    .split(",")
    .map((item) => item.trim().toLowerCase())
    .filter(Boolean);
}

export function UserEditorList({
  users,
  canManagePlatformRoles = false,
}: {
  users: User[];
  canManagePlatformRoles?: boolean;
}) {
  const [drafts, setDrafts] = useState<DraftState>(
    Object.fromEntries(users.map((user) => [user.id, toDraft(user)])),
  );
  const [messages, setMessages] = useState<Record<number, string>>({});
  const [isPending, startTransition] = useTransition();

  function updateDraft(userId: number, patch: Partial<DraftUser>) {
    setDrafts((current) => ({
      ...current,
      [userId]: {
        ...current[userId],
        ...patch,
      },
    }));
  }

  function saveUser(userId: number) {
    const user = drafts[userId];
    startTransition(async () => {
      setMessages((current) => ({ ...current, [userId]: "" }));
      const response = await fetch(`${API_BASE_URL}/api/v1/admin/users/${userId}`, {
        method: "PATCH",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          full_name: user.full_name,
          role: user.role,
          is_active: user.is_active,
          whatsapp_number: user.whatsapp_number,
          whatsapp_opt_in: user.whatsapp_opt_in,
          whatsapp_verified: user.whatsapp_verified,
          alert_preferences_json: {
            min_score: Number(user.min_score || 60),
            channels: parseChannels(user.channels_csv),
            receive_relevant: user.receive_relevant,
            receive_deadlines: user.receive_deadlines,
          },
        }),
      });

      if (!response.ok) {
        const payload = await response.json().catch(() => null);
        setMessages((current) => ({ ...current, [userId]: payload?.detail ?? "No se pudo guardar." }));
        return;
      }

      const saved = (await response.json()) as User;
      setDrafts((current) => ({ ...current, [userId]: toDraft(saved) }));
      setMessages((current) => ({ ...current, [userId]: "Usuario actualizado." }));
    });
  }

  return (
    <div className="user-edit-stack">
      {users.map((user) => {
        const draft = drafts[user.id];
        return (
          <article key={user.id} className="source-card">
            <div className="source-edit-grid">
              <div className="field">
                <label htmlFor={`user-name-${user.id}`}>Nombre</label>
                <input
                  id={`user-name-${user.id}`}
                  value={draft.full_name}
                  onChange={(event) => updateDraft(user.id, { full_name: event.target.value })}
                />
              </div>
              <div className="field">
                <label htmlFor={`user-email-${user.id}`}>Email</label>
                <input id={`user-email-${user.id}`} value={draft.email} disabled />
              </div>
            </div>

            <div className="source-edit-grid">
              <div className="field">
                <label htmlFor={`user-role-${user.id}`}>Rol</label>
                <select
                  id={`user-role-${user.id}`}
                  value={draft.role}
                  onChange={(event) => updateDraft(user.id, { role: event.target.value })}
                >
                  <option value="analyst">Analista</option>
                  <option value="manager">Manager</option>
                  {canManagePlatformRoles ? <option value="admin">Admin</option> : null}
                </select>
              </div>
              <div className="field">
                <label>Estado</label>
                <div className="meta">
                  <span className={`badge ${draft.is_active ? "tone-success" : "tone-muted"}`}>
                    {draft.is_active ? "Activo" : "Inactivo"}
                  </span>
                  <span className="badge tone-calm">{formatRoleLabel(draft.role)}</span>
                  <span className={`badge ${draft.whatsapp_verified ? "tone-success" : "tone-warning"}`}>
                    {draft.whatsapp_verified ? "WhatsApp verificado" : "WhatsApp sin verificar"}
                  </span>
                </div>
              </div>
            </div>

            <div className="source-edit-grid">
              <div className="field">
                <label htmlFor={`user-whatsapp-${user.id}`}>WhatsApp</label>
                <input
                  id={`user-whatsapp-${user.id}`}
                  value={draft.whatsapp_number ?? ""}
                  onChange={(event) => updateDraft(user.id, { whatsapp_number: event.target.value })}
                  placeholder="+5491123456789"
                />
              </div>
              <div className="field">
                <label htmlFor={`user-min-score-${user.id}`}>Min score alertas</label>
                <input
                  id={`user-min-score-${user.id}`}
                  value={draft.min_score}
                  onChange={(event) => updateDraft(user.id, { min_score: event.target.value })}
                  placeholder="60"
                />
              </div>
            </div>

            <div className="field">
              <label htmlFor={`user-channels-${user.id}`}>Canales</label>
              <input
                id={`user-channels-${user.id}`}
                value={draft.channels_csv}
                onChange={(event) => updateDraft(user.id, { channels_csv: event.target.value })}
                placeholder="dashboard, whatsapp"
              />
            </div>

            <div className="source-edit-actions">
              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={draft.is_active}
                  onChange={(event) => updateDraft(user.id, { is_active: event.target.checked })}
                />
                <span>Usuario habilitado</span>
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={draft.whatsapp_opt_in}
                  onChange={(event) => updateDraft(user.id, { whatsapp_opt_in: event.target.checked })}
                />
                <span>Opt-in para WhatsApp</span>
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={draft.whatsapp_verified}
                  onChange={(event) => updateDraft(user.id, { whatsapp_verified: event.target.checked })}
                />
                <span>Número verificado</span>
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={draft.receive_relevant}
                  onChange={(event) => updateDraft(user.id, { receive_relevant: event.target.checked })}
                />
                <span>Alertas de nuevas relevantes</span>
              </label>

              <label className="checkbox-row">
                <input
                  type="checkbox"
                  checked={draft.receive_deadlines}
                  onChange={(event) => updateDraft(user.id, { receive_deadlines: event.target.checked })}
                />
                <span>Alertas de deadlines</span>
              </label>

              <button
                type="button"
                onClick={() => saveUser(user.id)}
                disabled={isPending}
                className="button-secondary"
              >
                Guardar usuario
              </button>
            </div>

            {messages[user.id] ? <p className="form-message form-message-block">{messages[user.id]}</p> : null}
          </article>
        );
      })}
    </div>
  );
}
