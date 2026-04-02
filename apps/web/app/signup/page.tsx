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

      <section className="hero hero-app about-hero">
        <div>
          <span className="eyebrow">Crear cuenta</span>
          <h1>Una cuenta simple para seguir oportunidades sin perderte nada.</h1>
        </div>
        <p>
          Te pedimos solo lo necesario para empezar. Después vas a poder dejar tu WhatsApp y elegir cómo querés
          recibir alertas.
        </p>
      </section>

      <section className="auth-layout">
        <SignupForm />
        <article className="panel dispatch-panel">
          <span className="section-kicker">Qué sigue</span>
          <h2>Después del alta</h2>
          <p className="muted">
            Vas a entrar directo a tu cuenta para cargar tu número, activar alertas por WhatsApp y definir qué tan
            filtradas las querés.
          </p>
          <Link href="/login" className="button-secondary">
            Ya tengo cuenta
          </Link>
        </article>
      </section>
    </main>
  );
}
