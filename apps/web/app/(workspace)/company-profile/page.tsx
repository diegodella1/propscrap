import { redirect } from "next/navigation";

import { CompanyProfileForm } from "../../../components/company-profile-form";
import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";
import { getCurrentUserFromSession, getMyCompanyProfileFromSession } from "../../../lib/session";

export default async function CompanyProfilePage() {
  const currentUser = await getCurrentUserFromSession();
  if (!currentUser) {
    redirect("/login");
  }

  const profile = await getMyCompanyProfileFromSession();

  return (
    <PageShell variant="workspace" className="workspace-shell page-screen page-screen--company-profile">
      <SiteHeader
        section="profile"
        currentUserName={currentUser.full_name}
        currentUserRole={currentUser.role}
      />

      <section className="workspace-header profile-header">
        <div>
          <span className="eyebrow">Perfil de empresa</span>
          <h1>Criterio comercial.</h1>
          <p>Definí qué licitación entra al radar, con qué señales y con qué nivel de exigencia.</p>
        </div>
        <div className="workspace-header-actions">
          <a href="#company-profile-form" className="button-primary">
            Editar perfil
          </a>
        </div>
      </section>

      {profile ? (
        <>
          <section className="dashboard-executive-band profile-summary-band workspace-kpi-band">
            <article>
              <span>CUIT</span>
              <strong>{profile.cuit ?? "n/d"}</strong>
            </article>
            <article>
              <span>Score mínimo</span>
              <strong>{profile.alert_preferences_json?.min_score ?? 60}</strong>
            </article>
            <article>
              <span>Sectores</span>
              <strong>{profile.sectors?.length ?? 0}</strong>
            </article>
            <article>
              <span>Compradores</span>
              <strong>{profile.preferred_buyers?.length ?? 0}</strong>
            </article>
          </section>

          <section className="ops-priority-grid profile-workbench-grid">
            <article className="panel ops-priority-card ops-priority-card-strong">
              <span className="section-kicker">Matching</span>
              <h3>El perfil define el ranking inicial.</h3>
              <p>La plataforma cruza identidad, descripción, buyers, keywords, exclusiones y umbral para priorizar qué vale mirar primero.</p>
            </article>
            <article className="panel ops-priority-card">
              <span className="section-kicker">Señales</span>
              <h3>Menos ruido, mejores alertas</h3>
              <p>Si el perfil está bien armado, mejora discovery, ranking inicial y la calidad de alertas por dashboard, email y Telegram.</p>
            </article>
          </section>

          <section className="admin-control-grid admin-profile-layout profile-main-grid workspace-detail-grid">
            <article className="panel dispatch-panel">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Configuración comercial</span>
                  <h2>Reglas de matching</h2>
                </div>
                <p>Al guardar, la plataforma recalcula relevancia con estas reglas.</p>
              </div>
              <CompanyProfileForm
                profile={profile}
                saveUrl="/api/v1/me/company-profile"
                matchUrl="/api/v1/me/company-profile/rematch"
              />
            </article>

            <article className="panel dispatch-panel">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Resumen</span>
                  <h2>Lo que hoy usa la plataforma</h2>
                </div>
              </div>

              <div className="source-stack">
                <article className="source-card source-card-strong">
                  <strong>{profile.company_name}</strong>
                  <p>{profile.company_description || "Todavía no cargaste una descripción comercial."}</p>
                </article>
                <article className="source-card">
                  <span className="section-kicker">Identidad legal</span>
                  <p>{profile.legal_name ?? "Sin razón social legal"}</p>
                </article>
                <article className="source-card">
                  <span className="section-kicker">Keywords positivas</span>
                  <p>{(profile.include_keywords ?? []).join(", ") || "Sin keywords positivas"}</p>
                </article>
                <article className="source-card">
                  <span className="section-kicker">Exclusiones</span>
                  <p>{(profile.exclude_keywords ?? []).join(", ") || "Sin exclusiones definidas"}</p>
                </article>
                <article className="source-card">
                  <span className="section-kicker">Cobertura objetivo</span>
                  <p>
                    {(profile.jurisdictions ?? []).join(", ") || "Sin jurisdicciones"} ·{" "}
                    {(profile.preferred_buyers ?? []).join(", ") || "Sin buyers definidos"}
                  </p>
                </article>
                <article className="source-card">
                  <span className="section-kicker">Base legal</span>
                  <p>
                    {profile.company_data_source ?? "Sin fuente legal"}
                    {profile.company_data_updated_at
                      ? ` · ${new Date(profile.company_data_updated_at).toLocaleString("es-AR")}`
                      : ""}
                  </p>
                </article>
              </div>
            </article>
          </section>
        </>
      ) : null}
    </PageShell>
  );
}
