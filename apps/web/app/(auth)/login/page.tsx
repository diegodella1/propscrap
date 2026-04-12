import Link from "next/link";
import { redirect } from "next/navigation";

import { PageHero } from "../../../components/layout/page-hero";
import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";
import { getCurrentUserFromSession } from "../../../lib/session";

export default async function LoginPage() {
  const currentUser = await getCurrentUserFromSession();
  if (currentUser) {
    redirect(currentUser.role === "admin" ? "/admin/platform" : "/dashboard");
  }

  return (
    <PageShell variant="auth" className="page-screen page-screen--login-selector">
      <SiteHeader section="auth" />

      <PageHero
        eyebrow="Acceso"
        title="Elegí el tipo de acceso."
        description="Separá el ingreso operativo de clientes del acceso de plataforma para que la prueba sea clara y sin mezcla de roles."
        className="workspace-header auth-page-header"
      />

      <section className="auth-choice-grid">
        <article className="panel dispatch-panel auth-choice-card">
          <span className="section-kicker">Clientes</span>
          <h2>Ingreso empresa</h2>
          <p>Para usuarios de empresas que van a usar la demo 30 días en discovery, seguimiento y alertas.</p>
          <div className="signup-confidence-bar">
            <span>Dashboard</span>
            <span>Seguimiento</span>
            <span>Perfil empresa</span>
          </div>
          <div className="hero-actions">
            <Link href="/login/empresa" className="button-primary">
              Ingresar empresa
            </Link>
            <Link href="/signup" className="button-secondary">
              Crear cuenta
            </Link>
          </div>
        </article>

        <article className="panel dispatch-panel auth-choice-card">
          <span className="section-kicker">Plataforma</span>
          <h2>Ingreso superadmin</h2>
          <p>Para operación global: fuentes, jobs, automatización, credenciales y administración transversal del piloto.</p>
          <div className="signup-confidence-bar">
            <span>Fuentes</span>
            <span>Jobs</span>
            <span>Usuarios</span>
          </div>
          <div className="hero-actions">
            <Link href="/login/superadmin" className="button-primary">
              Ingresar superadmin
            </Link>
            <Link href="/about" className="button-secondary">
              Ver cómo funciona
            </Link>
          </div>
        </article>
      </section>
    </PageShell>
  );
}
