import Link from "next/link";

import { CompanyAlertSettingsForm } from "./company-alert-settings-form";
import { SiteHeader } from "./site-header";
import { UserEditorList } from "./user-editor-list";
import type { CompanyProfile, User } from "../lib/api";

type Props = {
  currentUserName: string;
  companyProfile: CompanyProfile;
  users: User[];
};

export function CompanyAdminPage({ currentUserName, companyProfile, users }: Props) {
  const defaults = companyProfile.alert_preferences_json ?? {};
  const whatsappReady = users.filter((user) => user.whatsapp_opt_in && user.whatsapp_number).length;
  const telegramReady = users.filter((user) => user.telegram_opt_in && user.telegram_chat_id).length;
  const emailReady = users.filter((user) => (user.alert_preferences_json?.channels ?? []).includes("email")).length;

  return (
    <main className="page-shell workspace-shell page-screen page-screen--admin-company">
      <SiteHeader section="admin" currentUserName={currentUserName} currentUserRole="manager" />

      <section className="workspace-header admin-header company-admin-header">
        <div>
          <span className="eyebrow">Administración de empresa</span>
          <h1>Equipo y perfil comercial.</h1>
          <p>Gestión compacta del equipo y del criterio comercial de la empresa.</p>
        </div>
        <div className="workspace-header-actions">
          <Link href="/company-profile" className="button-primary">
            Perfil comercial
          </Link>
          <Link href="/dashboard" className="button-secondary">
            Workspace
          </Link>
        </div>
      </section>

      <section className="dashboard-executive-band admin-summary-band company-admin-summary-band workspace-kpi-band">
        <article>
          <span>Usuarios</span>
          <strong>{users.length}</strong>
        </article>
        <article>
          <span>Ámbito</span>
          <strong>1 empresa</strong>
        </article>
        <article>
          <span>Permiso</span>
          <strong>Manager</strong>
        </article>
        <article>
          <span>Alcance</span>
          <strong>Equipo + perfil</strong>
        </article>
      </section>

      <section className="admin-shell-grid company-admin-shell-grid admin-workbench-grid">
        <aside className="panel admin-rail">
          <div className="admin-rail-block">
            <span className="section-kicker">Qué hacer acá</span>
            <div className="admin-quick-list">
              <article>
                <strong>Cargar la empresa</strong>
                <p>Partir del CUIT y completar el perfil comercial usable para matching.</p>
              </article>
              <article>
                <strong>Ordenar alertas</strong>
                <p>Definir aviso por email, WhatsApp y dashboard según cada usuario.</p>
              </article>
              <article>
                <strong>Seguir licitaciones</strong>
                <p>Guardar oportunidades y trabajar fechas, notas y próximos pasos.</p>
              </article>
            </div>
          </div>
        </aside>

        <div className="admin-content-stack">
          <section className="dashboard-focus-grid admin-focus-grid company-admin-focus-grid">
            <article className="panel dispatch-panel">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Perfil comercial</span>
                  <h2>Empresa, dossier y criterios de búsqueda</h2>
                </div>
                <p>CUIT, descripción, keywords, buyers, jurisdicciones y documentación base impactan directamente qué entra al radar.</p>
              </div>
              <div className="hero-actions">
                <Link href="/company-profile" className="button-primary">
                  Editar perfil comercial
                </Link>
                <Link href="/mi-cuenta" className="button-secondary">
                  Mis canales
                </Link>
                <Link href="/dashboard" className="button-secondary">
                  Ver oportunidades
                </Link>
              </div>
            </article>

            <article className="panel dispatch-panel onboarding-companion">
              <span className="section-kicker">Alcance del rol</span>
              <h2>Qué puede hacer un admin de empresa</h2>
              <div className="admin-overview-grid">
                <article>
                  <strong>Equipo</strong>
                  <p>Alta, baja y modificación de usuarios de su propia empresa.</p>
                </article>
                <article>
                  <strong>Matching</strong>
                  <p>Definir keywords, buyers y fuentes objetivo para mejorar el discovery.</p>
                </article>
                <article>
                  <strong>Seguimiento</strong>
                  <p>Guardar licitaciones, trabajar fechas y sostener una cartera activa.</p>
                </article>
                <article>
                  <strong>Límite</strong>
                  <p>No accede a otras empresas ni a configuración global de fuentes, LLM o automatización.</p>
                </article>
              </div>
            </article>
          </section>

          <section className="admin-section-stack">
            <article className="panel table-panel table-panel-upgraded">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Tablero</span>
                  <h2>Estado actual de alertas de la empresa</h2>
                </div>
                <p>Vista rápida para entender si la política de alertas ya puede funcionar en una demo real.</p>
              </div>
              <section className="dashboard-executive-band workspace-kpi-band">
                <article>
                  <span>Score mínimo</span>
                  <strong>{defaults.min_score ?? 60}</strong>
                </article>
                <article>
                  <span>WhatsApp listos</span>
                  <strong>{whatsappReady}</strong>
                </article>
                <article>
                  <span>Email activos</span>
                  <strong>{emailReady}</strong>
                </article>
                <article>
                  <span>Telegram listos</span>
                  <strong>{telegramReady}</strong>
                </article>
              </section>
              <div className="admin-overview-grid">
                <article className="panel admin-overview-card">
                  <span className="section-kicker">Discovery</span>
                  <h3>{defaults.receive_relevant ? "Activo" : "Pausado"}</h3>
                  <p>Nuevas licitaciones con score por encima del umbral definido por la empresa.</p>
                </article>
                <article className="panel admin-overview-card">
                  <span className="section-kicker">Deadlines</span>
                  <h3>{defaults.receive_deadlines ? "Activo" : "Pausado"}</h3>
                  <p>
                    {defaults.deadline_only_for_saved
                      ? "Recordatorios solo sobre licitaciones guardadas o en seguimiento."
                      : "Recordatorios sobre cualquier licitación con fechas detectadas."}
                  </p>
                </article>
                <article className="panel admin-overview-card">
                  <span className="section-kicker">Offsets</span>
                  <h3>{(defaults.deadline_offsets_hours ?? [168, 72, 24]).join(" · ")}h</h3>
                  <p>Anticipaciones base para recordatorios por fechas críticas detectadas en scraping o enriquecimiento.</p>
                </article>
              </div>
            </article>

            <article className="panel table-panel table-panel-upgraded">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Alertas</span>
                  <h2>Reglas default de la empresa</h2>
                </div>
                <p>Definí score mínimo para nuevas licitaciones y recordatorios sobre oportunidades guardadas.</p>
              </div>
              <CompanyAlertSettingsForm profile={companyProfile} />
            </article>

            <article className="panel table-panel table-panel-upgraded">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Equipo</span>
                  <h2>Usuarios de la empresa</h2>
                </div>
                <p>Mantené una operación compartida y trazable, sin depender de una sola persona.</p>
              </div>
              <UserEditorList users={users} />
            </article>
          </section>
        </div>
      </section>
    </main>
  );
}
