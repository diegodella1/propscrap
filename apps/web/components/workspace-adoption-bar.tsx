import Link from "next/link";

import { fetchSavedTenders } from "../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession, getMyCompanyProfileFromSession } from "../lib/session";

function buildAdoptionState(params: {
  hasAlertChannel: boolean;
  hasProfile: boolean;
  savedCount: number;
}) {
  const steps = [
    {
      id: "alerts",
      label: "Canal",
      title: "Configurá alertas",
      href: "/mi-cuenta",
      cta: "Ir a mi cuenta",
      complete: params.hasAlertChannel,
    },
    {
      id: "profile",
      label: "Perfil",
      title: "Completá el perfil comercial",
      href: "/company-profile",
      cta: "Ir a empresa",
      complete: params.hasProfile,
    },
    {
      id: "pipeline",
      label: "Pipeline",
      title: "Guardá la primera licitación",
      href: "/dashboard",
      cta: "Ir a discovery",
      complete: params.savedCount > 0,
    },
  ];

  const completed = steps.filter((step) => step.complete).length;
  const nextStep = steps.find((step) => !step.complete) ?? steps[steps.length - 1];

  return { completed, nextStep, steps };
}

export async function WorkspaceAdoptionBar() {
  const [currentUser, cookieHeader, profile] = await Promise.all([
    getCurrentUserFromSession(),
    getCookieHeaderFromSession(),
    getMyCompanyProfileFromSession(),
  ]);

  if (!currentUser || currentUser.role === "admin") {
    return null;
  }

  const saved = await fetchSavedTenders(cookieHeader || undefined).catch(() => null);
  const channels = currentUser.alert_preferences_json?.channels ?? ["dashboard"];
  const hasAlertChannel =
    channels.includes("email") ||
    (channels.includes("whatsapp") && Boolean(currentUser.whatsapp_number)) ||
    (channels.includes("telegram") && Boolean(currentUser.telegram_chat_id));
  const hasProfile = Boolean(
    profile?.company_description?.trim() &&
      ((profile?.include_keywords?.length ?? 0) > 0 ||
        (profile?.preferred_buyers?.length ?? 0) > 0 ||
        (profile?.jurisdictions?.length ?? 0) > 0),
  );
  const savedCount = saved?.total ?? 0;
  const adoption = buildAdoptionState({
    hasAlertChannel,
    hasProfile,
    savedCount,
  });

  return (
    <section className="workspace-adoption-bar">
      <div className="workspace-adoption-main">
        <span className="section-kicker">Prueba 30 días</span>
        <strong>
          {adoption.completed}/3 hitos activos. {adoption.completed === 3 ? "La base de uso ya está armada." : `Siguiente paso: ${adoption.nextStep.title}.`}
        </strong>
        <p>
          La adopción real llega cuando el equipo define alertas, arma el perfil comercial y mete oportunidades reales en el pipeline.
        </p>
      </div>

      <div className="workspace-adoption-steps">
        {adoption.steps.map((step) => (
          <article key={step.id} className={`workspace-adoption-step${step.complete ? " workspace-adoption-step--complete" : ""}`}>
            <span>{step.label}</span>
            <strong>{step.title}</strong>
          </article>
        ))}
      </div>

      <div className="workspace-adoption-actions">
        <Link href={adoption.nextStep.href} className="button-primary">
          {adoption.nextStep.cta}
        </Link>
        <Link href="/saved" className="button-secondary">
          Ver seguimiento
        </Link>
      </div>
    </section>
  );
}
