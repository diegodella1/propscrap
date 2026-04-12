import Link from "next/link";
import { redirect } from "next/navigation";

import { PageShell } from "../../../components/layout/page-shell";
import { SavedTenderAlertOverrides } from "../../../components/saved-tender-alert-overrides";
import { SiteHeader } from "../../../components/site-header";
import { fetchSavedTenders } from "../../../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession } from "../../../lib/session";

const PIPELINE = [
  { key: "saved", label: "Guardadas" },
  { key: "evaluating", label: "En revisión" },
  { key: "presenting", label: "Preparando oferta" },
];

function deadlineLabel(value: string | null) {
  if (!value) return "Sin fecha";
  const diff = new Date(value).getTime() - Date.now();
  if (diff < 0) return "Vencida";
  if (diff < 1000 * 60 * 60 * 24 * 3) return "Muy cerca";
  if (diff < 1000 * 60 * 60 * 24 * 7) return "Esta semana";
  return "Con margen";
}

export default async function SavedTendersPage() {
  const [currentUser, cookieHeader] = await Promise.all([
    getCurrentUserFromSession(),
    getCookieHeaderFromSession(),
  ]);

  if (!currentUser) {
    redirect("/login");
  }

  const saved = await fetchSavedTenders(cookieHeader || undefined);
  if (!saved) {
    redirect("/login");
  }

  const grouped = PIPELINE.map((column) => ({
    ...column,
    items: saved.items.filter((item) => item.states[0]?.state === column.key),
  }));

  return (
    <PageShell variant="workspace" className="workspace-shell page-screen page-screen--saved">
      <SiteHeader section="saved" currentUserName={currentUser.full_name} currentUserRole={currentUser.role} />

      <section className="workspace-header">
        <div>
          <span className="eyebrow">Seguimiento comercial</span>
          <h1>Pipeline.</h1>
          <p>Cartera activa ordenada por etapa para no perder timing ni contexto.</p>
        </div>
        <div className="workspace-header-actions">
          <Link href="/dashboard" className="button-secondary">
            Volver a oportunidades
          </Link>
        </div>
      </section>

      <section className="dashboard-executive-band workspace-kpi-band">
        {grouped.map((column) => (
          <article key={column.key}>
            <span>{column.label}</span>
            <strong>{column.items.length}</strong>
          </article>
        ))}
        <article>
          <span>Total en cartera</span>
          <strong>{saved.total}</strong>
        </article>
      </section>

      {saved.total === 0 ? (
        <section className="workspace-empty-state workspace-empty-state-strong">
          <strong>Tu pipeline todavía está vacío.</strong>
          <p>Guardá una licitación desde discovery para empezar a ordenar seguimiento, notas y fechas clave.</p>
          <Link href="/dashboard" className="button-primary">
            Ir a oportunidades
          </Link>
        </section>
      ) : null}

      <section className="pipeline-board workspace-pipeline-board">
        {grouped.map((column) => (
          <article key={column.key} className="pipeline-column">
            <div className="pipeline-column-head">
              <span className="section-kicker">{column.label}</span>
              <strong>{column.items.length}</strong>
            </div>
            <div className="pipeline-column-body">
              {column.items.length ? (
                column.items.map((item) => (
                  <article key={item.id} className="pipeline-card">
                    <div className="meta">
                      <span className="source-chip">{item.source.name}</span>
                      <span className="badge tone-calm">{deadlineLabel(item.deadline_date)}</span>
                    </div>
                    <strong>{item.title}</strong>
                    <p>{item.organization ?? "Sin organismo"} · {item.jurisdiction ?? "Sin jurisdicción"}</p>
                    {item.matches[0]?.reasons_json?.summary?.[0] ? (
                      <p className="muted">{item.matches[0].reasons_json?.summary?.[0]}</p>
                    ) : null}
                    <SavedTenderAlertOverrides
                      tenderId={item.id}
                      state={item.states[0]?.state ?? "saved"}
                      notes={item.states[0]?.notes ?? null}
                      alertOverrides={item.states[0]?.alert_overrides_json ?? null}
                    />
                    <div className="pipeline-card-footer">
                      <span className="muted">{item.states[0]?.notes ?? "Sin nota interna todavía"}</span>
                      <Link href={`/tenders/${item.id}`} className="linkish">
                        Abrir dossier
                      </Link>
                    </div>
                  </article>
                ))
              ) : (
                <div className="pipeline-empty workspace-empty-state">
                  <p>No hay licitaciones en esta etapa.</p>
                </div>
              )}
            </div>
          </article>
        ))}
      </section>
    </PageShell>
  );
}
