import Link from "next/link";

import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";

export default async function LoginPage() {
  return (
    <PageShell variant="auth" className="page-screen page-screen--login-selector">
      <SiteHeader section="auth" audience="public" />

      <section className="hero hero-app about-hero about-hero-premium auth-page-header auth-page-header-premium">
        <div className="premium-hero-copy">
          <span className="eyebrow">Acceso</span>
          <h1>Entrá por el carril correcto.</h1>
          <p>Separar acceso de empresa y acceso de plataforma evita mezcla de roles y hace más clara la prueba desde la primera pantalla.</p>
        </div>
        <article className="panel premium-hero-rail">
          <article>
            <span>Empresa</span>
            <strong>Uso operativo</strong>
            <p>Discovery, pipeline, perfil comercial y alertas.</p>
          </article>
          <article>
            <span>Superadmin</span>
            <strong>Operación global</strong>
            <p>Fuentes, jobs, automatización y gobierno de plataforma.</p>
          </article>
          <article>
            <span>Objetivo</span>
            <strong>Menos confusión</strong>
            <p>Que cada usuario vea solo el entorno que le corresponde.</p>
          </article>
        </article>
      </section>

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
