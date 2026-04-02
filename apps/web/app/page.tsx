import Link from "next/link";

import {
  HeroTechnicalIllustration,
  ProcessDiagramIllustration,
  ProofRibbonIllustration,
} from "../components/landing-ornaments";
import { SiteHeader } from "../components/site-header";
import { fetchAlerts, fetchSources, fetchTenders } from "../lib/api";
import { getCurrentUserFromSession } from "../lib/session";

export default async function LandingPage() {
  const [sources, tenders, alerts, currentUser] = await Promise.all([
    fetchSources(),
    fetchTenders({ min_score: "60" }),
    fetchAlerts(),
    getCurrentUserFromSession(),
  ]);

  const featured = tenders.items.slice(0, 3);
  const sourceNames = sources.map((source) => source.name).join(" · ");
  const urgent = featured.filter((item) => {
    if (!item.deadline_date) return false;
    return new Date(item.deadline_date).getTime() - Date.now() < 1000 * 60 * 60 * 24 * 10;
  }).length;

  return (
    <main className="page-shell landing-shell">
      <SiteHeader section="landing" currentUserName={currentUser?.full_name} />

      <section className="landing-hero landing-hero-refined">
        <div className="hero-copy">
          <span className="eyebrow">Licitaciones IA · Argentina</span>
          <h1>La forma sobria de convertir licitaciones dispersas en una operación comercial clara.</h1>
          <p className="hero-lead">
            Licitaciones IA reúne fuentes públicas, procesa documentos, explica relevancia y ordena una cola de
            decisión. El resultado no es más información: es menos ruido y mejores prioridades.
          </p>

          <div className="hero-actions">
            <Link href="/dashboard" className="button-primary">
              Entrar al producto
            </Link>
            <Link href="#about" className="button-secondary">
              Entender cómo funciona
            </Link>
          </div>

          <div className="hero-inline-metrics">
            <article>
              <span>Fuentes activas</span>
              <strong>{sources.length}</strong>
            </article>
            <article>
              <span>Alertas vigentes</span>
              <strong>{alerts.length}</strong>
            </article>
            <article>
              <span>Prioridad alta</span>
              <strong>{tenders.total}</strong>
            </article>
          </div>
        </div>

        <div className="hero-board">
          <div className="board-frame refined-board">
            <HeroTechnicalIllustration />
            <div className="board-topline">
              <span className="mini-pill">Instancia local persistida</span>
              <span className="mini-pill mini-pill-warm">{urgent} cierres cercanos</span>
            </div>

            <div className="board-score">
              <div>
                <small>Vista principal</small>
                <strong>Una cola de decisión</strong>
              </div>
              <p>
                Score, urgencia, fuente y estado operativo en una sola lectura. La decisión empieza acá, no en una
                cadena de pestañas abiertas.
              </p>
            </div>

            <div className="board-list">
              {featured.map((item) => (
                <article key={item.id} className="opportunity-card">
                  <div className="opportunity-head">
                    <span className="source-chip">{item.source.name}</span>
                    <span className="score-chip">Score {Math.round(Number(item.matches[0]?.score ?? 0))}</span>
                  </div>
                  <strong>{item.title}</strong>
                  <p>{item.organization ?? "Sin organismo"} · {item.jurisdiction ?? "Sin jurisdicción"}</p>
                </article>
              ))}
            </div>
          </div>
        </div>
      </section>

      <section className="proof-strip">
        <article className="proof-card">
          <ProofRibbonIllustration />
          <span className="section-kicker">Resultado</span>
          <strong>Menos fricción operativa.</strong>
          <p>La revisión manual de portales dispersos se reemplaza por una sola cola priorizada y trazable.</p>
        </article>
        <article className="proof-card">
          <span className="section-kicker">Criterio</span>
          <strong>Relevancia que se puede explicar.</strong>
          <p>La plataforma deja razones visibles, fechas críticas y evidencia para defender por qué avanzar o no.</p>
        </article>
        <article className="proof-card">
          <span className="section-kicker">Cobertura</span>
          <strong>{sourceNames}</strong>
          <p>Fuentes reales ya persistidas, con una estructura lista para sumar conectores sin romper la operación.</p>
        </article>
      </section>

      <section className="experience-strip">
        <article className="experience-card experience-card-dark">
          <span className="section-kicker">Vista 1</span>
          <h3>Cola priorizada</h3>
          <p>Una lectura de negocio: qué aparece primero, por qué y con cuánto margen real.</p>
          <div className="experience-mini-board">
            {featured.slice(0, 2).map((item) => (
              <div key={item.id} className="experience-mini-row">
                <span>{item.title}</span>
                <span className="badge tone-warning">Score {Math.round(Number(item.matches[0]?.score ?? 0))}</span>
              </div>
            ))}
          </div>
        </article>
        <article className="experience-card">
          <ProcessDiagramIllustration />
          <span className="section-kicker">Vista 2</span>
          <h3>Dossier con contexto</h3>
          <p>Documentos, resumen, matching y deadlines en una misma ficha para decidir sin desorden.</p>
        </article>
        <article className="experience-card">
          <span className="section-kicker">Vista 3</span>
          <h3>Operación trazable</h3>
          <p>Fuentes, corridas, perfil de empresa y alertas visibles para no depender de intuición ni memoria.</p>
        </article>
      </section>

      <section className="about-grid" id="about">
        <article className="feature-panel feature-panel-dark">
          <span className="section-kicker">Qué es</span>
          <h2>Un sistema de criterio para compras públicas.</h2>
          <p>
            Centraliza licitaciones, procesa documentos, resume lo relevante, compara contra un perfil de empresa y
            deja un flujo simple para evaluar, guardar o descartar. La fuente de verdad es el dashboard, no una
            combinación de mails, portales y planillas.
          </p>
        </article>

        <article className="feature-panel feature-panel-light">
          <span className="section-kicker">Recorrido</span>
          <ol className="timeline-list">
            <li>Se registran fuentes y se ejecutan corridas trazables.</li>
            <li>Se descargan documentos y se obtiene texto usable.</li>
            <li>Se prioriza por score, comprador, jurisdicción y tiempo remanente.</li>
            <li>El equipo decide desde una cola con workflow y alertas.</li>
          </ol>
        </article>
      </section>

      <section className="why-grid">
        <article className="why-card">
          <span className="section-kicker">Para quién</span>
          <h3>Equipos comerciales que necesitan foco</h3>
          <p>Para áreas que no pueden darse el lujo de revisar todo, pero sí necesitan detectar lo correcto a tiempo.</p>
        </article>
        <article className="why-card">
          <span className="section-kicker">Valor visible</span>
          <h3>Entendible en minutos</h3>
          <p>La propuesta se ve en pantalla: prioridad, razones, deadlines, documentos y seguimiento mínimo.</p>
        </article>
        <article className="why-card">
          <span className="section-kicker">Gobierno</span>
          <h3>Control sobre la operación</h3>
          <p>La instancia deja ver fuentes, corridas, alertas y estado general sin esconder la trastienda del sistema.</p>
        </article>
      </section>

      <section className="featured-grid">
        {featured.map((item) => (
          <article key={item.id} className="featured-tender">
            <div className="featured-meta">
              <span className="source-chip">{item.source.name}</span>
              <span className="mini-pill">#{item.id}</span>
            </div>
            <h3>{item.title}</h3>
            <p>{item.matches[0]?.reasons_json?.summary?.[0] ?? "Sin explicación generada todavía."}</p>
            <div className="featured-footer">
              <span>{item.organization ?? "Sin organismo"}</span>
              <Link href={`/tenders/${item.id}`}>Abrir detalle</Link>
            </div>
          </article>
        ))}
      </section>

      <section className="cta-band">
        <div>
          <span className="section-kicker">Siguiente paso</span>
          <h2>La propuesta se termina de entender cuando la cola ya está ordenada.</h2>
          <p>Entrá al dashboard y mirá qué aparece primero, por qué aparece y qué conviene hacer con eso.</p>
        </div>
        <Link href="/dashboard" className="button-primary">
          Entrar al dashboard
        </Link>
      </section>
    </main>
  );
}
