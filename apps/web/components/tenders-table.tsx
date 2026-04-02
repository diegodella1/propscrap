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
  if (diff < 1000 * 60 * 60 * 24 * 7) return "Cierra esta semana";
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

function formatScoreBand(value: string | null | undefined) {
  if (value === "high") return "alto";
  if (value === "medium") return "medio";
  if (value === "low") return "bajo";
  return value ?? "n/d";
}

function getScoreTone(score: number | null) {
  if (score === null) return "tone-neutral";
  if (score >= 75) return "tone-success";
  if (score >= 50) return "tone-warning";
  return "tone-muted";
}

function getStateTone(value: string | null | undefined) {
  switch (value) {
    case "presenting":
    case "evaluating":
      return "tone-success";
    case "saved":
      return "tone-calm";
    case "discarded":
      return "tone-danger";
    case "seen":
      return "tone-warning";
    default:
      return "tone-neutral";
  }
}

export function TendersTable({ tenders, total }: Props) {
  return (
    <section className="panel table-panel">
      <div className="results-header">
        <div>
          <span className="section-kicker">Cola priorizada</span>
          <h2>Licitaciones priorizadas</h2>
          <p>{total} registros persistidos en esta instancia local.</p>
        </div>
        <p className="muted">Una vista para decidir, no para acumular filas.</p>
      </div>

      <div className="table-wrap">
        <table className="desktop-table">
          <thead>
            <tr>
              <th>Título</th>
              <th>Organismo</th>
              <th>Fechas</th>
              <th>Estado</th>
              <th>Fuente</th>
            </tr>
          </thead>
          <tbody>
            {tenders.map((tender) => {
              const match = tender.matches[0];
              const state = tender.states[0];
              const score = match ? Math.round(Number(match.score)) : null;

              return (
                <tr key={tender.id}>
                  <td>
                    <div className="title-cell">
                      <strong>{tender.title}</strong>
                      <div className="meta">
                        {tender.procedure_type ? (
                          <span className="badge">{tender.procedure_type}</span>
                        ) : null}
                        {tender.jurisdiction ? (
                          <span className="badge">{tender.jurisdiction}</span>
                        ) : null}
                        <span className={`badge ${getUrgencyTone(tender.deadline_date)}`}>
                          {getUrgencyLabel(tender.deadline_date)}
                        </span>
                      </div>
                      <Link href={`/tenders/${tender.id}`} className="linkish">
                        Abrir dossier
                      </Link>
                    </div>
                  </td>
                  <td>{tender.organization ?? "Sin organismo"}</td>
                  <td>
                    <div className="title-cell">
                      <span className="muted">
                        Publicación: {tender.publication_date ?? "Sin fecha"}
                      </span>
                      <span
                        className={`badge ${getUrgencyTone(tender.deadline_date)}`}
                      >
                        Cierre: {formatDate(tender.deadline_date)}
                      </span>
                    </div>
                  </td>
                  <td>
                    <div className="title-cell">
                      <span>{tender.status_raw ?? "Sin estado"}</span>
                      {match ? (
                        <span className={`badge score-chip ${getScoreTone(score)}`}>
                          Score {score} / {formatScoreBand(match.score_band)}
                        </span>
                      ) : (
                        <span className="badge">Sin match</span>
                      )}
                      {state ? (
                        <span className={`badge workflow-chip ${getStateTone(state.state)}`}>
                          {formatStateLabel(state.state)}
                        </span>
                      ) : null}
                    </div>
                  </td>
                  <td>
                    <div className="title-cell">
                      <span className="badge source-chip">{tender.source.name}</span>
                      {match?.reasons_json?.summary?.[0] ? (
                        <span className="muted">{match.reasons_json.summary[0]}</span>
                      ) : null}
                      <a
                        href={tender.source_url}
                        target="_blank"
                        rel="noreferrer"
                        className="linkish"
                      >
                        Fuente original
                      </a>
                    </div>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="mobile-tender-list">
        {tenders.map((tender) => {
          const match = tender.matches[0];
          const state = tender.states[0];
          const score = match ? Math.round(Number(match.score)) : null;

          return (
            <article key={tender.id} className="mobile-tender-card">
              <div className="meta">
                <span className="source-chip">{tender.source.name}</span>
                {match ? <span className={`score-chip badge ${getScoreTone(score)}`}>Score {score}</span> : null}
                {state ? (
                  <span className={`badge workflow-chip ${getStateTone(state.state)}`}>
                    {formatStateLabel(state.state)}
                  </span>
                ) : null}
              </div>
              <h3>{tender.title}</h3>
              <p>{tender.organization ?? "Sin organismo"} · {tender.jurisdiction ?? "Sin jurisdicción"}</p>
              <div className="meta">
                {tender.procedure_type ? <span className="badge">{tender.procedure_type}</span> : null}
                <span className={`badge ${getUrgencyTone(tender.deadline_date)}`}>
                  {getUrgencyLabel(tender.deadline_date)}
                </span>
              </div>
              <div className="mobile-card-footer">
                <span className="muted">{formatDate(tender.deadline_date)}</span>
                <Link href={`/tenders/${tender.id}`} className="linkish">
                  Ver detalle
                </Link>
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
