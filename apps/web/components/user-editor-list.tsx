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
  telegram_verified: boolean;
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
    telegram_verified: Boolean(user.telegram_verified_at),
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
        credentials: "include",
        body: JSON.stringify({
          full_name: user.full_name,
          cuit: user.cuit,
          role: user.role,
          is_active: user.is_active,
          whatsapp_number: user.whatsapp_number,
          whatsapp_opt_in: user.whatsapp_opt_in,
          whatsapp_verified: user.whatsapp_verified,
          telegram_chat_id: user.telegram_chat_id,
          telegram_opt_in: user.telegram_opt_in,
          telegram_verified: user.telegram_verified,
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
            <details className="admin-disclosure" open={user.id === users[0]?.id}>
              <summary className="admin-disclosure-summary">
                <div className="source-card-header">
                  <div>
                    <strong>{draft.full_name}</strong>
                    <p>{draft.email}</p>
                  </div>
                  <div className="meta">
                    <span className={`badge ${draft.is_active ? "tone-success" : "tone-muted"}`}>
                      {draft.is_active ? "Activo" : "Inactivo"}
                    </span>
                    <span className="badge tone-calm">{formatRoleLabel(draft.role)}</span>
                    <span className={`badge ${draft.whatsapp_verified ? "tone-success" : "tone-warning"}`}>
                      {draft.whatsapp_verified ? "WhatsApp verificado" : "WhatsApp sin verificar"}
                    </span>
                    <span className={`badge ${draft.telegram_verified ? "tone-success" : "tone-warning"}`}>
                      {draft.telegram_verified ? "Telegram verificado" : "Telegram sin verificar"}
                    </span>
                  </div>
                </div>
              </summary>

              <div className="admin-disclosure-panel">
                <div className="source-edit-grid source-edit-grid-compact">
                  <div className="field">
                    <label htmlFor={`user-name-${user.id}`}>Nombre</label>
                    <input
                      id={`user-name-${user.id}`}
                      name={`user-name-${user.id}`}
                      value={draft.full_name}
                      onChange={(event) => updateDraft(user.id, { full_name: event.target.value })}
                    />
                  </div>
                  <div className="field">
                    <label htmlFor={`user-email-${user.id}`}>Email</label>
                    <input
                      id={`user-email-${user.id}`}
                      name={`user-email-${user.id}`}
                      type="email"
                      value={draft.email}
                      disabled
                    />
                  </div>
                  <div className="field">
                    <label htmlFor={`user-cuit-${user.id}`}>CUIT</label>
                    <input
                      id={`user-cuit-${user.id}`}
                      name={`user-cuit-${user.id}`}
                      value={draft.cuit ?? ""}
                      onChange={(event) => updateDraft(user.id, { cuit: event.target.value })}
                      placeholder="30712345678…"
                    />
                  </div>
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
                    <label htmlFor={`user-whatsapp-${user.id}`}>WhatsApp</label>
                    <input
                      id={`user-whatsapp-${user.id}`}
                      name={`user-whatsapp-${user.id}`}
                      type="tel"
                      value={draft.whatsapp_number ?? ""}
                      onChange={(event) => updateDraft(user.id, { whatsapp_number: event.target.value })}
                      placeholder="+5491123456789…"
                    />
                  </div>
                  <div className="field">
                    <label htmlFor={`user-min-score-${user.id}`}>Min score</label>
                    <input
                      id={`user-min-score-${user.id}`}
                      name={`user-min-score-${user.id}`}
                      value={draft.min_score}
                      onChange={(event) => updateDraft(user.id, { min_score: event.target.value })}
                      placeholder="60…"
                    />
                  </div>
                  <div className="field">
                    <label htmlFor={`user-telegram-${user.id}`}>Telegram chat id</label>
                    <input
                      id={`user-telegram-${user.id}`}
                      name={`user-telegram-${user.id}`}
                      value={draft.telegram_chat_id ?? ""}
                      onChange={(event) => updateDraft(user.id, { telegram_chat_id: event.target.value })}
                      placeholder="123456789…"
                    />
                  </div>
                </div>

                <div className="field">
                  <label htmlFor={`user-channels-${user.id}`}>Canales</label>
                  <input
                    id={`user-channels-${user.id}`}
                    value={draft.channels_csv}
                    onChange={(event) => updateDraft(user.id, { channels_csv: event.target.value })}
                    placeholder="dashboard, email, whatsapp, telegram…"
                  />
                </div>

                <div className="admin-toggle-grid">
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
                    <span>Opt-in WhatsApp</span>
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
                      checked={draft.telegram_opt_in}
                      onChange={(event) => updateDraft(user.id, { telegram_opt_in: event.target.checked })}
                    />
                    <span>Opt-in Telegram</span>
                  </label>

                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={draft.telegram_verified}
                      onChange={(event) => updateDraft(user.id, { telegram_verified: event.target.checked })}
                    />
                    <span>Chat verificado</span>
                  </label>

                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={draft.receive_relevant}
                      onChange={(event) => updateDraft(user.id, { receive_relevant: event.target.checked })}
                    />
                    <span>Nuevas relevantes</span>
                  </label>

                  <label className="checkbox-row">
                    <input
                      type="checkbox"
                      checked={draft.receive_deadlines}
                      onChange={(event) => updateDraft(user.id, { receive_deadlines: event.target.checked })}
                    />
                    <span>Deadlines</span>
                  </label>
                </div>

                <div className="source-edit-actions">
                  <button
                    type="button"
                    onClick={() => saveUser(user.id)}
                    disabled={isPending}
                    className="button-secondary"
                  >
                    Guardar usuario
                  </button>
                </div>

                {messages[user.id] ? (
                  <p className="form-message form-message-block" aria-live="polite">{messages[user.id]}</p>
                ) : null}
              </div>
            </details>
          </article>
        );
      })}
    </div>
  );
}
