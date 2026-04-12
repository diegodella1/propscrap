import Link from "next/link";
import { redirect } from "next/navigation";

import { PageHero } from "../../../../components/layout/page-hero";
import { PageShell } from "../../../../components/layout/page-shell";
import { LoginForm } from "../../../../components/login-form";
import { SiteHeader } from "../../../../components/site-header";
import { getCurrentUserFromSession } from "../../../../lib/session";

export default async function CompanyLoginPage() {
  const currentUser = await getCurrentUserFromSession();
  if (currentUser) {
    redirect(currentUser.role === "admin" ? "/admin/platform" : "/dashboard");
  }

  return (
    <PageShell variant="auth">
      <SiteHeader section="auth" />

      <PageHero
        eyebrow="Acceso empresa"
        title="Ingresá como cliente."
        description="Este acceso es para equipos de empresas que usan EasyTaciones para discovery, seguimiento y alertas."
        className="workspace-header auth-page-header"
      />

      <section className="auth-layout auth-layout-upgraded signup-shell login-shell">
        <LoginForm variant="company" />
        <article className="panel dispatch-panel onboarding-companion signup-companion login-companion">
          <span className="section-kicker">Qué encontrás adentro</span>
          <h2>Workspace comercial de empresa</h2>
          <div className="signup-path">
            <p>Discovery priorizado según score, fecha y motivo de match.</p>
            <p>Pipeline para seguir lo que ya vale trabajar.</p>
            <p>Perfil comercial de empresa para ajustar matching y alertas.</p>
          </div>
          <div className="hero-actions">
            <Link href="/signup" className="button-secondary">
              Crear cuenta
            </Link>
            <Link href="/login/superadmin" className="linkish">
              Soy superadmin
            </Link>
          </div>
        </article>
      </section>
    </PageShell>
  );
}
