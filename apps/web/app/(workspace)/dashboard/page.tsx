import Link from "next/link";
import { redirect } from "next/navigation";

import { FilterPanel } from "../../../components/filter-panel";
import { WorkspaceBoardIllustration } from "../../../components/landing-ornaments";
import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";
import { TendersTable } from "../../../components/tenders-table";
import { fetchAlerts, fetchMySourceAccess, fetchSavedTenders, fetchSources, fetchTenders } from "../../../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession, getMyCompanyProfileFromSession } from "../../../lib/session";

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

  const [sources, tenders, alerts, profile, saved, sourceAccess] = await Promise.all([
    fetchSources(),
    fetchTenders({
      source: params.source,
      jurisdiction: params.jurisdiction,
      min_score: params.min_score,
    }),
    fetchAlerts(cookieHeader || undefined),
    getMyCompanyProfileFromSession(),
    fetchSavedTenders(cookieHeader || undefined).catch(() => null),
    fetchMySourceAccess(cookieHeader || undefined).catch(() => null),
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
  const alertChannels = currentUser.alert_preferences_json?.channels ?? ["dashboard"];
  const alertChannelReady =
    alertChannels.includes("email") ||
    (alertChannels.includes("whatsapp") && Boolean(currentUser.whatsapp_number)) ||
    (alertChannels.includes("telegram") && Boolean(currentUser.telegram_chat_id));
  const profileReady = Boolean(
    profile?.company_description?.trim() &&
      ((profile?.include_keywords?.length ?? 0) > 0 ||
        (profile?.preferred_buyers?.length ?? 0) > 0 ||
        (profile?.jurisdictions?.length ?? 0) > 0),
  );
  const savedCount = saved?.total ?? 0;
  const activationSteps = [
    {
      label: "Semana 1",
      title: "Perfil comercial",
      body: "Dejá claro qué vende la empresa, a quién le vende y qué vale filtrar.",
      href: "/company-profile",
      cta: "Completar perfil",
      complete: profileReady,
    },
    {
      label: "Semana 2",
      title: "Primera cartera",
      body: "Guardá licitaciones relevantes para que el pipeline deje de ser abstracto.",
      href: "/dashboard",
      cta: "Explorar oportunidades",
      complete: savedCount > 0,
    },
    {
      label: "Semana 3",
      title: "Alertas reales",
      body: "Sacá el flujo del navegador y validá email, WhatsApp o Telegram.",
      href: "/mi-cuenta",
      cta: "Configurar alertas",
      complete: alertChannelReady,
    },
    {
      label: "Semana 4",
      title: "Rutina de seguimiento",
      body: "Revisá el pipeline todos los días y dejá notas o cambios de estado.",
      href: "/saved",
      cta: "Abrir pipeline",
      complete: savedCount > 0,
    },
  ];
  const completedActivation = activationSteps.filter((step) => step.complete).length;
  const nextActivationStep = activationSteps.find((step) => !step.complete) ?? activationSteps[activationSteps.length - 1];

  return (
    <PageShell variant="workspace" className="workspace-shell page-screen page-screen--dashboard">
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
        <article>
          <span>Fuentes efectivas</span>
          <strong>{sourceAccess?.effective_source_ids.length ?? 0}</strong>
        </article>
      </section>

      <section className="ops-priority-grid dashboard-activation-grid">
        <article className="panel ops-priority-card ops-priority-card-strong">
          <span className="section-kicker">Demo 30 días</span>
          <h3>Objetivo: que el equipo cambie su rutina, no solo vea una interfaz.</h3>
          <p>
            La prueba se vuelve valiosa cuando la empresa carga su criterio comercial, guarda oportunidades reales y empieza a seguir fechas desde la plataforma.
          </p>
        </article>
        <article className="panel ops-priority-card">
          <span className="section-kicker">Progreso</span>
          <h3>{completedActivation}/4 hitos cumplidos</h3>
          <p>{nextActivationStep.complete ? "La base de uso ya está armada." : `Siguiente paso recomendado: ${nextActivationStep.title}.`}</p>
        </article>
        <article className="panel ops-priority-card">
          <span className="section-kicker">Acción siguiente</span>
          <h3>{nextActivationStep.title}</h3>
          <p>{nextActivationStep.body}</p>
          <Link href={nextActivationStep.href} className="linkish">
            {nextActivationStep.cta}
          </Link>
        </article>
      </section>

      <section className="panel workspace-briefing-panel">
        <div className="results-header">
          <div>
            <span className="section-kicker">Plan de activación</span>
            <h2>Qué tendría que pasar en la demo para que el producto se vuelva indispensable</h2>
          </div>
          <p>No hace falta usar todo el sistema el primer día. Sí hace falta que el equipo vea valor real en menos tiempo y menos desorden.</p>
        </div>
        <div className="decision-rows">
          {activationSteps.map((step) => (
            <article key={step.label} className="decision-row decision-row-dense">
              <div className="decision-row-head">
                <span className="source-chip">{step.label}</span>
                <span className={`badge ${step.complete ? "tone-success" : "tone-calm"}`}>
                  {step.complete ? "Cumplido" : "Pendiente"}
                </span>
              </div>
              <strong>{step.title}</strong>
              <p>{step.body}</p>
              <div className="decision-row-footer">
                <span className="muted">{step.complete ? "Ya está cubierto en esta cuenta." : "Conviene resolverlo para sostener la prueba."}</span>
                <Link href={step.href} className="linkish">
                  {step.cta}
                </Link>
              </div>
            </article>
          ))}
        </div>
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
            {topPriority.length ? (
              topPriority.map((item, index) => (
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
              ))
            ) : (
              <div className="workspace-empty-state workspace-empty-state-strong">
                <strong>Todavía no hay oportunidades priorizadas.</strong>
                <p>Si el discovery quedó vacío, el siguiente ajuste razonable es mejorar el perfil comercial para afinar matching y cobertura.</p>
                <Link href="/company-profile" className="button-secondary">
                  Ajustar perfil comercial
                </Link>
              </div>
            )}
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

      <section className="panel workspace-briefing-panel">
        <div className="results-header">
          <div>
            <span className="section-kicker">Fuentes y scoring</span>
            <h2>Cómo leer este top</h2>
          </div>
          <p>El score mezcla keywords, buyer, jurisdicción, sectores, frescura de publicación y cercanía del cierre. No reemplaza criterio comercial: ordena primero qué conviene revisar.</p>
        </div>
        <div className="admin-overview-grid">
          <article className="panel admin-overview-card">
            <span className="section-kicker">Fuentes</span>
            <h3>Inventario efectivo</h3>
            <p>
              {sourceAccess
                ? `Modo ${sourceAccess.source_scope_mode === "all_active" ? "todas las activas" : "custom"} · ${sourceAccess.effective_source_ids.length} fuentes efectivas para esta empresa.`
                : "El listado no muestra todo lo que existe en plataforma, sino solo las fuentes globalmente activas y habilitadas para esta empresa."}
            </p>
          </article>
          <article className="panel admin-overview-card">
            <span className="section-kicker">Scoring</span>
            <h3>Orden de revisión</h3>
            <p>Un score alto sube por fit comercial real; baja si aparecen exclusiones, si la oportunidad está vencida o si el cierre está demasiado encima.</p>
          </article>
          <article className="panel admin-overview-card">
            <span className="section-kicker">Visibilidad</span>
            <h3>Quién define el alcance</h3>
            <p>
              Superadmin activa fuentes a nivel plataforma. El admin de empresa decide si hereda todas las activas o si trabaja con una selección custom para su equipo.
            </p>
          </article>
        </div>
      </section>
    </PageShell>
  );
}
