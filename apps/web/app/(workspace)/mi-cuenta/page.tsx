import Link from "next/link";
import { redirect } from "next/navigation";

import { AccountSettingsForm } from "../../../components/account-settings-form";
import { PageShell } from "../../../components/layout/page-shell";
import { LogoutButton } from "../../../components/logout-button";
import { OnboardingWizard, type OnboardingStep } from "../../../components/onboarding-wizard";
import { SiteHeader } from "../../../components/site-header";
import { fetchSavedTenders } from "../../../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession, getMyCompanyProfileFromSession } from "../../../lib/session";

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

function configuredChannelLabels(currentUser: Awaited<ReturnType<typeof getCurrentUserFromSession>>) {
  const channels = currentUser?.alert_preferences_json?.channels ?? ["dashboard"];
  const labels: string[] = [];
  if (channels.includes("email")) labels.push("Email");
  if (channels.includes("whatsapp") && currentUser?.whatsapp_number) labels.push("WhatsApp");
  if (channels.includes("telegram") && currentUser?.telegram_chat_id) labels.push("Telegram");
  if (!labels.length) labels.push("Dashboard");
  return labels;
}

export default async function AccountPage({ searchParams }: Props) {
  const params = await searchParams;
  const [currentUser, profile, cookieHeader] = await Promise.all([
    getCurrentUserFromSession(),
    getMyCompanyProfileFromSession(),
    getCookieHeaderFromSession(),
  ]);
  if (!currentUser) {
    redirect("/login");
  }

  const saved = await fetchSavedTenders(cookieHeader || undefined).catch(() => null);

  const onboarding = params.onboarding === "1";
  const adminHref =
    currentUser.role === "admin" ? "/admin/platform" : currentUser.role === "manager" ? "/admin/company" : null;
  const adminLabel =
    currentUser.role === "admin"
      ? "Abrir plataforma"
      : currentUser.role === "manager"
        ? "Abrir equipo"
        : null;
  const channels = currentUser.alert_preferences_json?.channels ?? ["dashboard"];
  const alertChannelReady =
    channels.includes("email") ||
    (channels.includes("whatsapp") && Boolean(currentUser.whatsapp_number)) ||
    (channels.includes("telegram") && Boolean(currentUser.telegram_chat_id));
  const profileReady = Boolean(
    profile?.company_description?.trim() &&
      ((profile?.include_keywords?.length ?? 0) > 0 ||
        (profile?.preferred_buyers?.length ?? 0) > 0 ||
        (profile?.jurisdictions?.length ?? 0) > 0),
  );
  const savedCount = saved?.total ?? 0;
  const configuredChannels = configuredChannelLabels(currentUser);
  const companyOnboardingSteps: OnboardingStep[] = [
    {
      id: "alerts",
      title: "Definí tu canal de alertas",
      body: "Configurá al menos un canal útil para sacar la operación del dashboard.",
      href: "/mi-cuenta",
      cta: "Configurar alertas",
      complete: alertChannelReady,
      evidence: alertChannelReady
        ? `Activo: ${primaryChannelLabel(currentUser)}.`
        : "Todavía no hay un canal directo listo para alertas útiles.",
    },
    {
      id: "profile",
      title: "Completá el perfil comercial",
      body: "Cargá descripción, señales positivas y cobertura para que el matching deje de ser genérico.",
      href: "/company-profile",
      cta: "Completar perfil",
      complete: profileReady,
      evidence: profileReady
        ? "Hay base comercial suficiente para recalcular relevancia."
        : "Falta describir mejor la empresa o agregar señales de matching.",
    },
    {
      id: "pipeline",
      title: "Guardá tu primera licitación",
      body: "Mandá al pipeline al menos una oportunidad para empezar a usar el flujo real de seguimiento.",
      href: "/dashboard",
      cta: "Ir a discovery",
      complete: savedCount > 0,
      evidence: savedCount > 0 ? `${savedCount} licitaciones ya están en seguimiento.` : "Todavía no guardaste ninguna oportunidad.",
    },
    {
      id: "follow-up",
      title: "Ordená el seguimiento",
      body: "Revisá el pipeline y dejá notas o estado para sostener el próximo vencimiento sin ruido.",
      href: "/saved",
      cta: "Abrir pipeline",
      complete: savedCount > 0,
      evidence: savedCount > 0 ? "Ya existe pipeline para operar." : "El pipeline se activa cuando guardás la primera licitación.",
    },
  ];

  return (
    <PageShell variant="workspace" className="workspace-shell account-page page-screen page-screen--account">
      {currentUser.role !== "admin" ? (
        <OnboardingWizard
          variant="company"
          forceOpen={onboarding}
          content={{
            steps: companyOnboardingSteps,
          }}
        />
      ) : null}
      <SiteHeader
        section="account"
        currentUserName={currentUser.full_name}
        currentUserRole={currentUser.role}
      />

      <section className="workspace-header account-header">
        <div>
          <span className="eyebrow">Mi cuenta</span>
          <h1>Alertas, identidad y canales.</h1>
          <p>
            {onboarding
              ? "Antes de operar, dejá resuelto cómo y por dónde te va a avisar el sistema."
              : "Configurá tu identidad y los canales que realmente querés usar fuera del dashboard."}
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
          <span>Canales disponibles</span>
          <strong>{configuredChannels.join(" · ")}</strong>
        </article>
        <article>
          <span>Umbral</span>
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
          <h2>Lectura rápida de la cuenta</h2>

          <div className="onboarding-proof-list">
            <article>
              <strong>Canales activos</strong>
              <p>
                {alertChannelReady
                  ? configuredChannels.join(", ")
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
            <article>
              <strong>Pipeline</strong>
              <p>{savedCount > 0 ? `${savedCount} licitaciones ya están en seguimiento.` : "Todavía no hay oportunidades guardadas."}</p>
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
