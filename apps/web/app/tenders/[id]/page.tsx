import Link from "next/link";

import { SiteHeader } from "../../../components/site-header";
import { StateForm } from "../../../components/state-form";
import { fetchTenderDetail } from "../../../lib/api";
import { getCurrentUserFromSession } from "../../../lib/session";

type Props = {
  params: Promise<{ id: string }>;
};

export default async function TenderDetailPlaceholder({ params }: Props) {
  const { id } = await params;
  const [tender, currentUser] = await Promise.all([fetchTenderDetail(id), getCurrentUserFromSession()]);

  const extractedText = tender.documents.find((document) => document.texts.length > 0)
    ?.texts[0]?.extracted_text;
  const enrichment = tender.enrichments[0];
  const structured = enrichment?.summary_structured_json;
  const match = tender.matches[0];
  const state = tender.states[0];
  const primaryDocument = tender.documents[0];
  const matchScore = match ? Math.round(Number(match.score)) : null;

  function scoreTone(score: number | null) {
    if (score === null) return "tone-neutral";
    if (score >= 75) return "tone-success";
    if (score >= 50) return "tone-warning";
    return "tone-muted";
  }

  function formatStateLabel(value: string | null | undefined) {
    switch (value) {
      case "new":
        return "Nuevo";
      case "seen":
        return "Visto";
      case "saved":
        return "Guardado";
      case "discarded":
        return "Descartado";
      case "evaluating":
        return "En evaluación";
      case "presenting":
        return "Presentando";
      default:
        return value ?? "Sin estado";
    }
  }

  function formatAlertType(value: string) {
    if (value === "new_relevant") return "Nueva relevante";
    if (value === "deadline_7d") return "Cierre en 7 días";
    if (value === "deadline_3d") return "Cierre en 3 días";
    if (value === "deadline_24h") return "Cierre en 24h";
    return value;
  }

  function formatScoreBand(value: string | null | undefined) {
    if (value === "high") return "alto";
    if (value === "medium") return "medio";
    if (value === "low") return "bajo";
    return value ?? "n/d";
  }

  return (
    <main className="page-shell">
      <SiteHeader section="detail" currentUserName={currentUser?.full_name} />

      <section className="hero hero-app" style={{ marginBottom: 18 }}>
        <div>
          <span className="eyebrow">Dossier de licitación</span>
          <h1 style={{ maxWidth: "16ch" }}>{tender.title}</h1>
        </div>
        <p>{tender.organization ?? "Sin organismo"} · {tender.jurisdiction ?? "Sin jurisdicción"}</p>
        <div className="meta">
          {tender.procedure_type ? <span className="badge">{tender.procedure_type}</span> : null}
          {tender.status_raw ? <span className="badge">{tender.status_raw}</span> : null}
          <span className="badge source-chip">{tender.source.name}</span>
          {match ? <span className={`badge score-chip ${scoreTone(matchScore)}`}>Score {matchScore}</span> : null}
        </div>
      </section>

      <section className="detail-summary-grid">
        <article className="signal-card signal-accent">
          <span className="signal-label">Relevancia</span>
          <strong>{match ? Math.round(Number(match.score)) : "n/d"}</strong>
          <p>{match?.score_band ?? "Sin match calculado"}</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Workflow</span>
          <strong>{formatStateLabel(state?.state ?? "new")}</strong>
          <p>{state?.notes ?? "Sin notas todavía"}</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Deadline</span>
          <strong>{tender.deadline_date ? new Date(tender.deadline_date).toLocaleDateString("es-AR") : "n/d"}</strong>
          <p>{tender.deadline_date ? new Date(tender.deadline_date).toLocaleTimeString("es-AR") : "Sin cierre informado"}</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Documentos</span>
          <strong>{tender.documents.length}</strong>
          <p>{primaryDocument?.texts[0]?.extraction_method ?? "Sin extracción todavía"}</p>
        </article>
      </section>

      <section className="layout-grid" style={{ gridTemplateColumns: "320px minmax(0, 1fr)" }}>
        <aside className="panel filters detail-sidebar">
          <div className="section-heading">
            <span className="section-kicker">Dossier</span>
            <h2>Metadatos clave</h2>
          </div>
          <div className="field">
            <label>Publicación</label>
            <div>{tender.publication_date ?? "Sin fecha"}</div>
          </div>
          <div className="field">
            <label>Apertura / cierre</label>
            <div>{tender.deadline_date ? new Date(tender.deadline_date).toLocaleString("es-AR") : "Sin fecha"}</div>
          </div>
          <div className="field">
            <label>Fuente original</label>
            <a href={tender.source_url} className="linkish" target="_blank" rel="noreferrer">
              Abrir publicación
            </a>
          </div>
          <div className="field">
            <label>Cache de detalle</label>
            <div>{tender.detail_cached_at ? new Date(tender.detail_cached_at).toLocaleString("es-AR") : "No cacheado"}</div>
          </div>
          <div className="detail-note-card">
            <span className="section-kicker">Lectura rápida</span>
            <p>
              {match?.reasons_json?.summary?.[0] ??
                "Usá esta ficha para decidir si se descarta, se guarda o pasa a evaluación."}
            </p>
          </div>
          {match ? (
            <div className="detail-note-card detail-note-compact">
              <span className={`badge score-chip ${scoreTone(matchScore)}`}>Score {matchScore}</span>
              <span className="muted">Prioridad {formatScoreBand(match.score_band)}</span>
            </div>
          ) : null}
          <div className="field">
            <label>Workflow</label>
            <StateForm tenderId={tender.id} initialState={state?.state} />
          </div>
          <Link href="/dashboard" className="linkish">Volver al dashboard</Link>
        </aside>

        <section className="detail-content">
          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Alerts</span>
              <h2>Ventanas de acción</h2>
            </div>
            {tender.alerts.length ? (
              <div className="alert-stack">
                {tender.alerts.map((alert) => (
                  <div key={alert.id} className={`alert-row ${alert.alert_type.includes("24h") ? "tone-danger" : "tone-warning"}`}>
                    <div className="meta">
                      <span className={`badge ${alert.alert_type.includes("24h") ? "tone-danger" : "tone-warning"}`}>
                        {formatAlertType(alert.alert_type)}
                      </span>
                      <span className="badge">{alert.delivery_status}</span>
                    </div>
                    <p className="muted" style={{ marginBottom: 0 }}>
                      Programada para {new Date(alert.scheduled_for).toLocaleString("es-AR")}
                    </p>
                  </div>
                ))}
              </div>
            ) : (
              <p className="muted">Todavía no hay alerts para esta licitación.</p>
            )}
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Matching</span>
              <h2>Por qué esta licitación importa</h2>
            </div>
            {match ? (
              <div className="content-stack">
                <div className="meta">
                  <span className={`badge score-chip ${scoreTone(matchScore)}`}>
                    Score {matchScore}
                  </span>
                  <span className="badge">{formatScoreBand(match.score_band)}</span>
                </div>
                {match.reasons_json?.summary?.length ? (
                  <ul className="muted">
                    {match.reasons_json.summary.map((item) => <li key={item}>{item}</li>)}
                  </ul>
                ) : null}
                {match.reasons_json?.components ? (
                  <div className="meta">
                    {Object.entries(match.reasons_json.components as Record<string, { points?: number }>).map(
                      ([key, value]) => (
                        <span key={key} className="badge">
                          {key}: {value.points ?? 0}
                        </span>
                      ),
                    )}
                  </div>
                ) : null}
              </div>
            ) : (
              <p className="muted">Todavía no hay match calculado para esta licitación.</p>
            )}
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Resumen IA</span>
              <h2>Lectura ejecutiva</h2>
            </div>
            {enrichment ? (
              <div className="content-stack">
                <div className="meta">
                  <span className="badge">{enrichment.enrichment_status}</span>
                  {enrichment.llm_model ? <span className="badge source-chip">{enrichment.llm_model}</span> : null}
                </div>
                <p className="muted" style={{ whiteSpace: "pre-wrap", margin: 0 }}>
                  {enrichment.summary_short ?? "Sin resumen corto"}
                </p>
                {structured?.procurement_object ? (
                  <div>
                    <strong>Objeto</strong>
                    <p className="muted" style={{ marginBottom: 0 }}>{structured.procurement_object}</p>
                  </div>
                ) : null}
                {structured?.key_dates ? (
                  <div>
                    <strong>Fechas clave</strong>
                    <div className="meta" style={{ marginTop: 8 }}>
                      {Object.entries(structured.key_dates).map(([key, value]) => (
                        <span key={key} className="badge">{key}: {value ?? "n/d"}</span>
                      ))}
                    </div>
                  </div>
                ) : null}
                {structured?.key_requirements?.length ? (
                  <div>
                    <strong>Requisitos</strong>
                    <ul className="muted">
                      {structured.key_requirements.map((item) => <li key={item}>{item}</li>)}
                    </ul>
                  </div>
                ) : null}
                {structured?.risk_flags?.length ? (
                  <div>
                    <strong>Riesgos</strong>
                    <ul className="muted">
                      {structured.risk_flags.map((item) => <li key={item}>{item}</li>)}
                    </ul>
                  </div>
                ) : null}
              </div>
            ) : (
              <p className="muted">Todavía no hay enriquecimiento LLM para esta licitación.</p>
            )}
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Fuente</span>
              <h2>Texto base de la publicación</h2>
            </div>
            <p className="muted" style={{ whiteSpace: "pre-wrap" }}>
              {tender.description_raw ?? "Todavía no hay cuerpo extraído para esta licitación."}
            </p>
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Documentos</span>
              <h2>Adjuntos y extracción</h2>
            </div>
            {tender.documents.length === 0 ? (
              <p className="muted">Esta fuente todavía no expone documentos descargados en la demo.</p>
            ) : (
              <div className="document-grid">
                {tender.documents.map((document) => (
                  <div key={document.id} className="document-card">
                    <div className="meta" style={{ marginBottom: 8 }}>
                      <span className="badge">{document.document_type}</span>
                      <span className="badge">{document.download_status}</span>
                      {document.texts[0] ? (
                        <span className="badge">
                          {document.texts[0].extraction_method} / {document.texts[0].extraction_status}
                        </span>
                      ) : null}
                    </div>
                    <strong>{document.filename}</strong>
                    <div style={{ marginTop: 8 }}>
                      <a href={document.source_url} className="linkish" target="_blank" rel="noreferrer">
                        Fuente del documento
                      </a>
                    </div>
                    {document.file_path ? (
                      <p className="muted" style={{ marginBottom: 0 }}>Guardado en {document.file_path}</p>
                    ) : null}
                  </div>
                ))}
              </div>
            )}
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Texto</span>
              <h2>Extracción usable</h2>
            </div>
            <p className="text-block">
              {extractedText?.slice(0, 5000) ?? "Todavía no hay texto extraído para esta licitación."}
            </p>
          </article>
        </section>
      </section>
    </main>
  );
}
