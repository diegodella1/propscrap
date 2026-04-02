import Link from "next/link";
import { redirect } from "next/navigation";

import { AccountSettingsForm } from "../../components/account-settings-form";
import { LogoutButton } from "../../components/logout-button";
import { SiteHeader } from "../../components/site-header";
import { getCurrentUserFromSession } from "../../lib/session";

type Props = {
  searchParams: Promise<{ onboarding?: string }>;
};

export default async function AccountPage({ searchParams }: Props) {
  const params = await searchParams;
  const currentUser = await getCurrentUserFromSession();
  if (!currentUser) {
    redirect("/login");
  }

  const onboarding = params.onboarding === "1";
  const adminHref = currentUser.role === "admin" ? "/admin/platform" : currentUser.role === "manager" ? "/admin/company" : null;
  const adminLabel = currentUser.role === "admin" ? "Abrir admin de plataforma" : currentUser.role === "manager" ? "Abrir admin de empresa" : null;

  return (
    <main className="page-shell">
      <SiteHeader section="account" currentUserName={currentUser.full_name} />

      <section className="hero hero-app about-hero">
        <div>
          <span className="eyebrow">Mi cuenta</span>
          <h1>Tu contacto y tus alertas, en una sola pantalla.</h1>
        </div>
        <p>
          {onboarding
            ? "Tu cuenta ya está lista. Dejá tu WhatsApp y elegí qué querés recibir."
            : "Acá podés cambiar tu contacto, tu empresa y la forma en que querés enterarte de nuevas oportunidades."}
        </p>
      </section>

      <section className="auth-layout">
        <article className="panel dispatch-panel">
          {onboarding ? (
            <div className="detail-note-card">
              <span className="section-kicker">Paso recomendado</span>
              <p>Si completás tu WhatsApp ahora, las alertas te pueden llegar sin depender de abrir el dashboard.</p>
            </div>
          ) : null}
          <AccountSettingsForm user={currentUser} />
        </article>

        <article className="panel dispatch-panel">
          <span className="section-kicker">Resumen</span>
          <h2>Qué vas a recibir</h2>
          <div className="source-stack">
            <article className="source-card">
              <strong>WhatsApp</strong>
              <p>{currentUser.whatsapp_number ?? "Todavía no cargaste un número."}</p>
            </article>
            <article className="source-card">
              <strong>Empresa</strong>
              <p>{currentUser.company_name ?? "Todavía no cargaste tu empresa."}</p>
            </article>
            <article className="source-card">
              <strong>Prioridad</strong>
              <p>
                {(currentUser.alert_preferences_json?.min_score ?? 60) >= 75
                  ? "Solo alta prioridad"
                  : (currentUser.alert_preferences_json?.min_score ?? 60) <= 0
                    ? "Todas"
                    : "Media o alta"}
              </p>
            </article>
          </div>
          <div className="hero-actions">
            <Link href="/company-profile" className="button-primary">
              Editar perfil comercial
            </Link>
            {adminHref && adminLabel ? (
              <Link href={adminHref} className="button-secondary">
                {adminLabel}
              </Link>
            ) : null}
            <LogoutButton />
          </div>
        </article>
      </section>
    </main>
  );
}
