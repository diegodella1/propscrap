import Link from "next/link";

import { PageShell } from "../../components/layout/page-shell";
import { SiteHeader } from "../../components/site-header";
import { fetchSources } from "../../lib/api";

export default async function LandingPage() {
  const sources = await fetchSources();
  const activeSources = sources.filter((source) => source.is_active).length;
  const activeSourceNames = sources
    .filter((source) => source.is_active)
    .map((source) => source.name)
    .slice(0, 5);
  const remainingSources = Math.max(activeSources - activeSourceNames.length, 0);

  return (
    <PageShell variant="marketing" className="landing-shell page-screen page-screen--home">
      <SiteHeader section="landing" audience="public" />

      <section className="landing-minimal-hero">
        <div className="landing-minimal-copy">
          <span className="eyebrow">Sistema operativo comercial para proveedores del Estado</span>
          <h1>Un solo lugar para decidir qué licitación mirar, seguir y mover.</h1>
          <p className="landing-minimal-lead">
            EasyTaciones reemplaza portales, planillas y memoria suelta por una operación legible: alta por CUIT, top priorizado, pipeline y alertas en una interfaz que un cliente puede entender en minutos.
          </p>
          <div className="landing-hero-ticks">
            <span>Alta inicial en minutos</span>
            <span>Scoring con motivo y deadline</span>
            <span>Prueba usable por 30 días</span>
          </div>
          <div className="hero-actions">
            <Link href="/contact" className="button-primary">
              Solicitar demo
            </Link>
            <Link href="/signup" className="button-secondary">
              Registrar empresa
            </Link>
          </div>
        </div>

        <div className="landing-minimal-rail">
          <article className="landing-stat-card landing-stat-card-strong">
            <span>Top operativo</span>
            <strong>Discovery, seguimiento y alertas</strong>
            <p>La lectura principal arranca con criterio, estado y próxima acción.</p>
          </article>
          <div className="landing-stat-grid">
            <article className="landing-stat-card">
              <span>Fuentes activas</span>
              <strong>{activeSources}</strong>
              <p>
                {activeSourceNames.join(", ")}
                {remainingSources > 0 ? ` y ${remainingSources} más.` : "."}
              </p>
            </article>
            <article>
              <span>Gobierno</span>
              <strong>Superadmin + empresa</strong>
            </article>
            <article>
              <span>Canales</span>
              <strong>Dashboard, email, Telegram</strong>
            </article>
          </div>
        </div>
      </section>

      <section className="landing-operator-band">
        <div className="landing-operator-copy">
          <span className="section-kicker">Cómo se ordena</span>
          <h2>Menos búsqueda manual. Más criterio compartido.</h2>
          <p>
            La empresa entra por CUIT, el sistema consolida fuentes, ordena oportunidades por fit comercial y deja el seguimiento dentro del mismo workspace.
          </p>
        </div>
        <div className="landing-operator-steps">
          <article>
            <span>01</span>
            <strong>Alta por CUIT</strong>
            <p>Identidad legal y base inicial sin fricción.</p>
          </article>
          <article>
            <span>02</span>
            <strong>Inbox priorizado</strong>
            <p>Score, motivo y cierre en una misma cola.</p>
          </article>
          <article>
            <span>03</span>
            <strong>Pipeline trazable</strong>
            <p>Estado, notas y alertas sin depender de memoria humana.</p>
          </article>
        </div>
      </section>

      <section className="landing-proof-strip">
        <article className="landing-proof-card landing-proof-card-dark">
          <span className="section-kicker">Para la empresa</span>
          <h3>Una operación más gobernable.</h3>
          <p>La cuenta deja de ser un experimento y empieza a sostener una rutina real de trabajo.</p>
        </article>
        <article className="landing-proof-card">
          <span className="section-kicker">Para el equipo</span>
          <h3>Un criterio compartido.</h3>
          <p>Todos miran la misma oportunidad con score, estado y siguiente acción en el mismo contexto.</p>
        </article>
        <article className="landing-proof-card">
          <span className="section-kicker">Para la gestión</span>
          <h3>Menos pérdida por desorden.</h3>
          <p>El proceso queda más defendible frente a cliente interno y menos atado a personas clave.</p>
        </article>
      </section>
    </PageShell>
  );
}
