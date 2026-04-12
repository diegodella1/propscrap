import Link from "next/link";
import { redirect } from "next/navigation";

import { AccountSettingsForm } from "../../../components/account-settings-form";
import { PageShell } from "../../../components/layout/page-shell";
import { LogoutButton } from "../../../components/logout-button";
import { OnboardingWizard } from "../../../components/onboarding-wizard";
import { SiteHeader } from "../../../components/site-header";
import { getCurrentUserFromSession } from "../../../lib/session";

type Props = {
  searchParams: Promise<{ onboarding?: string }>;
};

function alertPriorityLabel(minScore: number | undefined) {
  if ((minScore ?? 60) >= 75) return "Alta";
  if ((minScore ?? 60) <= 0) return "Todas";
  return "Media o alta";
}

function primaryChannelLabel(currentUser: Awaited<ReturnType<typeof getCurrentUserFromSession>>) {
  const channels = currentUser?.alert_preferences_json?.channels ?? ["dashboard"];
  if (channels.includes("whatsapp")) return "WhatsApp";
  if (channels.includes("telegram")) return "Telegram";
  if (channels.includes("email")) return "Email";
  return "Dashboard";
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
    <PageShell variant="workspace" className="workspace-shell account-page">
      {currentUser.role !== "admin" ? <OnboardingWizard variant="company" forceOpen={onboarding} /> : null}
      <SiteHeader
        section="account"
        currentUserName={currentUser.full_name}
        currentUserRole={currentUser.role}
      />

      <section className="workspace-header account-header">
        <div>
          <span className="eyebrow">Mi cuenta</span>
          <h1>Preferencias personales.</h1>
          <p>
            {onboarding
              ? "Definí canal y nivel de alerta antes de empezar a operar."
              : "Ajustá identidad, canal y preferencias de avisos."}
          </p>
        </div>
        <div className="workspace-header-actions">
          <Link href="/company-profile" className="button-secondary">
            Perfil comercial
          </Link>
          {adminHref && adminLabel ? (
            <Link href={adminHref} className="button-primary">
              {adminLabel}
            </Link>
          ) : null}
        </div>
      </section>

      <section className="dashboard-executive-band account-summary-band workspace-kpi-band">
        <article>
          <span>Canal principal</span>
          <strong>{primaryChannelLabel(currentUser)}</strong>
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
              <p>
                {currentUser.whatsapp_number
                  ? `WhatsApp ${currentUser.whatsapp_number}`
                  : currentUser.telegram_chat_id
                    ? `Telegram ${currentUser.telegram_chat_id}`
                    : "Todavía no cargaste un canal directo para alertas instantáneas."}
              </p>
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
            <Link href="/company-profile" className="button-secondary">
              Editar perfil comercial
            </Link>
            <LogoutButton />
          </div>
        </article>
      </section>
    </PageShell>
  );
}
