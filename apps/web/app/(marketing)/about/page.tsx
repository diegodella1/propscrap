import Link from "next/link";

import { ProcessFlowEditorialIllustration, WorkspaceBoardIllustration } from "../../../components/landing-ornaments";
import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";

export default async function AboutPage() {
  return (
    <PageShell variant="marketing" className="page-screen page-screen--about">
      <SiteHeader section="about" audience="public" />

      <section className="hero hero-app about-hero about-hero-premium">
        <div className="premium-hero-copy">
          <span className="eyebrow">Cómo Funciona</span>
          <h1>Del alta legal al seguimiento diario, sin cambiar de sistema.</h1>
          <p>La prueba sirve cuando deja una operación mínima funcionando: empresa cargada, discovery priorizado, pipeline vivo y alertas que salen del dashboard.</p>
        </div>
        <article className="panel premium-hero-rail">
          <article>
            <span>01</span>
            <strong>CUIT validado</strong>
            <p>La empresa entra con identidad legal y base inicial.</p>
          </article>
          <article>
            <span>02</span>
            <strong>Discovery priorizado</strong>
            <p>Score, motivo y fecha en la misma cola.</p>
          </article>
          <article>
            <span>03</span>
            <strong>Seguimiento serio</strong>
            <p>Estado, notas y alertas sostenibles por 30 días.</p>
          </article>
        </article>
      </section>

      <section className="how-it-works-stage">
        <div className="results-header">
          <div>
            <span className="section-kicker">Recorrido</span>
            <h2>Un recorrido breve para pasar del interés a una rutina operativa real.</h2>
          </div>
          <p>No es un tour largo. Son tres movimientos concretos para que el equipo deje de trabajar repartido.</p>
        </div>

        <article className="panel how-it-works-diagram">
          <ProcessFlowEditorialIllustration />
        </article>

        <div className="how-it-works-steps">
          <article className="proof-card">
            <span className="section-kicker">Paso 1</span>
            <h2>Se registra la empresa</h2>
            <p>Alta por CUIT para arrancar con identidad legal y una base comercial inicial.</p>
          </article>
          <article className="proof-card">
            <span className="section-kicker">Paso 2</span>
            <h2>Se ordena el discovery</h2>
            <p>Las fuentes se consolidan en una cola priorizada, con contexto y fechas visibles.</p>
          </article>
          <article className="proof-card">
            <span className="section-kicker">Paso 3</span>
            <h2>Se ejecuta el seguimiento</h2>
            <p>La licitación pasa a pipeline, con estado, notas, alertas y próxima acción.</p>
          </article>
        </div>
      </section>

      <section className="editorial-grid">
        <article className="editorial-callout editorial-callout-dark">
          <span className="section-kicker">Para quién</span>
          <h2>Empresas proveedoras que ya sienten el costo de operar licitaciones a mano.</h2>
          <p>
            Si hoy el equipo trabaja con portales, pliegos y planillas por separado, EasyTaciones entra para dar
            estructura y criterio compartido.
          </p>
        </article>
        <article className="editorial-callout">
          <span className="section-kicker">Qué cambia</span>
          <h2>Se deja de recolectar links y se pasa a gestionar una cola de trabajo.</h2>
          <p>No suma ruido. Reduce fricción y vuelve más defendible la operación frente al cliente interno.</p>
        </article>
      </section>

      <section className="about-logic-stage">
        <div className="results-header about-logic-header">
          <div>
            <span className="section-kicker">Workspace</span>
            <h2>La promesa del producto se tiene que entender apenas abrís la pantalla.</h2>
          </div>
          <p>Alta por CUIT, matching con criterio y seguimiento para no depender de memoria humana.</p>
        </div>

        <div className="about-logic-grid">
          <article className="panel about-logic-diagram">
            <WorkspaceBoardIllustration />
          </article>

          <article className="panel about-logic-copy">
            <span className="section-kicker">Qué cambia</span>
            <h3>Se pasa de una tarea artesanal a una operación repetible.</h3>
            <div className="about-logic-points">
              <article>
                <strong>Antes</strong>
                <p>Buscar, leer, copiar y acordarse. Todo repartido en personas, tabs y planillas.</p>
              </article>
              <article>
                <strong>Con EasyTaciones</strong>
                <p>La oportunidad entra con contexto, se guarda con criterio y se sigue con fechas y responsables.</p>
              </article>
              <article>
                <strong>Para el equipo</strong>
                <p>Más continuidad operativa, menos fricción interna y menos riesgo de perder timing.</p>
              </article>
            </div>
          </article>
        </div>
      </section>

      <section className="workspace-preview-grid">
        <article className="experience-card experience-card-dark">
          <span className="section-kicker">Cliente</span>
          <h3>Workspace claro y accionable</h3>
          <p>Oportunidades, seguimiento y alertas en un único entorno de trabajo.</p>
        </article>
        <article className="experience-card">
          <span className="section-kicker">Equipo</span>
          <h3>Menos dependencia de personas clave</h3>
          <p>El criterio deja de vivir en una sola persona y pasa a estar disponible para todos.</p>
        </article>
        <article className="experience-card">
          <span className="section-kicker">Empresa</span>
          <h3>Más calma para operar</h3>
          <p>Paz mental operativa frente a un proceso que suele sentirse caótico todos los días.</p>
        </article>
      </section>

      <section className="cta-band">
        <div>
          <span className="section-kicker">Siguiente Paso</span>
          <h2>La propuesta se vuelve clara cuando entra con una operación real.</h2>
          <p>Pedí demo o registrá una empresa por CUIT para probar el flujo completo con un equipo real durante 30 días.</p>
        </div>
        <div className="hero-actions">
          <Link href="/contact" className="button-primary">
            Solicitar Demo
          </Link>
          <Link href="/signup" className="button-secondary">
            Registrar Empresa
          </Link>
        </div>
      </section>
    </PageShell>
  );
}
