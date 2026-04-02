import { Source } from "../lib/api";

type Props = {
  selectedSource?: string;
  selectedJurisdiction?: string;
  selectedMinScore?: string;
  sources: Source[];
};

export function FilterPanel({
  selectedSource,
  selectedJurisdiction,
  selectedMinScore,
  sources,
}: Props) {
  return (
    <form className="panel filters dashboard-filter-panel">
      <div className="section-heading">
        <span className="section-kicker">Filtros</span>
        <h2>Refiná la cola de decisión</h2>
      </div>

      <div className="filter-preset-row">
        <a href="/dashboard?min_score=60" className="mini-pill filter-pill">
          Prioridad alta
        </a>
        <a href="/dashboard?jurisdiction=Naci%C3%B3n" className="mini-pill filter-pill">
          Nación
        </a>
        <a href="/dashboard" className="mini-pill filter-pill">
          Limpiar
        </a>
      </div>

      <div className="field">
        <label htmlFor="source">Fuente</label>
        <select id="source" name="source" defaultValue={selectedSource ?? ""}>
          <option value="">Todas</option>
          {sources.map((source) => (
            <option key={source.id} value={source.slug}>
              {source.name}
            </option>
          ))}
        </select>
      </div>

      <div className="field">
        <label htmlFor="jurisdiction">Jurisdicción</label>
        <input
          id="jurisdiction"
          name="jurisdiction"
          placeholder="Ej. Nación"
          defaultValue={selectedJurisdiction ?? ""}
        />
      </div>

      <div className="field">
        <label htmlFor="min_score">Relevancia mínima</label>
        <select id="min_score" name="min_score" defaultValue={selectedMinScore ?? ""}>
          <option value="">Todas</option>
          <option value="50">50+</option>
          <option value="60">60+</option>
          <option value="75">75+</option>
        </select>
      </div>

      <button type="submit" className="button-primary button-block">
        Aplicar filtros
      </button>

      <p className="muted filter-tip">
        Para una lectura ejecutiva, empezá por `60+` y después recortá por fuente o jurisdicción.
      </p>
    </form>
  );
}
