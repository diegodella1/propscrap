import Link from "next/link";
import { redirect } from "next/navigation";

import { SignupForm } from "../../components/signup-form";
import { SiteHeader } from "../../components/site-header";
import { getCurrentUserFromSession } from "../../lib/session";

export default async function SignupPage() {
  const currentUser = await getCurrentUserFromSession();
  if (currentUser) {
    redirect("/mi-cuenta");
  }

  return (
    <main className="page-shell">
      <SiteHeader section="auth" />

      <section className="hero hero-app about-hero signup-hero">
        <div>
          <span className="eyebrow">Onboarding por CUIT</span>
          <h1>Registrá tu empresa por CUIT.</h1>
        </div>
        <p>Ingresás CUIT, validás identidad legal y arrancás con un perfil comercial inicial.</p>
      </section>

      <section className="auth-layout auth-layout-upgraded signup-shell">
        <SignupForm />

        <article className="panel dispatch-panel onboarding-companion signup-companion">
          <span className="section-kicker">Qué se resuelve en el alta</span>
          <h2>Alta inicial de la empresa.</h2>
          <div className="signup-path">
            <p>1. Consultamos el CUIT y precargamos la identidad legal de la empresa.</p>
            <p>2. Confirmás cómo vende tu empresa: rubros, buyers, keywords y jurisdicciones.</p>
            <p>3. Entrás al workspace con una base comercial lista para trabajar.</p>
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
              <p>El objetivo del alta es llegar rápido a oportunidades relevantes.</p>
            </article>
          </div>

          <div className="hero-actions">
            <Link href="/about" className="button-secondary">
              Ver el flujo completo
            </Link>
            <Link href="/login" className="linkish">
              Ya tengo cuenta
            </Link>
          </div>
        </article>
      </section>
    </main>
  );
}
