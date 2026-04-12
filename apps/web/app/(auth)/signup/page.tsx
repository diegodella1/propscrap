import Link from "next/link";
import { redirect } from "next/navigation";

import { PageHero } from "../../../components/layout/page-hero";
import { PageShell } from "../../../components/layout/page-shell";
import { SignupForm } from "../../../components/signup-form";
import { SiteHeader } from "../../../components/site-header";
import { getCurrentUserFromSession } from "../../../lib/session";

export default async function SignupPage() {
  const currentUser = await getCurrentUserFromSession();
  if (currentUser) {
    redirect(currentUser.role === "admin" ? "/admin/platform" : "/dashboard");
  }

  return (
    <PageShell variant="auth">
      <SiteHeader section="auth" />

      <PageHero
        eyebrow="Onboarding por CUIT"
        title="Registrá tu empresa por CUIT."
        description="Ingresás CUIT, validás identidad legal y arrancás una prueba de 30 días con un workspace listo para usar."
        className="workspace-header auth-page-header"
      />

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
