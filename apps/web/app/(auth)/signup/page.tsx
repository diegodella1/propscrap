import Link from "next/link";

import { PageShell } from "../../../components/layout/page-shell";
import { SignupForm } from "../../../components/signup-form";
import { SiteHeader } from "../../../components/site-header";

export default async function SignupPage() {
  return (
    <PageShell variant="auth" className="page-screen page-screen--signup">
      <SiteHeader section="auth" audience="public" />

      <section className="hero hero-app about-hero about-hero-premium auth-page-header auth-page-header-premium">
        <div className="premium-hero-copy">
          <span className="eyebrow">Onboarding por CUIT</span>
          <h1>Alta limpia, rápida y con base legal.</h1>
          <p>Ingresás CUIT, validás identidad legal y arrancás una prueba de 30 días con una cuenta orientada a discovery, seguimiento y alertas.</p>
        </div>
        <article className="panel premium-hero-rail">
          <article>
            <span>01</span>
            <strong>Validación</strong>
            <p>CUIT y empresa precargados desde fuente legal.</p>
          </article>
          <article>
            <span>02</span>
            <strong>Cuenta lista</strong>
            <p>El alta no termina en login: termina en workspace.</p>
          </article>
          <article>
            <span>03</span>
            <strong>Prueba seria</strong>
            <p>La intención es que el equipo pueda usarla de verdad.</p>
          </article>
        </article>
      </section>

      <section className="auth-layout auth-layout-upgraded signup-shell">
        <SignupForm />

        <article className="panel dispatch-panel onboarding-companion signup-companion">
          <span className="section-kicker">Qué se resuelve en el alta</span>
          <h2>Alta inicial para una prueba seria</h2>
          <div className="signup-path">
            <p>1. Consultamos el CUIT y precargamos la identidad legal de la empresa.</p>
            <p>2. Confirmás cómo vende tu empresa: rubros, buyers, keywords y jurisdicciones.</p>
            <p>3. Entrás al workspace con una base comercial lista para que el equipo lo use de verdad durante 30 días.</p>
          </div>

          <div className="onboarding-proof-list">
            <article>
              <strong>Fuente legal</strong>
              <p>Base de datos pública argentina para acelerar el alta y reducir errores manuales.</p>
            </article>
            <article>
              <strong>Perfil inicial</strong>
              <p>No arrancás de cero: el sistema deja una primera estructura usable.</p>
            </article>
            <article>
              <strong>Primer valor</strong>
              <p>El objetivo del alta es que la prueba llegue rápido a oportunidades, pipeline y alertas reales.</p>
            </article>
          </div>

          <div className="hero-actions">
            <Link href="/about" className="button-secondary">
              Ver el flujo completo
            </Link>
            <Link href="/login/empresa" className="linkish">
              Ya tengo cuenta
            </Link>
          </div>
        </article>
      </section>
    </PageShell>
  );
}
