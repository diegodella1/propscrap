import { AlertOpsPanel } from "./alert-ops-panel";
import { AutomationSettingsPanel } from "./automation-settings-panel";
import { OnboardingWizard, type OnboardingStep } from "./onboarding-wizard";
import { SiteHeader } from "./site-header";
import { SourceEditorList } from "./source-editor-list";
import { SourceForm } from "./source-form";
import { UserEditorList } from "./user-editor-list";
import type { AdminAuditEvent, Alert, AutomationSettings, Source, SourceRun, User, WhatsappOutboxMessage } from "../lib/api";

type Props = {
  currentUserName: string;
  sourceRuns: SourceRun[];
  alerts: Alert[];
  users: User[];
  sources: Source[];
  automationSettings: AutomationSettings;
  whatsappOutbox: WhatsappOutboxMessage[];
  auditEvents: AdminAuditEvent[];
};

export function PlatformAdminPage({
  currentUserName,
  sourceRuns,
  alerts,
  users,
  sources,
  automationSettings,
  whatsappOutbox,
  auditEvents,
}: Props) {
  const sourceMap = new Map(sources.map((source) => [source.id, source]));
  const userMap = new Map(users.map((user) => [user.id, user]));
  const activeSources = sources.filter((source) => source.is_active).length;
  const healthyRuns = sourceRuns.filter((run) => run.status === "success" || run.status === "completed").length;
  const failedRuns = sourceRuns.filter((run) => run.status === "failed" || run.status === "error").length;
  const pendingAlerts = alerts.filter((alert) => alert.delivery_status !== "delivered").length;
  const deliveredAlerts = alerts.filter((alert) => alert.delivery_status === "delivered").length;
  const connectorReady = sources.filter((source) => source.connector_available).length;
  const recentRuns = sourceRuns.slice(0, 5);
  const recentAlerts = alerts.slice(0, 10);
  const activeAdmins = users.filter((user) => user.role === "admin" && user.is_active).length;
  const activeManagers = users.filter((user) => user.role === "manager" && user.is_active).length;
  const activeAnalysts = users.filter((user) => user.role === "analyst" && user.is_active).length;
  const inactiveSources = sources.length - activeSources;
  const sourcesWithoutConnector = sources.length - connectorReady;
  const latestRun = recentRuns[0] ?? null;
  const latestAuditEvent = auditEvents[0] ?? null;
  const platformStatus =
    failedRuns > 0 ? "Atención operativa" : pendingAlerts > 0 ? "Operación en cola" : "Operación estable";
  const llmReady = automationSettings.openai_api_key_configured && Boolean(automationSettings.openai_model);
  const deliveryReady = Boolean(
    (automationSettings.email_delivery_enabled && automationSettings.resend_api_key_configured) ||
      automationSettings.whatsapp_enabled ||
      automationSettings.telegram_enabled,
  );
  const adminOnboardingSteps: OnboardingStep[] = [
    {
      id: "sources",
      title: "Revisá las fuentes base",
      body: "Confirmá que las fuentes centrales estén activas y con conector disponible antes de abrir el campo.",
      href: "/admin/platform#admin-sources",
      cta: "Ir a fuentes",
      complete: activeSources > 0 && connectorReady > 0,
      evidence:
        activeSources > 0
          ? `${activeSources} fuentes activas y ${connectorReady} conectores listos.`
          : "Todavía no hay fuentes activas suficientes para operar.",
    },
    {
      id: "llm",
      title: "Configurá IA y scoring",
      body: "Dejá API key, modelo y prompt maestro en condiciones para resumen y ranking.",
      href: "/admin/platform#admin-automation",
      cta: "Ir a IA",
      complete: llmReady,
      evidence: llmReady
        ? `Modelo activo: ${automationSettings.openai_model}.`
        : "Falta completar API key o modelo de OpenAI.",
    },
    {
      id: "delivery",
      title: "Activá el delivery operativo",
      body: "Resend, WhatsApp o Telegram tienen que estar listos para alertas fuera de la web.",
      href: "/admin/platform#admin-delivery",
      cta: "Ir a delivery",
      complete: deliveryReady,
      evidence: deliveryReady
        ? "Hay al menos un canal de entrega habilitado."
        : "Todavía no hay un canal de delivery externo listo.",
    },
    {
      id: "users",
      title: "Verificá acceso y auditoría",
      body: "Revisá usuarios, roles y trazabilidad administrativa antes de mostrarlo a cliente.",
      href: "/admin/platform#admin-users",
      cta: "Ir a usuarios",
      complete: users.length > 0 && auditEvents.length > 0,
      evidence:
        users.length > 0
          ? `${users.length} usuarios cargados y ${auditEvents.length} eventos de auditoría.`
          : "Todavía no hay usuarios globales para validar ABM.",
    },
  ];

  return (
    <main className="page-shell workspace-shell">
      <OnboardingWizard
        variant="superadmin"
        content={{
          steps: adminOnboardingSteps,
        }}
      />
      <SiteHeader section="admin" currentUserName={currentUserName} currentUserRole="admin" />

      <section className="workspace-header admin-header">
        <div>
          <span className="eyebrow">Superadmin</span>
          <h1>Consola de plataforma.</h1>
          <p>Gobierno de fuentes, automatización, alertas y acceso global.</p>
        </div>
        <div className="workspace-header-actions">
          <a href="#admin-sources" className="button-secondary">
            Ir a fuentes
          </a>
          <a href="#admin-automation" className="button-primary">
            Ir a automatización
          </a>
        </div>
      </section>

      <section className="dashboard-executive-band admin-summary-band workspace-kpi-band">
        <article>
          <span>Fuentes activas</span>
          <strong>{activeSources}</strong>
        </article>
        <article>
          <span>Conectores listos</span>
          <strong>{connectorReady}</strong>
        </article>
        <article>
          <span>Runs sanos</span>
          <strong>{healthyRuns}</strong>
        </article>
        <article>
          <span>Alertas pendientes</span>
          <strong>{pendingAlerts}</strong>
        </article>
      </section>

      <section className="admin-shell-grid admin-workbench-grid">
        <aside className="panel admin-rail">
          <div className="admin-rail-block">
            <span className="section-kicker">Estado</span>
            <div className="ops-status-card">
              <strong>{platformStatus}</strong>
              <p>
                {failedRuns > 0
                  ? `Hay ${failedRuns} corridas con error que conviene revisar antes de sumar nuevas fuentes.`
                  : pendingAlerts > 0
                    ? `La ingesta está sana, pero hay ${pendingAlerts} alertas todavía en cola.`
                    : "Fuentes, matching y delivery están sin señales críticas inmediatas."}
              </p>
            </div>
          </div>

          <div className="admin-rail-block">
            <span className="section-kicker">Secciones</span>
            <nav className="admin-anchor-nav" aria-label="Navegación interna de superadmin">
              <a href="#admin-overview">Resumen</a>
              <a href="#admin-sources">Fuentes</a>
              <a href="#admin-automation">Automatización</a>
              <a href="#admin-delivery">Entregas</a>
              <a href="#admin-audit">Auditoría</a>
              <a href="#admin-users">Usuarios</a>
            </nav>
          </div>

          <div className="admin-rail-block">
            <span className="section-kicker">Qué revisar primero</span>
            <div className="admin-quick-list">
              <article>
                <strong>Salud de fuentes</strong>
                <p>{inactiveSources} inactivas y {sourcesWithoutConnector} sin conector disponible.</p>
              </article>
              <article>
                <strong>LLM y automatización</strong>
                <p>Confirmá ciclo activo, modelo, prompt maestro y credenciales antes de correr jobs manuales.</p>
              </article>
              <article>
                <strong>Usuarios y ABM</strong>
                <p>{users.length} cuentas globales entre admins, managers y analistas.</p>
              </article>
            </div>
          </div>

          <div className="admin-rail-block">
            <span className="section-kicker">Actividad reciente</span>
            <div className="admin-status-list">
              {recentRuns.length ? (
                recentRuns.slice(0, 3).map((run) => (
                  <article key={run.id}>
                    <strong>{sourceMap.get(run.source_id)?.name ?? `Fuente #${run.source_id}`}</strong>
                    <p>
                      {run.status} · {new Date(run.started_at).toLocaleString("es-AR")}
                    </p>
                  </article>
                ))
              ) : (
                <article>
                  <strong>Sin actividad reciente</strong>
                  <p>Todavía no hay corridas registradas.</p>
                </article>
              )}
            </div>
          </div>
        </aside>

        <div className="admin-content-stack">
          <section id="admin-overview" className="admin-section-stack">
            <div className="results-header">
              <div>
                <span className="section-kicker">Resumen</span>
                <h2>Consola operativa de plataforma</h2>
              </div>
              <p>Ordená prioridades, ejecutá cambios con criterio y verificá si discovery, matching y entrega están sanos.</p>
            </div>

            <div className="ops-priority-grid">
              <article className="panel ops-priority-card ops-priority-card-strong">
                <span className="section-kicker">Prioridad ahora</span>
                <h3>{failedRuns > 0 ? "Revisar corridas con error" : pendingAlerts > 0 ? "Destrabar entrega" : "Expandir cobertura"}</h3>
                <p>
                  {failedRuns > 0
                    ? "Empezá por delivery y corridas recientes. Si falla la ingesta, todo lo demás queda desalineado."
                    : pendingAlerts > 0
                      ? "La infraestructura central respondió, pero todavía quedan entregas pendientes para usuarios."
                      : "Sin incidentes inmediatos. El siguiente foco razonable es sumar o ajustar fuentes útiles."}
                </p>
              </article>
              <article className="panel ops-priority-card">
                <span className="section-kicker">Último run</span>
                <h3>{latestRun ? sourceMap.get(latestRun.source_id)?.name ?? `Fuente #${latestRun.source_id}` : "Sin runs recientes"}</h3>
                <p>
                  {latestRun
                    ? `${latestRun.status} · ${new Date(latestRun.started_at).toLocaleString("es-AR")}`
                    : "Todavía no hubo corridas registradas."}
                </p>
              </article>
              <article className="panel ops-priority-card">
                <span className="section-kicker">Última auditoría</span>
                <h3>{latestAuditEvent ? latestAuditEvent.action : "Sin eventos"}</h3>
                <p>
                  {latestAuditEvent
                    ? new Date(latestAuditEvent.created_at).toLocaleString("es-AR")
                    : "Cuando haya cambios sensibles, van a aparecer acá."}
                </p>
              </article>
            </div>

            <div className="admin-overview-grid">
              <article className="panel admin-overview-card">
                <span className="section-kicker">Discovery</span>
                <h3>Fuentes y conectores</h3>
                <p>Alta, edición y gobierno del inventario de orígenes, conectores y modos de parseo.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Motor</span>
                <h3>LLM y automatización</h3>
                <p>Ciclo de ingesta, modelo, prompt maestro y credenciales sensibles de la plataforma.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Entrega</span>
                <h3>Alertas y dispatch</h3>
                <p>Generación de alertas, colas, outbox y verificación del contenido final enviado.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Acceso</span>
                <h3>Usuarios globales y ABM</h3>
                <p>Control de roles, altas, bajas y configuración transversal de cuentas de empresas.</p>
              </article>
            </div>

            <div className="admin-ops-snapshot">
              <article className="panel admin-overview-card">
                <span className="section-kicker">Fuentes</span>
                <h3>{activeSources} activas / {sources.length} totales</h3>
                <p>{connectorReady} con conector listo para correr.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Runs</span>
                <h3>{healthyRuns} sanos / {failedRuns} con error</h3>
                <p>Último foco: estabilidad del discovery y parsing.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Alertas</span>
                <h3>{pendingAlerts} pendientes / {deliveredAlerts} entregadas</h3>
                <p>Monitoreo rápido del circuito de entrega.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Roles</span>
                <h3>{activeAdmins} admin · {activeManagers} manager · {activeAnalysts} analyst</h3>
                <p>Distribución actual de acceso operativo.</p>
              </article>
            </div>
          </section>

          <section id="admin-sources" className="admin-section-stack">
            <div className="results-header">
              <div>
                <span className="section-kicker">Fuentes</span>
                <h2>Alta e inventario de orígenes</h2>
              </div>
              <p>Primero se da de alta el origen. Después se ajusta modo de scraping, conector, estado y configuración.</p>
            </div>

            <div className="admin-control-grid admin-main-grid">
              <article className="panel dispatch-panel">
                <div className="results-header">
                  <div>
                    <span className="section-kicker">Crear</span>
                    <h2>Nueva fuente</h2>
                  </div>
                  <p>Bloque corto para alta inicial. Lo fino se ajusta después en el inventario.</p>
                </div>
                <SourceForm />
              </article>

              <article className="panel dispatch-panel">
                <div className="results-header">
                  <div>
                    <span className="section-kicker">Editar</span>
                    <h2>Fuentes existentes</h2>
                  </div>
                  <p>Cada bloque concentra estado, URL base, conector y configuración editable.</p>
                </div>
                <SourceEditorList sources={sources} />
              </article>
            </div>
          </section>

          <section id="admin-automation" className="admin-section-stack">
            <div className="results-header">
              <div>
                <span className="section-kicker">Automatización</span>
                <h2>Ciclo global, IA y canales comerciales</h2>
              </div>
              <p>Todo lo sensible de operación y captación pública vive acá, con una secuencia más clara.</p>
            </div>

            <div className="admin-control-grid">
              <article className="panel dispatch-panel">
                <AutomationSettingsPanel settings={automationSettings} />
              </article>
              <article className="panel dispatch-panel">
                <AlertOpsPanel />
              </article>
            </div>
          </section>

          <section id="admin-delivery" className="admin-section-stack">
            <div className="results-header">
              <div>
                <span className="section-kicker">Entregas</span>
                <h2>Corridas, cola y outbox</h2>
              </div>
              <p>Monitoreo rápido para ver qué corrió, qué quedó pendiente y qué contenido salió hacia usuarios.</p>
            </div>

            <div className="results-ribbon">
              <span>{recentRuns.length} runs recientes</span>
              <span>{pendingAlerts} alertas pendientes</span>
              <span>{whatsappOutbox.length} mensajes en outbox</span>
              <span>{deliveredAlerts} alertas entregadas</span>
            </div>

            <div className="admin-delivery-kpis">
              <article className="panel admin-overview-card">
                <span className="section-kicker">Runs recientes</span>
                <h3>{recentRuns.length}</h3>
                <p>{failedRuns > 0 ? `${failedRuns} con error reciente.` : "Sin errores recientes."}</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Cola</span>
                <h3>{pendingAlerts}</h3>
                <p>Alertas todavía no entregadas.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Outbox</span>
                <h3>{whatsappOutbox.length}</h3>
                <p>Mensajes generados para inspección operativa.</p>
              </article>
            </div>

            <article className="panel table-panel table-panel-upgraded">
              <div className="results-header">
                <div>
                  <span className="section-kicker">WhatsApp mock</span>
                  <h2>Outbox generado</h2>
                </div>
                <p>Revisá el contenido final del mensaje aunque el proveedor real todavía no esté conectado.</p>
              </div>
              {whatsappOutbox.length === 0 ? (
                <p className="muted">Todavía no hay mensajes en el outbox mock.</p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Destino</th>
                        <th>Proveedor</th>
                        <th>Mensaje</th>
                      </tr>
                    </thead>
                    <tbody>
                      {whatsappOutbox.slice(0, 8).map((message) => (
                        <tr key={message.id}>
                          <td>{message.created_at ? new Date(message.created_at).toLocaleString("es-AR") : "n/d"}</td>
                          <td>{message.to || "n/d"}</td>
                          <td>{message.provider}</td>
                          <td>{message.body}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </article>

            <div className="admin-data-grid">
              <article className="panel table-panel table-panel-upgraded">
                <div className="results-header">
                  <div>
                    <span className="section-kicker">Corridas</span>
                    <h2>Últimos runs</h2>
                  </div>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Fuente</th>
                        <th>Status</th>
                        <th>Items</th>
                        <th>Fecha</th>
                      </tr>
                    </thead>
                    <tbody>
                      {sourceRuns.slice(0, 12).map((run) => (
                        <tr key={run.id}>
                          <td>{run.id}</td>
                          <td>{sourceMap.get(run.source_id)?.name ?? `#${run.source_id}`}</td>
                          <td>{run.status}</td>
                          <td>{run.items_new} / {run.items_found}</td>
                          <td>{new Date(run.started_at).toLocaleString("es-AR")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>

              <article className="panel table-panel table-panel-upgraded">
                <div className="results-header">
                  <div>
                    <span className="section-kicker">Alertas</span>
                    <h2>Cola reciente</h2>
                  </div>
                </div>
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>ID</th>
                        <th>Tender</th>
                        <th>Tipo</th>
                        <th>Canal</th>
                        <th>Intentos</th>
                        <th>Programada</th>
                      </tr>
                    </thead>
                    <tbody>
                      {recentAlerts.map((alert) => (
                        <tr key={alert.id}>
                          <td>{alert.id}</td>
                          <td>{alert.tender_id}</td>
                          <td>{alert.alert_type}</td>
                          <td>{alert.delivery_channel} / {alert.delivery_status}</td>
                          <td>
                            {alert.delivery_attempts}
                            {alert.last_error_message ? ` · ${alert.last_error_message}` : ""}
                          </td>
                          <td>{new Date(alert.scheduled_for).toLocaleString("es-AR")}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </article>
            </div>
          </section>

          <section id="admin-audit" className="admin-section-stack">
            <article className="panel table-panel table-panel-upgraded">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Auditoría</span>
                  <h2>Eventos administrativos recientes</h2>
                </div>
                <p>Registro de acciones sensibles ejecutadas por platform admins y jobs manuales.</p>
              </div>
              {auditEvents.length === 0 ? (
                <p className="muted">Todavía no hay eventos de auditoría registrados.</p>
              ) : (
                <div className="table-wrap">
                  <table>
                    <thead>
                      <tr>
                        <th>Fecha</th>
                        <th>Actor</th>
                        <th>Acción</th>
                        <th>Detalle</th>
                      </tr>
                    </thead>
                    <tbody>
                      {auditEvents.slice(0, 20).map((event) => (
                        <tr key={event.id}>
                          <td>{new Date(event.created_at).toLocaleString("es-AR")}</td>
                          <td>
                            {event.actor_user_id
                              ? userMap.get(event.actor_user_id)?.email ?? `user:${event.actor_user_id}`
                              : "system"}
                          </td>
                          <td>{event.action}</td>
                          <td>{event.detail_json ? JSON.stringify(event.detail_json) : "{}"}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </article>
          </section>

          <section id="admin-users" className="admin-section-stack">
            <article className="panel table-panel table-panel-upgraded">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Usuarios</span>
                  <h2>Usuarios de todas las empresas</h2>
                </div>
                <p>ABM global de cuentas y permisos, separado de fuentes, LLM y automatización.</p>
              </div>
              <UserEditorList users={users} canManagePlatformRoles />
            </article>
          </section>
        </div>
      </section>
    </main>
  );
}
