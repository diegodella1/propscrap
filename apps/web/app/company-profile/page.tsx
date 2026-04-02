import { redirect } from "next/navigation";

import { CompanyProfileForm } from "../../components/company-profile-form";
import { SiteHeader } from "../../components/site-header";
import { getCurrentUserFromSession, getMyCompanyProfileFromSession } from "../../lib/session";

export default async function CompanyProfilePage() {
  const currentUser = await getCurrentUserFromSession();
  if (!currentUser) {
    redirect("/login");
  }

  const profile = await getMyCompanyProfileFromSession();

  return (
    <main className="page-shell">
      <SiteHeader section="profile" currentUserName={currentUser.full_name} />

      <section className="hero hero-app about-hero">
        <div>
          <span className="eyebrow">Perfil de empresa</span>
          <h1>Definí qué entiende la plataforma por una oportunidad relevante.</h1>
        </div>
        <p>
          Este perfil controla keywords, sectores, jurisdicciones, compradores y umbrales. Cuando cambia, cambia el
          criterio con el que se ordena toda la cola.
        </p>
      </section>

      {profile ? (
        <section className="admin-control-grid admin-profile-layout">
          <article className="panel dispatch-panel">
            <div className="results-header">
              <div>
                <span className="section-kicker">Configuración</span>
                <h2>Definí qué oportunidades te importan</h2>
              </div>
              <p>Guardá y el sistema vuelve a calcular relevancia usando el perfil comercial de tu empresa.</p>
            </div>
            <CompanyProfileForm
              profile={profile}
              saveUrl="/api/v1/me/company-profile"
              matchUrl={`/api/v1/jobs/match-all?profile_id=${profile.id}`}
            />
          </article>

          <article className="panel dispatch-panel">
            <div className="results-header">
              <div>
                <span className="section-kicker">Qué impacta</span>
                <h2>Cómo prioriza tus licitaciones</h2>
              </div>
            </div>
            <div className="source-stack">
              <article className="source-card source-card-strong">
                <strong>{profile.company_name}</strong>
                <p>{profile.company_description}</p>
              </article>
              <article className="source-card">
                <span className="section-kicker">Keywords positivas</span>
                <p>{(profile.include_keywords ?? []).join(", ") || "Sin keywords positivas"}</p>
              </article>
              <article className="source-card">
                <span className="section-kicker">Keywords negativas</span>
                <p>{(profile.exclude_keywords ?? []).join(", ") || "Sin keywords negativas"}</p>
              </article>
              <article className="source-card">
                <span className="section-kicker">Jurisdicciones y compradores</span>
                <p>
                  {(profile.jurisdictions ?? []).join(", ") || "Sin jurisdicciones"} ·{" "}
                  {(profile.preferred_buyers ?? []).join(", ") || "Sin compradores"}
                </p>
              </article>
            </div>
          </article>
        </section>
      ) : null}
    </main>
  );
}
