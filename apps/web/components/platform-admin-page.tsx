import { AlertOpsPanel } from "./alert-ops-panel";
import { AutomationSettingsPanel } from "./automation-settings-panel";
import { SiteHeader } from "./site-header";
import { SourceEditorList } from "./source-editor-list";
import { SourceForm } from "./source-form";
import { UserEditorList } from "./user-editor-list";
import type { Alert, AutomationSettings, Source, SourceRun, User } from "../lib/api";

type Props = {
  currentUserName: string;
  sourceRuns: SourceRun[];
  alerts: Alert[];
  users: User[];
  sources: Source[];
  automationSettings: AutomationSettings;
};

export function PlatformAdminPage({
  currentUserName,
  sourceRuns,
  alerts,
  users,
  sources,
  automationSettings,
}: Props) {
  const sourceMap = new Map(sources.map((source) => [source.id, source]));

  return (
    <main className="page-shell">
      <SiteHeader section="admin" currentUserName={currentUserName} />

      <section className="hero hero-app">
        <div>
          <span className="eyebrow">Admin de plataforma</span>
          <h1>Administración general de toda la plataforma.</h1>
        </div>
        <p>Desde acá controlás las fuentes, la automatización, OpenAI, las corridas y la operación completa de todas las empresas.</p>
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <div className="stat-label">Source runs</div>
          <div className="stat-value">{sourceRuns.length}</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Alerts</div>
          <div className="stat-value">{alerts.length}</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Usuarios</div>
          <div className="stat-value">{users.length}</div>
        </article>
      </section>

      <section className="dispatch-grid">
        <article className="panel dispatch-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Health</span>
              <h2>Estado general</h2>
            </div>
            <p>Resumen rápido de la actividad global de la plataforma, sin entrar a logs ni tareas manuales.</p>
          </div>

          <div className="priority-list compact-priority-list">
            {sourceRuns.slice(0, 3).map((run, index) => (
              <article key={run.id} className="priority-item">
                <div className="priority-rank">0{index + 1}</div>
                <div className="priority-body">
                  <div className="meta">
                    <span className="badge">{run.status}</span>
                    <span className="mini-pill">source #{run.source_id}</span>
                  </div>
                  <h3>Run {run.id}</h3>
                  <p>
                    {run.items_new} nuevos / {run.items_found} encontrados ·{" "}
                    {new Date(run.started_at).toLocaleString("es-AR")}
                  </p>
                </div>
              </article>
            ))}
          </div>
        </article>

        <article className="panel dispatch-panel dispatch-alerts">
          <div className="results-header">
            <div>
              <span className="section-kicker">Queue</span>
              <h2>Últimos alerts visibles</h2>
            </div>
          </div>

          <div className="alert-stack">
            {alerts.slice(0, 4).map((alert) => (
              <article key={alert.id} className="alert-row">
                <span className="mini-pill">{alert.alert_type}</span>
                <strong>Tender #{alert.tender_id}</strong>
                <p>{new Date(alert.scheduled_for).toLocaleString("es-AR")}</p>
              </article>
            ))}
          </div>
        </article>
      </section>

      <section className="admin-control-grid">
        <article className="panel dispatch-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Fuentes</span>
              <h2>Agregar una fuente nueva</h2>
            </div>
            <p>La fuente queda registrada para toda la plataforma. Si el slug coincide con un conector implementado, queda lista para correr.</p>
          </div>
          <SourceForm />
        </article>

        <article className="panel dispatch-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Estado</span>
              <h2>Editar fuentes existentes</h2>
            </div>
            <p>Acá definís qué fuentes siguen activas y con qué datos opera la plataforma.</p>
          </div>
          <SourceEditorList sources={sources} />
        </article>
      </section>

      <section style={{ display: "grid", gap: 20, marginBottom: 20 }}>
        <article className="panel dispatch-panel">
          <AutomationSettingsPanel settings={automationSettings} />
        </article>
        <article className="panel dispatch-panel">
          <AlertOpsPanel />
        </article>
      </section>

      <section style={{ display: "grid", gap: 20 }}>
        <article className="panel table-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Runs</span>
              <h2>Últimas corridas globales</h2>
            </div>
          </div>
          <div className="table-wrap">
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Source</th>
                  <th>Status</th>
                  <th>Items</th>
                  <th>Fechas</th>
                </tr>
              </thead>
              <tbody>
                {sourceRuns.map((run) => (
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

        <article className="panel table-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Alerts</span>
              <h2>Cola global de notificaciones</h2>
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
                {alerts.map((alert) => (
                  <tr key={alert.id}>
                    <td>{alert.id}</td>
                    <td>{alert.tender_id}</td>
                    <td>{alert.alert_type}</td>
                    <td>{alert.delivery_channel} / {alert.delivery_status}</td>
                    <td>{alert.delivery_attempts}{alert.last_error_message ? ` · ${alert.last_error_message}` : ""}</td>
                    <td>{new Date(alert.scheduled_for).toLocaleString("es-AR")}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </article>

        <article className="panel table-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Usuarios</span>
              <h2>Usuarios de todas las empresas</h2>
            </div>
            <p>Como admin de plataforma podés ver y administrar usuarios de cualquier empresa.</p>
          </div>
          <UserEditorList users={users} canManagePlatformRoles />
        </article>
      </section>
    </main>
  );
}
