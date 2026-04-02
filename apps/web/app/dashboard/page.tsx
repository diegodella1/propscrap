import { FilterPanel } from "../../components/filter-panel";
import { SiteHeader } from "../../components/site-header";
import { TendersTable } from "../../components/tenders-table";
import { fetchAlerts, fetchSources, fetchTenders } from "../../lib/api";
import { getCurrentUserFromSession } from "../../lib/session";

type Props = {
  searchParams: Promise<{
    source?: string;
    jurisdiction?: string;
    min_score?: string;
  }>;
};

export default async function DashboardPage({ searchParams }: Props) {
  const params = await searchParams;
  const [sources, tenders, alerts, currentUser] = await Promise.all([
    fetchSources(),
    fetchTenders({
      source: params.source,
      jurisdiction: params.jurisdiction,
      min_score: params.min_score,
    }),
    fetchAlerts(),
    getCurrentUserFromSession(),
  ]);

  const highRelevance = tenders.items.filter((item) => Number(item.matches[0]?.score ?? 0) >= 60).length;
  const urgentDeadlines = tenders.items.filter((item) => {
    if (!item.deadline_date) return false;
    return new Date(item.deadline_date).getTime() - Date.now() < 1000 * 60 * 60 * 24 * 7;
  }).length;
  const topPriority = [...tenders.items]
    .sort((a, b) => Number(b.matches[0]?.score ?? 0) - Number(a.matches[0]?.score ?? 0))
    .slice(0, 3);
  const visibleAlerts = alerts.slice(0, 4);

  function scoreTone(score: number) {
    if (score >= 75) return "tone-success";
    if (score >= 50) return "tone-warning";
    return "tone-muted";
  }

  function alertTone(type: string) {
    if (type.includes("24h")) return "tone-danger";
    if (type.includes("3d") || type.includes("7d")) return "tone-warning";
    return "tone-calm";
  }

  function formatAlertType(value: string) {
    if (value === "new_relevant") return "Nueva relevante";
    if (value === "deadline_7d") return "Cierre en 7 días";
    if (value === "deadline_3d") return "Cierre en 3 días";
    if (value === "deadline_24h") return "Cierre en 24h";
    return value;
  }

  function formatStateLabel(value: string | null | undefined) {
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
        return value ?? "Sin estado";
    }
  }

  function deadlineTone(value: string | null) {
    if (!value) return "tone-neutral";
    const diff = new Date(value).getTime() - Date.now();
    if (diff < 0) return "tone-danger";
    if (diff < 1000 * 60 * 60 * 24 * 3) return "tone-danger";
    if (diff < 1000 * 60 * 60 * 24 * 7) return "tone-warning";
    return "tone-calm";
  }

  function deadlineLabel(value: string | null) {
    if (!value) return "Sin fecha";
    const diff = new Date(value).getTime() - Date.now();
    if (diff < 0) return "Vencida";
    if (diff < 1000 * 60 * 60 * 24) return "Cierra en 24h";
    if (diff < 1000 * 60 * 60 * 24 * 3) return "Cierra en 3 días";
    if (diff < 1000 * 60 * 60 * 24 * 7) return "Cierra en 7 días";
    return "Con margen";
  }

  return (
    <main className="page-shell">
      <SiteHeader section="dashboard" currentUserName={currentUser?.full_name} />

      <section className="hero hero-app">
        <div>
          <span className="eyebrow">Dashboard operativo</span>
          <h1>Qué merece atención ahora y qué no.</h1>
        </div>
        <p>
          Esta es la vista principal del producto. Cada oportunidad combina score, deadline, fuente y estado para que
          el equipo pueda decidir sin saltar entre portales y documentos dispersos.
        </p>
      </section>

      <section className="signal-grid">
        <article className="signal-card signal-accent">
          <span className="signal-label">Tenders visibles</span>
          <strong>{tenders.total}</strong>
          <p>Normalizados y listos para revisión comercial.</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Alta relevancia</span>
          <strong>{highRelevance}</strong>
          <p>Con score 60+ según el perfil demo.</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Vencen pronto</span>
          <strong>{urgentDeadlines}</strong>
          <p>Con cierre dentro de los próximos 7 días.</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Alerts activos</span>
          <strong>{alerts.length}</strong>
          <p>Recordatorios y oportunidades nuevas listos para seguimiento.</p>
        </article>
      </section>

      <section className="dispatch-grid">
        <article className="panel dispatch-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Prioridad</span>
              <h2>Qué conviene poner primero sobre la mesa</h2>
            </div>
            <p>Los mejores casos combinan afinidad comercial, comprador relevante y tiempo todavía utilizable.</p>
          </div>

          <div className="priority-list">
            {topPriority.map((item, index) => (
              <article key={item.id} className="priority-item">
                <div className="priority-rank">0{index + 1}</div>
                <div className="priority-body">
                  <div className="meta">
                    <span className="source-chip">{item.source.name}</span>
                    <span className={`score-chip badge ${scoreTone(Math.round(Number(item.matches[0]?.score ?? 0)))}`}>
                      Score {Math.round(Number(item.matches[0]?.score ?? 0))}
                    </span>
                    <span className={`badge ${deadlineTone(item.deadline_date)}`}>{deadlineLabel(item.deadline_date)}</span>
                    {item.states[0] ? (
                      <span className="badge workflow-chip tone-calm">{formatStateLabel(item.states[0].state)}</span>
                    ) : null}
                  </div>
                  <h3>{item.title}</h3>
                  <p>{item.matches[0]?.reasons_json?.summary?.[0] ?? "Todavía no hay explicación sintetizada."}</p>
                </div>
              </article>
            ))}
          </div>
        </article>

        <article className="panel dispatch-panel dispatch-alerts">
          <div className="results-header">
            <div>
              <span className="section-kicker">Alertas</span>
              <h2>Eventos que no conviene dejar pasar</h2>
            </div>
          </div>

          <div className="alert-stack">
            {visibleAlerts.map((alert) => (
              <article key={alert.id} className={`alert-row ${alertTone(alert.alert_type)}`}>
                <span className={`mini-pill ${alertTone(alert.alert_type)}`}>{formatAlertType(alert.alert_type)}</span>
                <strong>Tender #{alert.tender_id}</strong>
                <p>{new Date(alert.scheduled_for).toLocaleString("es-AR")}</p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <section className="layout-grid">
        <FilterPanel
          selectedJurisdiction={params.jurisdiction}
          selectedMinScore={params.min_score}
          selectedSource={params.source}
          sources={sources}
        />
        <TendersTable tenders={tenders.items} total={tenders.total} />
      </section>
    </main>
  );
}
