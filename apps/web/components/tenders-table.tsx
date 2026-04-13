import Link from "next/link";

import { Tender } from "../lib/api";

type Props = {
  tenders: Tender[];
  total: number;
};

function formatDate(value: string | null) {
  if (!value) return "Sin fecha";
  return new Intl.DateTimeFormat("es-AR", {
    dateStyle: "medium",
    timeStyle: "short",
  }).format(new Date(value));
}

function getUrgencyLabel(value: string | null) {
  if (!value) return "Sin cierre";
  const diff = new Date(value).getTime() - Date.now();
  if (diff < 0) return "Vencida";
  if (diff < 1000 * 60 * 60 * 24) return "Cierra en 24h";
  if (diff < 1000 * 60 * 60 * 24 * 3) return "Cierra en 3 días";
  if (diff < 1000 * 60 * 60 * 24 * 7) return "Esta semana";
  return "Con margen";
}

function getUrgencyTone(value: string | null) {
  if (!value) return "tone-neutral";
  const diff = new Date(value).getTime() - Date.now();
  if (diff < 0) return "tone-danger";
  if (diff < 1000 * 60 * 60 * 24 * 3) return "tone-danger";
  if (diff < 1000 * 60 * 60 * 24 * 7) return "tone-warning";
  return "tone-calm";
}

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

function getScoreTone(score: number | null) {
  if (score === null) return "tone-neutral";
  if (score >= 70) return "tone-success";
  if (score >= 45) return "tone-warning";
  return "tone-muted";
}

function formatScoreBand(value: string | null | undefined) {
  switch (value) {
    case "high":
      return "Alto fit";
    case "medium":
      return "Fit medio";
    case "low":
      return "Fit bajo";
    default:
      return "Sin banda";
  }
}

function collectReasonLines(tender: Tender): string[] {
  const summary = tender.matches[0]?.reasons_json?.summary;
  if (!summary || !Array.isArray(summary)) return [];
  return summary.filter((item): item is string => typeof item === "string" && item.trim().length > 0).slice(0, 2);
}

export function TendersTable({ tenders, total }: Props) {
  const isEmpty = tenders.length === 0;

  return (
    <section className="panel table-panel table-panel-upgraded">
      <div className="results-header">
        <div>
          <span className="section-kicker">Resultados</span>
          <h2>Oportunidades disponibles</h2>
          <p>
            {isEmpty
              ? "No hay coincidencias con los filtros actuales."
              : `${total} registros visibles en el top de licitaciones habilitado para esta empresa, con score, urgencia y acceso a fuente original.`}
          </p>
        </div>
        <p className="muted">Usá esta lista como inbox de revisión. El objetivo no es mirar todo: es guardar rápido lo que sí amerita seguimiento.</p>
      </div>

      {!isEmpty ? (
        <div className="detail-note-card">
          <span className="section-kicker">Alcance efectivo</span>
          <p>Lo que aparece acá depende de dos filtros: fuentes activas a nivel plataforma y fuentes habilitadas para esta empresa.</p>
        </div>
      ) : null}

      {!isEmpty ? (
      <div className="results-ribbon">
        <span>Score, banda y motivo</span>
        <span>Deadline</span>
        <span>Workflow</span>
        <span>Fuente original</span>
      </div>
      ) : null}

      <div className="opportunity-list">
        {isEmpty ? (
          <div className="opportunity-list-empty workspace-empty-state">
            <p className="opportunity-list-empty-title">Nada por aquí todavía</p>
            <p className="muted">
              Probá bajar el umbral de relevancia, sacar la jurisdicción o elegir otra fuente.
            </p>
            <Link href="/dashboard" className="button-primary">
              Ver todas las oportunidades
            </Link>
          </div>
        ) : null}
        {tenders.map((tender) => {
          const match = tender.matches[0];
          const state = tender.states[0];
          const score = match ? Math.round(Number(match.score)) : null;
          const reasonLines = collectReasonLines(tender);

          return (
            <article key={tender.id} className="opportunity-list-card">
              <div className="opportunity-list-main">
                <div className="opportunity-list-head">
                  <span className="source-chip">{tender.source.name}</span>
                  {tender.procedure_type ? <span className="badge">{tender.procedure_type}</span> : null}
                  {tender.jurisdiction ? <span className="badge">{tender.jurisdiction}</span> : null}
                  <span className={`badge ${getUrgencyTone(tender.deadline_date)}`}>{getUrgencyLabel(tender.deadline_date)}</span>
                </div>
                <strong>{tender.title}</strong>
                <p>{tender.organization ?? "Sin organismo"} · cierre {formatDate(tender.deadline_date)}</p>
                <p className="muted">Fuente {tender.source.name}{tender.external_id ? ` · expediente/proceso ${tender.external_id}` : ""}</p>
                {reasonLines.length ? (
                  <div className="admin-status-list">
                    {reasonLines.map((line) => (
                      <article key={`${tender.id}-${line}`}>
                        <p>{line}</p>
                      </article>
                    ))}
                  </div>
                ) : (
                  <p className="muted">Sin explicación sintetizada todavía.</p>
                )}
              </div>

              <div className="opportunity-list-aside">
                {match ? (
                  <>
                    <span className={`badge score-chip ${getScoreTone(score)}`}>Score {score}</span>
                    <span className="badge">{formatScoreBand(match.score_band)}</span>
                  </>
                ) : (
                  <span className="badge">Sin match</span>
                )}
                {state ? <span className="badge">{formatStateLabel(state.state)}</span> : null}
                <Link href={`/tenders/${tender.id}`} className="button-secondary">
                  Abrir dossier
                </Link>
                <a href={tender.source_url} target="_blank" rel="noreferrer" className="linkish">
                  Fuente original
                </a>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
