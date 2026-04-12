import Link from "next/link";
import { redirect } from "next/navigation";

import { AccountSettingsForm } from "../../components/account-settings-form";
import { LogoutButton } from "../../components/logout-button";
import { SiteHeader } from "../../components/site-header";
import { getCurrentUserFromSession } from "../../lib/session";

type Props = {
  searchParams: Promise<{ onboarding?: string }>;
};

function alertPriorityLabel(minScore: number | undefined) {
  if ((minScore ?? 60) >= 75) return "Alta";
  if ((minScore ?? 60) <= 0) return "Todas";
  return "Media o alta";
}

export default async function AccountPage({ searchParams }: Props) {
  const params = await searchParams;
  const currentUser = await getCurrentUserFromSession();
  if (!currentUser) {
    redirect("/login");
  }

  const onboarding = params.onboarding === "1";
  const adminHref =
    currentUser.role === "admin" ? "/admin/platform" : currentUser.role === "manager" ? "/admin/company" : null;
  const adminLabel =
    currentUser.role === "admin"
      ? "Abrir plataforma"
      : currentUser.role === "manager"
        ? "Abrir equipo"
        : null;

  return (
    <main className="page-shell">
      <SiteHeader
        section="account"
        currentUserName={currentUser.full_name}
        currentUserRole={currentUser.role}
      />

      <section className="hero hero-app about-hero account-hero">
        <div>
          <span className="eyebrow">Mi cuenta</span>
          <h1>Preferencias personales.</h1>
        </div>
        <p>
          {onboarding
            ? "Configurá canal de alertas y datos personales antes de empezar."
            : "Ajustá canal, identidad y preferencias de alertas."}
        </p>
      </section>

      <section className="dashboard-executive-band account-summary-band">
        <article>
          <span>Canal principal</span>
          <strong>{currentUser.whatsapp_opt_in ? "WhatsApp" : "Dashboard"}</strong>
        </article>
        <article>
          <span>Prioridad</span>
          <strong>{alertPriorityLabel(currentUser.alert_preferences_json?.min_score)}</strong>
        </article>
        <article>
          <span>Empresa</span>
          <strong>{currentUser.company_name ?? "Sin empresa"}</strong>
        </article>
        <article>
          <span>Rol</span>
          <strong>{currentUser.role}</strong>
        </article>
      </section>

      <section className="auth-layout auth-layout-upgraded account-shell">
        <article className="panel dispatch-panel">
          {onboarding ? (
            <div className="detail-note-card">
              <span className="section-kicker">Recomendado</span>
              <p>Cargá WhatsApp si querés recibir alertas fuera del dashboard.</p>
            </div>
          ) : null}
          <AccountSettingsForm user={currentUser} />
        </article>

        <article className="panel dispatch-panel onboarding-companion">
          <span className="section-kicker">Resumen</span>
          <h2>Configuración actual</h2>

          <div className="onboarding-proof-list">
            <article>
              <strong>Canal</strong>
              <p>{currentUser.whatsapp_number ?? "Todavía no cargaste un número para WhatsApp."}</p>
            </article>
            <article>
              <strong>Empresa</strong>
              <p>{currentUser.company_name ?? "Todavía no vinculaste una empresa visible."}</p>
            </article>
            <article>
              <strong>Filtro de alertas</strong>
              <p>{alertPriorityLabel(currentUser.alert_preferences_json?.min_score)}</p>
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
