import Link from "next/link";
import { redirect } from "next/navigation";

import { PageHero } from "../../../components/layout/page-hero";
import { PageShell } from "../../../components/layout/page-shell";
import { LoginForm } from "../../../components/login-form";
import { SiteHeader } from "../../../components/site-header";
import { getCurrentUserFromSession } from "../../../lib/session";

export default async function LoginPage() {
  const currentUser = await getCurrentUserFromSession();
  if (currentUser) {
    redirect("/mi-cuenta");
  }

  return (
    <PageShell variant="auth">
      <SiteHeader section="auth" />

      <PageHero
        eyebrow="Ingresar"
        title="Ingresá a tu workspace."
        description="Accedé con email y contraseña para volver a oportunidades, seguimiento o administración según tu rol."
        className="workspace-header auth-page-header"
      />

      <section className="auth-layout auth-layout-upgraded signup-shell login-shell">
        <LoginForm />
        <article className="panel dispatch-panel onboarding-companion signup-companion login-companion">
          <span className="section-kicker">Qué encontrás adentro</span>
          <h2>Una herramienta de trabajo, no una landing</h2>
          <div className="signup-path">
            <p>Oportunidades priorizadas por score y urgencia.</p>
            <p>Seguimiento con estados, notas y alertas.</p>
            <p>Capas de administración si tu rol lo permite.</p>
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
    </PageShell>
  );
}
