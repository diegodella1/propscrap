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
  const sourceLabels = Array.from(
    new Set(
      sources
        .map((source) => source.name.trim())
        .filter((name) => name.length > 0)
        .filter((name) => !/(^|\b)(qa|test|demo|updated)(\b|$)/i.test(name)),
    ),
  ).slice(0, 4);
  const isLoggedIn = Boolean(currentUser);

  return (
    <PageShell variant="marketing" className="landing-shell page-screen page-screen--home">
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
              ? "La mesa de control comercial de tus licitaciones."
              : "La forma seria de operar licitaciones sin portales, PDFs y planillas dispersas."}
          </h1>
          <p className="hero-lead">
            {isLoggedIn
              ? "EasyTaciones concentra discovery, scoring, seguimiento y próximas acciones para que el equipo trabaje sobre una sola lectura de prioridad, fecha y próximo paso."
              : "EasyTaciones convierte un proceso manual y fragmentado en una herramienta de trabajo. La empresa entra por CUIT, el perfil se completa con criterio comercial y el equipo opera sobre oportunidades priorizadas."}
          </p>
          <div className="hero-actions">
            {currentUser ? (
              <>
                <Link href="/dashboard" className="button-primary">
                  Abrir workspace
                </Link>
                <Link href="/saved" className="button-secondary">
                  Ver pipeline
                </Link>
              </>
            ) : (
              <>
                <Link href="/signup" className="button-primary">
                  Registrar empresa
                </Link>
                <Link href="/about" className="button-secondary">
                  Ver cómo funciona
                </Link>
              </>
            )}
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
                <span>Alta</span>
                <strong>Alta por CUIT</strong>
                <p>Identidad legal y base inicial en minutos.</p>
              </article>
              <article>
                <span>Discovery</span>
                <strong>Discovery priorizado</strong>
                <p>Una sola cola con score, motivo y cierre.</p>
              </article>
              <article>
                <span>Seguimiento</span>
                <strong>Seguimiento trazable</strong>
                <p>Pipeline, notas y alertas sin depender de memoria humana.</p>
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
                <small>{isLoggedIn ? "Resultado operativo" : "Resultado del sistema"}</small>
                <strong>{isLoggedIn ? "Menos ruido, más control y mejor timing." : "La empresa entra por CUIT. El equipo opera con criterio compartido."}</strong>
              </div>
              <p>
                {isLoggedIn
                  ? "La operación deja de vivir entre tabs, PDFs y planillas y pasa a una superficie única con prioridad, fecha, estado y próxima acción."
                  : "La propuesta no es mostrar más portales. Es darle al equipo una lectura común de qué apareció, qué importa y qué vale seguir hoy."}
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

      <section className="ops-proof-grid landing-proof-grid surface-band">
        <article className="proof-card">
          <span className="section-kicker">Problema</span>
          <h2>Buscar no es operar.</h2>
          <p>Portales, pliegos y planillas rompen continuidad, timing y criterio comercial.</p>
        </article>
        <article className="proof-card">
          <span className="section-kicker">Solución</span>
          <h2>Una sola superficie de trabajo.</h2>
          <p>Fuentes, oportunidades, pipeline y alertas entran en la misma lógica operativa.</p>
        </article>
        <article className="proof-card">
          <span className="section-kicker">Resultado</span>
          <h2>Menos pérdida por timing.</h2>
          <p>Más claridad sobre qué mover hoy, qué descartar y qué sostener en seguimiento.</p>
        </article>
      </section>

      <section className="landing-system-stage surface-band surface-band--alt">
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
            <h3>Inbox, prioridades y pipeline en una misma superficie.</h3>
            <p>
              Cada oportunidad aparece con motivo de match, deadline, estado y siguiente acción. La lectura del equipo deja de estar repartida entre herramientas.
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
          <h2>No vendemos scraping. Vendemos control operativo.</h2>
          <p>El diferencial está en transformar información dispersa en un sistema de trabajo serio para empresas proveedoras.</p>
        </article>

        <article className="editorial-callout">
          <span className="section-kicker">Cobertura inicial</span>
          <h2>Una base multi-fuente lista para crecer.</h2>
          <p>
            {sourceLabels.join(" · ") ||
              "COMPR.AR · portales oficiales · boletines públicos · fuentes administradas desde la plataforma."}
          </p>
        </article>
      </section>

      <section className="workspace-preview-grid landing-experience-grid surface-band">
        <article className="experience-card experience-card-dark">
          <span className="section-kicker">Para la empresa</span>
          <h3>Discovery, pipeline y alertas en un mismo lugar.</h3>
          <p>La empresa entra por CUIT y empieza a trabajar con una base inicial ya ordenada y accionable.</p>
        </article>
        <article className="experience-card">
          <span className="section-kicker">Para el equipo</span>
          <h3>Un criterio compartido</h3>
          <p>Todos miran la misma oportunidad con el mismo score, el mismo estado y el mismo contexto.</p>
        </article>
        <article className="experience-card">
          <span className="section-kicker">Para la gestión</span>
          <h3>Menos fricción y menos pérdida.</h3>
          <p>Saca a la empresa del desorden manual y la lleva a una operación más gobernable y más defendible frente a cliente interno.</p>
        </article>
      </section>
    </PageShell>
  );
}
