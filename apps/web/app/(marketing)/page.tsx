import Link from "next/link";

import { PageShell } from "../../components/layout/page-shell";
import { WorkspaceBoardIllustration } from "../../components/landing-ornaments";
import { SiteHeader } from "../../components/site-header";
import { fetchSources, fetchTenders } from "../../lib/api";

export default async function LandingPage() {
  const [sources] = await Promise.all([
    fetchSources(),
    fetchTenders({ min_score: "50" }),
  ]);
  const sourceLabels = Array.from(
    new Set(
      sources
        .map((source) => source.name.trim())
        .filter((name) => name.length > 0)
        .filter((name) => !/(^|\b)(qa|test|demo|updated)(\b|$)/i.test(name)),
    ),
  ).slice(0, 4);

  return (
    <PageShell variant="marketing" className="landing-shell page-screen page-screen--home">
      <SiteHeader section="landing" audience="public" />

      <section className="landing-hero landing-hero-refined landing-masterhead landing-masterhead-public">
        <div className="hero-copy">
          <span className="eyebrow">Sistema operativo comercial para proveedores del Estado</span>
          <h1>Mostrá un producto claro, serio y accionable desde la primera pantalla.</h1>
          <p className="hero-lead">
            EasyTaciones convierte un proceso manual y fragmentado en una experiencia que se entiende rápido: alta por CUIT, fuentes gobernadas, discovery priorizado, seguimiento y alertas en una misma superficie.
          </p>
          <div className="landing-audience-strip">
            <span>Presentación comercial clara</span>
            <span>Demo de 30 días usable</span>
            <span>Sin ruido de sesión en páginas públicas</span>
          </div>
          <div className="hero-actions">
            <Link href="/contact" className="button-primary">
              Solicitar demo
            </Link>
            <Link href="/signup" className="button-secondary">
              Registrar empresa
            </Link>
          </div>
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
        </div>

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

        <div className="landing-system-grid landing-system-grid--wide">
          <article className="panel landing-system-diagram landing-system-diagram--wide">
            <div className="landing-system-diagram-copy">
              <span className="section-kicker">Vista operativa</span>
              <h3>Inbox, prioridades y pipeline en una misma superficie.</h3>
              <p>
                Cada oportunidad aparece con motivo de match, deadline, estado y siguiente acción. La lectura del equipo deja de estar repartida entre herramientas.
              </p>
            </div>
            <WorkspaceBoardIllustration />
          </article>
        </div>
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
