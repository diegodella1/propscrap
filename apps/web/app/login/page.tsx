import Link from "next/link";
import { redirect } from "next/navigation";

import { LoginForm } from "../../components/login-form";
import { SiteHeader } from "../../components/site-header";
import { getCurrentUserFromSession } from "../../lib/session";

export default async function LoginPage() {
  const currentUser = await getCurrentUserFromSession();
  if (currentUser) {
    redirect("/mi-cuenta");
  }

  return (
    <main className="page-shell">
      <SiteHeader section="auth" />

      <section className="hero hero-app about-hero">
        <div>
          <span className="eyebrow">Ingresar</span>
          <h1>Ingresá a tu workspace.</h1>
        </div>
        <p>Entrás con email y contraseña y volvés a oportunidades, seguimiento o administración según tu rol.</p>
      </section>

      <section className="auth-layout auth-layout-upgraded signup-shell login-shell">
        <LoginForm />
        <article className="panel dispatch-panel onboarding-companion signup-companion login-companion">
          <span className="section-kicker">Acceso</span>
          <h2>Qué vas a encontrar adentro.</h2>
          <div className="signup-path">
            <p>Discovery priorizado.</p>
            <p>Seguimiento y alertas configuradas.</p>
            <p>Capas de administración, si tu rol lo permite.</p>
          </div>
          <div className="hero-actions">
            <Link href="/signup" className="button-secondary">
              Crear cuenta
            </Link>
            <Link href="/about" className="linkish">
              Ver propuesta
            </Link>
          </div>
        </article>
      </section>
    </main>
  );
}
