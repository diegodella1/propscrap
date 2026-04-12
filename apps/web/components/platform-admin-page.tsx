import { AlertOpsPanel } from "./alert-ops-panel";
import { AutomationSettingsPanel } from "./automation-settings-panel";
import { SiteHeader } from "./site-header";
import { SourceEditorList } from "./source-editor-list";
import { SourceForm } from "./source-form";
import { UserEditorList } from "./user-editor-list";
import type { Alert, AutomationSettings, Source, SourceRun, User, WhatsappOutboxMessage } from "../lib/api";

type Props = {
  currentUserName: string;
  sourceRuns: SourceRun[];
  alerts: Alert[];
  users: User[];
  sources: Source[];
  automationSettings: AutomationSettings;
  whatsappOutbox: WhatsappOutboxMessage[];
};

export function PlatformAdminPage({
  currentUserName,
  sourceRuns,
  alerts,
  users,
  sources,
  automationSettings,
  whatsappOutbox,
}: Props) {
  const sourceMap = new Map(sources.map((source) => [source.id, source]));
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

  return (
    <main className="page-shell">
      <SiteHeader section="admin" currentUserName={currentUserName} currentUserRole="admin" />

      <section className="hero hero-app admin-hero">
        <div>
          <span className="eyebrow">Superadmin</span>
          <h1>Consola de plataforma.</h1>
        </div>
        <p>Estado global, puntos de intervención y acceso a configuración crítica.</p>
      </section>

      <section className="dashboard-executive-band admin-summary-band">
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

      <section className="admin-shell-grid">
        <aside className="panel admin-rail">
          <div className="admin-rail-block">
            <span className="section-kicker">Secciones</span>
            <nav className="admin-anchor-nav" aria-label="Navegación interna de superadmin">
              <a href="#admin-overview">Resumen</a>
              <a href="#admin-sources">Fuentes</a>
              <a href="#admin-automation">Automatización</a>
              <a href="#admin-delivery">Entregas</a>
              <a href="#admin-users">Usuarios</a>
            </nav>
          </div>

          <div className="admin-rail-block">
            <span className="section-kicker">Qué revisar primero</span>
            <div className="admin-quick-list">
              <article>
                <strong>Salud de fuentes</strong>
                <p>Verificá estado, conector, scraping y últimas corridas.</p>
              </article>
              <article>
                <strong>LLM y automatización</strong>
                <p>Confirmá ciclo activo, modelo, prompt maestro y credenciales.</p>
              </article>
              <article>
                <strong>Usuarios y ABM</strong>
                <p>Revisá altas, roles, actividad y cola de alertas por empresa.</p>
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
                <h2>Qué resuelve esta consola</h2>
              </div>
              <p>No es una página de settings. Es una consola para operar la plataforma con criterio y contexto.</p>
            </div>

            <div className="admin-overview-grid">
              <article className="panel admin-overview-card">
                <span className="section-kicker">Discovery</span>
                <h3>Fuentes y conectores</h3>
                <p>Alta, edición y gobierno del inventario completo de orígenes y modos de parseo.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Motor</span>
                <h3>LLM y automatización</h3>
                <p>Ciclo de ingesta, modelo, prompt maestro y credenciales sensibles.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Entrega</span>
                <h3>Alertas y dispatch</h3>
                <p>Generación de alertas, colas y verificación del contenido final.</p>
              </article>
              <article className="panel admin-overview-card">
                <span className="section-kicker">Acceso</span>
                <h3>Usuarios globales y ABM</h3>
                <p>Control de roles, altas, bajas y configuración de cuentas de todas las empresas.</p>
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
              <p>Primero se crea el origen. Después se ajusta modo, conector, estado y configuración.</p>
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
                  <p>Cada tarjeta concentra estado, URL, conector y JSON de configuración.</p>
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
              <p>Monitoreo rápido para ver qué corrió, qué quedó pendiente y qué se intentó entregar.</p>
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

          <section id="admin-users" className="admin-section-stack">
            <article className="panel table-panel table-panel-upgraded">
              <div className="results-header">
                <div>
                  <span className="section-kicker">Usuarios</span>
                  <h2>Usuarios de todas las empresas</h2>
                </div>
                <p>Administración global de cuentas y permisos sin mezclarlo con fuentes ni automatización.</p>
              </div>
              <UserEditorList users={users} canManagePlatformRoles />
            </article>
          </section>
        </div>
      </section>
    </main>
  );
}
