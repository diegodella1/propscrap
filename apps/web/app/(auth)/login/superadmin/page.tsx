import Link from "next/link";
import { redirect } from "next/navigation";

import { PageHero } from "../../../../components/layout/page-hero";
import { PageShell } from "../../../../components/layout/page-shell";
import { LoginForm } from "../../../../components/login-form";
import { SiteHeader } from "../../../../components/site-header";
import { getCurrentUserFromSession } from "../../../../lib/session";

export default async function SuperadminLoginPage() {
  const currentUser = await getCurrentUserFromSession();
  if (currentUser) {
    redirect(currentUser.role === "admin" ? "/admin/platform" : "/dashboard");
  }

  return (
    <PageShell variant="auth">
      <SiteHeader section="auth" />

      <PageHero
        eyebrow="Acceso superadmin"
        title="Ingresá a la consola de plataforma."
        description="Este acceso es exclusivo para superadmin. Desde acá se gobiernan fuentes, jobs, automatización y usuarios globales."
        className="workspace-header auth-page-header"
      />

      <section className="auth-layout auth-layout-upgraded signup-shell login-shell">
        <LoginForm variant="superadmin" />
        <article className="panel dispatch-panel onboarding-companion signup-companion login-companion">
          <span className="section-kicker">Qué controlás acá</span>
          <h2>Operación completa de la plataforma</h2>
          <div className="signup-path">
            <p>Alta y edición de fuentes, conectores y modos de scraping.</p>
            <p>Ejecución de jobs, revisión de auditoría y monitoreo de alertas.</p>
            <p>Configuración de LLM, Resend, contactos públicos y automatización.</p>
          </div>
          <div className="hero-actions">
            <Link href="/login/empresa" className="button-secondary">
              Ir a ingreso empresa
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
