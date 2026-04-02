import Link from "next/link";

import { ProcessDiagramIllustration } from "../../components/landing-ornaments";
import { SiteHeader } from "../../components/site-header";
import { getCurrentUserFromSession } from "../../lib/session";

export default async function AboutPage() {
  const currentUser = await getCurrentUserFromSession();

  return (
    <main className="page-shell">
      <SiteHeader section="about" currentUserName={currentUser?.full_name} />

      <section className="hero hero-app about-hero">
        <div>
          <span className="eyebrow">Cómo funciona</span>
          <h1>De información fragmentada a un criterio operativo compartido.</h1>
        </div>
        <p>
          Licitaciones IA toma fuentes públicas, normaliza oportunidades, procesa documentos, prioriza relevancia y
          deja una vista que un equipo comercial puede usar para decidir con menos fricción y más contexto.
        </p>
      </section>

      <section className="about-grid">
        <article className="feature-panel feature-panel-dark">
          <span className="section-kicker">Qué hace</span>
          <h2>Centraliza, explica y ordena.</h2>
          <p>
            El sistema consolida licitaciones, muestra metadatos, baja documentos, extrae texto, genera contexto
            estructurado y calcula relevancia contra un perfil de empresa. El objetivo no es “mostrar más”, sino
            ayudar a decidir mejor.
          </p>
        </article>

        <article className="feature-panel feature-panel-light">
          <ProcessDiagramIllustration />
          <span className="section-kicker">Qué evita</span>
          <ol className="timeline-list">
            <li>Buscar manualmente en múltiples portales sin una vista común.</li>
            <li>Discutir oportunidades sin fechas, evidencia ni score explicable.</li>
            <li>Llegar tarde por no tener seguimiento mínimo y alertas visibles.</li>
            <li>Perder trazabilidad entre hallazgo, análisis y decisión comercial.</li>
          </ol>
        </article>
      </section>

      <section className="why-grid">
        <article className="why-card">
          <span className="section-kicker">1. Ingesta</span>
          <h3>Fuentes públicas reales</h3>
          <p>Las fuentes se registran, se corren y dejan trazabilidad. El sistema no oculta si algo falla.</p>
        </article>
        <article className="why-card">
          <span className="section-kicker">2. Análisis</span>
          <h3>Resumen, score y riesgo</h3>
          <p>La oportunidad deja de ser un título y pasa a ser una decisión con contexto, razones y urgencia visible.</p>
        </article>
        <article className="why-card">
          <span className="section-kicker">3. Acción</span>
          <h3>Workflow y alertas</h3>
          <p>El equipo puede guardar, evaluar o descartar sin salir de la misma interfaz operativa.</p>
        </article>
      </section>

      <section className="cta-band">
        <div>
          <span className="section-kicker">Ver la experiencia</span>
          <h2>La mejor explicación sigue siendo el producto funcionando.</h2>
          <p>Entrá al dashboard para ver score, urgencia, fuentes y seguimiento en una misma vista.</p>
        </div>
        <Link href="/dashboard" className="button-primary">
          Abrir dashboard
        </Link>
      </section>
    </main>
  );
}
