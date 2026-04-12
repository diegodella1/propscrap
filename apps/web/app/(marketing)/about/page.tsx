import Link from "next/link";

import { ProcessFlowEditorialIllustration, WorkspaceBoardIllustration } from "../../../components/landing-ornaments";
import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";
import { getCurrentUserFromSession } from "../../../lib/session";

export default async function AboutPage() {
  const currentUser = await getCurrentUserFromSession();

  return (
    <PageShell variant="marketing">
      <SiteHeader
        section="about"
        currentUserName={currentUser?.full_name}
        currentUserRole={currentUser?.role}
      />

      <section className="hero hero-app about-hero">
        <div>
          <span className="eyebrow">Cómo Funciona</span>
          <h1>Del CUIT al seguimiento, en un solo flujo.</h1>
        </div>
        <p>La lógica es simple: completar la empresa, ordenar el discovery y sostener la ejecución.</p>
      </section>

      <section className="how-it-works-stage">
        <div className="results-header">
          <div>
            <span className="section-kicker">Recorrido</span>
            <h2>Un flujo simple para un trabajo que hoy suele hacerse a mano.</h2>
          </div>
          <p>Primero entra la empresa. Después aparece el discovery. Por último se ordena la ejecución.</p>
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
          <h2>Empresas proveedoras que hoy trabajan licitaciones con demasiada fricción.</h2>
          <p>
            Si hoy el equipo trabaja con portales, pliegos y planillas por separado, EasyTaciones entra para dar
            estructura y criterio compartido.
          </p>
        </article>
        <article className="editorial-callout">
          <span className="section-kicker">Qué cambia</span>
          <h2>Se deja de buscar y acordarse, y se pasa a ver, decidir y seguir.</h2>
          <p>No es sólo más información. Es una operación más controlada.</p>
        </article>
      </section>

      <section className="about-logic-stage">
        <div className="results-header about-logic-header">
          <div>
            <span className="section-kicker">Workspace</span>
            <h2>La promesa del producto se ve en la interfaz.</h2>
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
          <h3>Workspace simple y accionable</h3>
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
          <h2>La propuesta se entiende mejor cuando se recorre el flujo completo.</h2>
          <p>Pedí demo o registrá una empresa por CUIT para recorrer el producto desde adentro.</p>
        </div>
        <div className="hero-actions">
          <Link href="/contact" className="button-primary">
            Solicitar Demo
          </Link>
          <Link href={currentUser ? "/dashboard" : "/signup"} className="button-secondary">
            {currentUser ? "Ir al Workspace" : "Registrar Empresa"}
          </Link>
        </div>
      </section>
    </PageShell>
  );
}
