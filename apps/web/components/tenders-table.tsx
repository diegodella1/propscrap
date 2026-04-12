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
  if (score >= 75) return "tone-success";
  if (score >= 50) return "tone-warning";
  return "tone-muted";
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
              : `${total} registros visibles con score, urgencia y acceso a fuente original.`}
          </p>
        </div>
        <p className="muted">Usá esta lista como inbox de revisión. El objetivo no es mirar todo: es guardar rápido lo que sí amerita seguimiento.</p>
      </div>

      {!isEmpty ? (
      <div className="results-ribbon">
        <span>Score y motivo</span>
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
                <p className="muted">
                  {match?.reasons_json?.summary?.[0] ?? "Sin explicación sintetizada todavía."}
                </p>
              </div>

              <div className="opportunity-list-aside">
                {match ? (
                  <span className={`badge score-chip ${getScoreTone(score)}`}>Score {score}</span>
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
