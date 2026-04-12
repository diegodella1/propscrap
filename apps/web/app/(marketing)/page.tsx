import Link from "next/link";

import { PageShell } from "../../components/layout/page-shell";
import { ExecutiveControlIllustration, WorkspaceBoardIllustration } from "../../components/landing-ornaments";
import { SiteHeader } from "../../components/site-header";
import { fetchSources, fetchTenders } from "../../lib/api";
import { getCurrentUserFromSession } from "../../lib/session";

function formatDeadlineLabel(value: string | null) {
  if (!value) return "Sin cierre informado";
  const diff = new Date(value).getTime() - Date.now();
  if (diff < 1000 * 60 * 60 * 24) return "Cierra en 24h";
  if (diff < 1000 * 60 * 60 * 24 * 3) return "Cierra en 3 días";
  if (diff < 1000 * 60 * 60 * 24 * 7) return "Cierra esta semana";
  return "Con margen";
}

export default async function LandingPage() {
  const [sources, tenders, currentUser] = await Promise.all([
    fetchSources(),
    fetchTenders({ min_score: "50" }),
    getCurrentUserFromSession(),
  ]);

  const featured = tenders.items.slice(0, 3);
  const urgentCount = featured.filter((item) => {
    if (!item.deadline_date) return false;
    return new Date(item.deadline_date).getTime() - Date.now() < 1000 * 60 * 60 * 24 * 7;
  }).length;
  const sourceLabels = sources.slice(0, 4).map((source) => source.name);
  const isLoggedIn = Boolean(currentUser);

  return (
    <PageShell variant="marketing" className="landing-shell">
      <SiteHeader
        section="landing"
        currentUserName={currentUser?.full_name}
        currentUserRole={currentUser?.role}
      />

      <section
        className={`landing-hero landing-hero-refined landing-masterhead ${
          isLoggedIn ? "landing-masterhead-operator" : "landing-masterhead-public"
        }`}
      >
        <div className="hero-copy">
          <span className="eyebrow">Plataforma para proveedores del Estado</span>
          <h1>
            {isLoggedIn
              ? "La operación comercial de licitaciones, en una sola vista."
              : "La infraestructura operativa para empresas que venden al Estado."}
          </h1>
          <p className="hero-lead">
            {isLoggedIn
              ? "EasyTaciones concentra discovery, scoring, seguimiento y próximas acciones para que el equipo decida con contexto y ejecute sin dispersión."
              : "EasyTaciones reemplaza portales, PDFs, planillas y memoria informal por un sistema claro. La empresa entra por CUIT, se arma el perfil comercial y el equipo trabaja con prioridades, fechas y alertas."}
          </p>
          <div className="hero-actions">
            <Link href="/contact" className="button-primary">
              Hablar con Ventas
            </Link>
            <Link href={currentUser ? "/dashboard" : "/signup"} className="button-secondary">
              {currentUser ? "Abrir Workspace" : "Registrar Empresa"}
            </Link>
            <Link href="/about" className="button-secondary">
              Ver Cómo Funciona
            </Link>
          </div>
          {isLoggedIn ? (
            <div className="hero-inline-metrics">
              <article>
                <span>Fuentes activas</span>
                <strong>{sources.length}</strong>
              </article>
              <article>
                <span>Oportunidades visibles</span>
                <strong>{tenders.total}</strong>
              </article>
              <article>
                <span>Cierres cercanos</span>
                <strong>{urgentCount}</strong>
              </article>
            </div>
          ) : (
            <div className="hero-inline-metrics hero-inline-splash">
              <article>
                <span>Paso 1</span>
                <strong>Registro por CUIT</strong>
                <p>Alta legal y perfil inicial en el primer paso.</p>
              </article>
              <article>
                <span>Paso 2</span>
                <strong>Discovery priorizado</strong>
                <p>Una sola vista con fit, contexto y fecha.</p>
              </article>
              <article>
                <span>Paso 3</span>
                <strong>Seguimiento sin memoria informal</strong>
                <p>Pipeline, notas y alertas con trazabilidad.</p>
              </article>
            </div>
          )}
        </div>

        <div className="hero-board hero-board-premium">
          <div className="board-frame refined-board">
          <div className="board-topline">
              <span className="mini-pill">{isLoggedIn ? "Workspace activo" : "Entrada por CUIT"}</span>
              <span className="mini-pill mini-pill-warm">{isLoggedIn ? "Seguimiento trazable" : "Operación ordenada"}</span>
            </div>

            <ExecutiveControlIllustration />

            <div className="board-score">
              <div>
                <small>{isLoggedIn ? "Resultado operativo" : "Propuesta de valor"}</small>
                <strong>{isLoggedIn ? "Menos ruido. Más foco. Mejor ejecución." : "La empresa entra por CUIT. El equipo opera con criterio."}</strong>
              </div>
              <p>
                {isLoggedIn
                  ? "La operación deja de vivir entre tabs, PDFs y planillas y pasa a una superficie única con prioridad, fecha, estado y próxima acción."
                  : "La propuesta no es mostrar más portales. Es bajar desorden y darle al equipo una lectura común de qué apareció, qué importa y qué hay que seguir."}
              </p>
            </div>

            <div className="decision-rows">
              {isLoggedIn
                ? featured.map((item) => (
                    <article key={item.id} className="decision-row">
                      <div className="decision-row-head">
                        <span className="source-chip">{item.source.name}</span>
                        <span className="badge tone-calm">{formatDeadlineLabel(item.deadline_date)}</span>
                      </div>
                      <strong>{item.title}</strong>
                      <p>
                        {item.matches[0]?.reasons_json?.summary?.[0] ??
                          "Aparece ordenada con contexto suficiente para decidir si vale moverla."}
                      </p>
                    </article>
                  ))
                : [
                    {
                      key: "cuit",
                      label: "Paso 1",
                      title: "La empresa entra por CUIT.",
                      copy: "Se valida la identidad legal y se arma una base inicial.",
                    },
                    {
                      key: "match",
                      label: "Paso 2",
                      title: "El sistema ordena el discovery.",
                      copy: "Cada oportunidad aparece con score, fecha y motivo de match.",
                    },
                    {
                      key: "followup",
                      label: "Paso 3",
                      title: "El equipo sigue sin perderse.",
                      copy: "La licitación pasa a pipeline con alertas y próxima acción visible.",
                    },
                  ].map((item) => (
                    <article key={item.key} className="decision-row">
                      <div className="decision-row-head">
                        <span className="source-chip">{item.label}</span>
                        <span className="badge tone-calm">Splash pública</span>
                      </div>
                      <strong>{item.title}</strong>
                      <p>{item.copy}</p>
                    </article>
                  ))}
            </div>
          </div>
        </div>
      </section>

      <section className="ops-proof-grid landing-proof-grid">
        <article className="proof-card">
          <span className="section-kicker">Problema</span>
          <h2>Buscar no es operar.</h2>
          <p>Portales, pliegos y planillas rompen continuidad y criterio comercial.</p>
        </article>
        <article className="proof-card">
          <span className="section-kicker">Solución</span>
          <h2>Una sola superficie operativa.</h2>
          <p>Fuentes, oportunidades y seguimiento entran en la misma lógica.</p>
        </article>
        <article className="proof-card">
          <span className="section-kicker">Resultado</span>
          <h2>Menos pérdida por timing.</h2>
          <p>Más claridad sobre qué mover hoy y qué sostener en seguimiento.</p>
        </article>
      </section>

      <section className="landing-system-stage">
        <div className="results-header landing-system-header">
          <div>
            <span className="section-kicker">Sistema</span>
            <h2>Una herramienta para pasar de búsqueda manual a seguimiento ordenado.</h2>
          </div>
          <p>
            El valor está en bajar ruido, fijar criterio y sostener la ejecución con contexto compartido.
          </p>
        </div>

        <div className="landing-system-grid">
          <article className="panel landing-system-copy">
            <span className="section-kicker">Vista operativa</span>
            <h3>Inbox, calendario y pipeline en una misma superficie.</h3>
            <p>
              Cada oportunidad aparece con motivo de match, deadline, estado y siguiente acción. No hay que perseguir
              contexto entre herramientas.
            </p>
            <div className="landing-system-points">
              <article>
                <strong>Entrada</strong>
                <p>Fuentes, APIs, sitios y documentos se vuelven una sola cola.</p>
              </article>
              <article>
                <strong>Decisión</strong>
                <p>La empresa ve por qué una licitación importa y decide rápido si seguirla.</p>
              </article>
              <article>
                <strong>Ejecución</strong>
                <p>La oportunidad pasa a seguimiento con responsables, notas y alertas.</p>
              </article>
            </div>
          </article>

          <article className="panel landing-system-diagram">
            <WorkspaceBoardIllustration />
          </article>
        </div>
      </section>

      <section className="editorial-grid landing-editorial-grid">
        <article className="editorial-callout editorial-callout-dark">
          <span className="section-kicker">Oferta</span>
          <h2>No vendemos scraping. Vendemos orden operativo.</h2>
          <p>El diferencial está en transformar información dispersa en un sistema de trabajo para empresas proveedoras.</p>
        </article>

        <article className="editorial-callout">
          <span className="section-kicker">Cobertura inicial</span>
          <h2>Una base multi-fuente lista para crecer.</h2>
          <p>{sourceLabels.join(" · ") || "Fuentes persistidas y listas para administrarse desde la plataforma."}</p>
        </article>
      </section>

      <section className="workspace-preview-grid landing-experience-grid">
        <article className="experience-card experience-card-dark">
          <span className="section-kicker">Para la empresa</span>
          <h3>Discovery, pipeline y alertas en un mismo lugar.</h3>
          <p>La empresa entra por CUIT y empieza a trabajar con una base inicial ya ordenada.</p>
        </article>
        <article className="experience-card">
          <span className="section-kicker">Para el equipo</span>
          <h3>Un criterio compartido</h3>
          <p>Todos miran la misma oportunidad con el mismo estado y el mismo contexto.</p>
        </article>
        <article className="experience-card">
          <span className="section-kicker">Para la gestión</span>
          <h3>Menos fricción y menos pérdida.</h3>
          <p>Saca a la empresa del desorden manual y la lleva a una operación mucho más gobernable.</p>
        </article>
      </section>
    </PageShell>
  );
}
