import Link from "next/link";
import { redirect } from "next/navigation";

import { SiteHeader } from "../../../components/site-header";
import { StateForm } from "../../../components/state-form";
import { fetchTenderDetail } from "../../../lib/api";
import { getCookieHeaderFromSession, getCurrentUserFromSession } from "../../../lib/session";

type Props = {
  params: Promise<{ id: string }>;
};

function formatStateLabel(value: string | null | undefined) {
  switch (value) {
    case "new":
      return "Nueva";
    case "seen":
      return "Vista";
    case "saved":
      return "Guardada";
    case "discarded":
      return "Descartada";
    case "evaluating":
      return "En revisión";
    case "presenting":
      return "Preparando oferta";
    default:
      return value ?? "Sin estado";
  }
}

export default async function TenderDetailPage({ params }: Props) {
  const { id } = await params;
  const [currentUser, cookieHeader] = await Promise.all([
    getCurrentUserFromSession(),
    getCookieHeaderFromSession(),
  ]);
  if (!currentUser) {
    redirect("/login");
  }

  const tender = await fetchTenderDetail(id, cookieHeader || undefined);
  const enrichment = tender.enrichments[0];
  const structured = enrichment?.summary_structured_json;
  const match = tender.matches[0];
  const state = tender.states[0];
  const primaryDocument = tender.documents[0];
  const matchScore = match ? Math.round(Number(match.score)) : null;
  const keyDates = structured?.key_dates ? Object.entries(structured.key_dates) : [];
  const extractedText = tender.documents.find((document) => document.texts.length > 0)?.texts[0]?.extracted_text;

  return (
    <main className="page-shell">
      <SiteHeader section="detail" currentUserName={currentUser.full_name} currentUserRole={currentUser.role} />

      <section className="hero hero-app about-hero tender-hero">
        <div>
          <span className="eyebrow">Dossier de licitación</span>
          <h1 style={{ maxWidth: "15ch" }}>{tender.title}</h1>
        </div>
        <p>
          {tender.organization ?? "Sin organismo"} · {tender.jurisdiction ?? "Sin jurisdicción"} ·{" "}
          {tender.procedure_type ?? "Sin tipo de procedimiento"}
        </p>
      </section>

      <section className="detail-masthead tender-masthead">
        <article className="signal-card signal-accent">
          <span className="signal-label">Score</span>
          <strong>{matchScore ?? "n/d"}</strong>
          <p>{match?.score_band ?? "Sin banda de relevancia"}</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Estado interno</span>
          <strong>{formatStateLabel(state?.state ?? "new")}</strong>
          <p>{state?.notes ?? "Todavía sin nota del equipo."}</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Deadline</span>
          <strong>{tender.deadline_date ? new Date(tender.deadline_date).toLocaleDateString("es-AR") : "Sin fecha"}</strong>
          <p>{tender.deadline_date ? new Date(tender.deadline_date).toLocaleTimeString("es-AR") : "Sin horario"}</p>
        </article>
        <article className="signal-card">
          <span className="signal-label">Documentos</span>
          <strong>{tender.documents.length}</strong>
          <p>{primaryDocument?.texts[0]?.extraction_method ?? "Sin extracción todavía"}</p>
        </article>
      </section>

      <section className="layout-grid detail-layout-upgraded tender-layout">
        <aside className="panel filters detail-sidebar">
          <div className="section-heading">
            <span className="section-kicker">Acción</span>
            <h2>Estado y nota interna</h2>
          </div>
          <StateForm tenderId={tender.id} initialState={state?.state} />

          <div className="detail-note-card">
            <span className="section-kicker">Fuente original</span>
            <a href={tender.source_url} className="linkish" target="_blank" rel="noreferrer">
              Abrir publicación
            </a>
            <p className="muted">
              {tender.detail_cached_at
                ? `Cacheado ${new Date(tender.detail_cached_at).toLocaleString("es-AR")}`
                : "Sin cache visible"}
            </p>
          </div>

          <div className="detail-note-card">
            <span className="section-kicker">Resumen</span>
            <p>{match?.reasons_json?.summary?.[0] ?? "Revisá fit, tiempo útil y requisitos antes de avanzar."}</p>
            <Link href="/dashboard" className="linkish">
              Volver a oportunidades
            </Link>
          </div>
        </aside>

        <section className="detail-content">
          <article className="panel content-panel detail-panel-spotlight">
            <div className="section-heading">
              <span className="section-kicker">Resumen</span>
              <h2>Qué revisar antes de moverla</h2>
            </div>
            <div className="decision-grid">
              <div>
                <strong>Por qué podría importar</strong>
                <p>{match?.reasons_json?.summary?.[0] ?? "Hay que validar encaje comercial y documento base."}</p>
              </div>
              <div>
                <strong>Objeto</strong>
                <p>{structured?.procurement_object ?? tender.description_raw?.slice(0, 180) ?? "Sin objeto sintetizado."}</p>
              </div>
              <div>
                <strong>Qué hacer ahora</strong>
                <p>{state?.notes ?? "Definir si se guarda, se evalúa o se descarta con una nota clara."}</p>
              </div>
            </div>
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Por qué coincide</span>
              <h2>Motivos del matching</h2>
            </div>
            {match ? (
              <div className="content-stack">
                <div className="meta">
                  <span className="badge score-chip">Score {matchScore}</span>
                  <span className="badge">{match.score_band}</span>
                </div>
                {match.reasons_json?.summary?.length ? (
                  <ul className="muted">
                    {match.reasons_json.summary.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
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
              <p className="muted">Todavía no hay matching calculado para esta licitación.</p>
            )}
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Fechas y alertas</span>
              <h2>Ventanas de acción</h2>
            </div>
            {keyDates.length ? (
              <div className="detail-date-strip">
                {keyDates.map(([key, value]) => (
                  <article key={key}>
                    <span>{key}</span>
                    <strong>{value ?? "n/d"}</strong>
                  </article>
                ))}
              </div>
            ) : null}
            {tender.alerts.length ? (
              <div className="alert-stack">
                {tender.alerts.map((alert) => (
                  <article key={alert.id} className="alert-row">
                    <span className="mini-pill">{alert.alert_type.replaceAll("_", " ")}</span>
                    <strong>{alert.delivery_channel}</strong>
                    <p>{new Date(alert.scheduled_for).toLocaleString("es-AR")}</p>
                  </article>
                ))}
              </div>
            ) : (
              <p className="muted">Todavía no hay alertas programadas para esta licitación.</p>
            )}
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Resumen IA</span>
              <h2>Lectura corta de documento</h2>
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
                {structured?.key_requirements?.length ? (
                  <div>
                    <strong>Requisitos</strong>
                    <ul className="muted">
                      {structured.key_requirements.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
                    </ul>
                  </div>
                ) : null}
                {structured?.risk_flags?.length ? (
                  <div>
                    <strong>Riesgos</strong>
                    <ul className="muted">
                      {structured.risk_flags.map((item) => (
                        <li key={item}>{item}</li>
                      ))}
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
                      <p className="muted" style={{ marginBottom: 0 }}>
                        Guardado en {document.file_path}
                      </p>
                    ) : null}
                  </div>
                ))}
              </div>
            )}
          </article>

          <article className="panel content-panel">
            <div className="section-heading">
              <span className="section-kicker">Texto base</span>
              <h2>Extracción usable</h2>
            </div>
            <p className="text-block">
              {extractedText?.slice(0, 5000) ?? tender.description_raw ?? "Todavía no hay texto extraído para esta licitación."}
            </p>
          </article>
        </section>
      </section>
    </main>
  );
}
