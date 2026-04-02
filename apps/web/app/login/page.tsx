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
          <h1>Entrá y dejá tus alertas listas.</h1>
        </div>
        <p>Usá tu email y contraseña. Si todavía no tenés cuenta, la podés crear en menos de un minuto.</p>
      </section>

      <section className="auth-layout">
        <LoginForm />
        <article className="panel dispatch-panel">
          <span className="section-kicker">Nuevo</span>
          <h2>¿Todavía no tenés cuenta?</h2>
          <p className="muted">
            Creala una vez y después vas a poder cargar tu WhatsApp, definir qué querés recibir y cambiarlo cuando
            quieras.
          </p>
          <Link href="/signup" className="button-secondary">
            Crear cuenta
          </Link>
        </article>
      </section>
    </main>
  );
}
