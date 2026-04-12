import Link from "next/link";
import { redirect } from "next/navigation";

import { FilterPanel } from "../../../components/filter-panel";
import { WorkspaceBoardIllustration } from "../../../components/landing-ornaments";
import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";
import { TendersTable } from "../../../components/tenders-table";
import { fetchAlerts, fetchSources, fetchTenders } from "../../../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession } from "../../../lib/session";

type Props = {
  searchParams: Promise<{
    source?: string;
    jurisdiction?: string;
    min_score?: string;
  }>;
};

function formatStateLabel(value: string | null | undefined) {
  switch (value) {
    case "new":
      return "Nueva";
    case "seen":
      return "Vista";
    case "saved":
      return "Guardada";
    case "discarded":
      return "Descartada";
    case "evaluating":
      return "En revisión";
    case "presenting":
      return "Preparando oferta";
    default:
      return value ?? "Sin estado";
  }
}

function deadlineLabel(value: string | null) {
  if (!value) return "Sin fecha";
  const diff = new Date(value).getTime() - Date.now();
  if (diff < 0) return "Vencida";
  if (diff < 1000 * 60 * 60 * 24) return "Cierra en 24h";
  if (diff < 1000 * 60 * 60 * 24 * 3) return "Cierra en 3 días";
  if (diff < 1000 * 60 * 60 * 24 * 7) return "Cierra esta semana";
  return "Con margen";
}

export default async function DashboardPage({ searchParams }: Props) {
  const params = await searchParams;
  const [currentUser, cookieHeader] = await Promise.all([
    getCurrentUserFromSession(),
    getCookieHeaderFromSession(),
  ]);

  if (!currentUser) {
    redirect("/login");
  }

  const [sources, tenders, alerts] = await Promise.all([
    fetchSources(),
    fetchTenders({
      source: params.source,
      jurisdiction: params.jurisdiction,
      min_score: params.min_score,
    }),
    fetchAlerts(cookieHeader || undefined),
  ]);

  const topPriority = [...tenders.items]
    .sort((a, b) => Number(b.matches[0]?.score ?? 0) - Number(a.matches[0]?.score ?? 0))
    .slice(0, 4);
  const urgentDeadlines = topPriority.filter((item) => {
    if (!item.deadline_date) return false;
    return new Date(item.deadline_date).getTime() - Date.now() < 1000 * 60 * 60 * 24 * 7;
  }).length;
  const inPipeline = tenders.items.filter((item) => {
    const state = item.states[0]?.state;
    return state === "saved" || state === "evaluating" || state === "presenting";
  }).length;
  const visibleAlerts = alerts.slice(0, 4);

  return (
    <PageShell variant="workspace" className="workspace-shell">
      <SiteHeader section="dashboard" currentUserName={currentUser.full_name} currentUserRole={currentUser.role} />

      <section className="workspace-header dashboard-header">
        <div>
          <span className="eyebrow">Workspace empresa</span>
          <h1>Oportunidades.</h1>
          <p>Inbox operativo con relevancia, urgencia y acceso inmediato al dossier.</p>
        </div>
        <div className="workspace-header-actions">
          <Link href="/saved" className="button-secondary">
            Ver seguimiento
          </Link>
          <Link href="/company-profile" className="button-primary">
            Ajustar perfil
          </Link>
        </div>
      </section>

      <section className="dashboard-executive-band dashboard-summary-band workspace-kpi-band">
        <article>
          <span>Oportunidades visibles</span>
          <strong>{tenders.total}</strong>
        </article>
        <article>
          <span>Cierres cercanos</span>
          <strong>{urgentDeadlines}</strong>
        </article>
        <article>
          <span>En seguimiento</span>
          <strong>{inPipeline}</strong>
        </article>
        <article>
          <span>Alertas activas</span>
          <strong>{alerts.length}</strong>
        </article>
      </section>

      <section className="panel dashboard-hero-board workspace-briefing-panel">
        <div className="results-header">
          <div>
            <span className="section-kicker">Briefing</span>
            <h2>Qué mirar hoy</h2>
          </div>
          <p>Usá esta vista para decidir qué entra al pipeline y qué necesita revisión inmediata.</p>
        </div>
        <WorkspaceBoardIllustration />
      </section>

      <section className="dashboard-focus-grid">
        <article className="panel dispatch-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Prioridad</span>
              <h2>Primero revisar</h2>
            </div>
            <p>Ordenado por relevancia y urgencia.</p>
          </div>

          <div className="decision-rows">
            {topPriority.map((item, index) => (
              <article key={item.id} className="decision-row decision-row-dense">
                <div className="decision-row-head">
                  <span className="mini-pill">0{index + 1}</span>
                  <span className="source-chip">{item.source.name}</span>
                  <span className="badge tone-calm">{deadlineLabel(item.deadline_date)}</span>
                  {item.states[0] ? <span className="badge">{formatStateLabel(item.states[0].state)}</span> : null}
                </div>
                <strong>{item.title}</strong>
                <p>{item.matches[0]?.reasons_json?.summary?.[0] ?? "Revisar fit comercial y documentación."}</p>
                <div className="decision-row-footer">
                  <span className="muted">{item.organization ?? "Sin organismo"} · {item.jurisdiction ?? "Sin jurisdicción"}</span>
                  <Link href={`/tenders/${item.id}`} className="linkish">
                    Abrir dossier
                  </Link>
                </div>
              </article>
            ))}
          </div>
        </article>

        <article className="panel dispatch-panel dashboard-side-rail">
          <div className="results-header">
            <div>
              <span className="section-kicker">Alertas</span>
              <h2>Actividad reciente</h2>
            </div>
          </div>
          <div className="alert-stack">
            {visibleAlerts.length ? (
              visibleAlerts.map((alert) => (
                <article key={alert.id} className="alert-row">
                  <span className="mini-pill">{alert.alert_type.replaceAll("_", " ")}</span>
                  <strong>Tender #{alert.tender_id}</strong>
                  <p>{new Date(alert.scheduled_for).toLocaleString("es-AR")}</p>
                </article>
              ))
            ) : (
              <p className="muted">Todavía no hay alertas activas para mostrar.</p>
            )}
          </div>

          <div className="detail-note-card">
            <span className="section-kicker">Siguiente paso</span>
            <p>Mandá a seguimiento lo que ya decidiste trabajar.</p>
            <Link href="/saved" className="linkish">
              Ir al pipeline
            </Link>
          </div>
        </article>
      </section>

      <section className="layout-grid dashboard-main-grid">
        <FilterPanel
          selectedJurisdiction={params.jurisdiction}
          selectedMinScore={params.min_score}
          selectedSource={params.source}
          sources={sources}
        />
        <TendersTable tenders={tenders.items} total={tenders.total} />
      </section>
    </PageShell>
  );
}
