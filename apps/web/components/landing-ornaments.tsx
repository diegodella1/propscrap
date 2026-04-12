export function HeroTechnicalIllustration() {
  return (
    <div className="hero-technical-illustration" aria-hidden="true">
      <svg viewBox="0 0 520 340" role="presentation">
        <rect x="20" y="24" width="480" height="292" className="hero-svg-panel" />
        <path d="M44 70 H476" className="hero-svg-line hero-svg-line-soft" />
        <path d="M44 166 H476" className="hero-svg-line hero-svg-line-soft" />
        <path d="M180 52 V288" className="hero-svg-line hero-svg-line-soft" />
        <path d="M344 52 V288" className="hero-svg-line hero-svg-line-soft" />
        <rect x="56" y="40" width="112" height="20" className="hero-svg-chip" />
        <rect x="362" y="40" width="108" height="20" className="hero-svg-chip hero-svg-chip-warm" />
        <path d="M72 118 C126 102 178 108 234 134 S342 180 448 138" className="hero-svg-trace" />
        <path d="M72 232 C132 216 184 226 236 248 S342 286 448 248" className="hero-svg-trace hero-svg-trace-alt" />
        <circle cx="72" cy="118" r="6" className="hero-svg-node" />
        <circle cx="236" cy="134" r="7" className="hero-svg-node hero-svg-node-strong" />
        <circle cx="448" cy="138" r="6" className="hero-svg-node hero-svg-node-calm" />
        <circle cx="72" cy="232" r="6" className="hero-svg-node" />
        <circle cx="236" cy="248" r="7" className="hero-svg-node hero-svg-node-warm" />
        <circle cx="448" cy="248" r="6" className="hero-svg-node hero-svg-node-strong" />
      </svg>
    </div>
  );
}

export function ProofRibbonIllustration() {
  return (
    <div className="proof-ribbon-illustration" aria-hidden="true">
      <svg viewBox="0 0 320 72" role="presentation">
        <path d="M10 36 H110" className="proof-svg-line" />
        <circle cx="116" cy="36" r="5" className="proof-svg-dot" />
        <path d="M122 36 H202" className="proof-svg-line proof-svg-line-accent" />
        <circle cx="208" cy="36" r="5" className="proof-svg-dot proof-svg-dot-accent" />
        <path d="M214 36 H310" className="proof-svg-line" />
      </svg>
    </div>
  );
}

export function ProcessDiagramIllustration() {
  return (
    <div className="process-diagram-illustration" aria-hidden="true">
      <svg viewBox="0 0 360 180" role="presentation">
        <rect x="18" y="26" width="88" height="44" className="process-svg-box" />
        <rect x="136" y="26" width="88" height="44" className="process-svg-box process-svg-box-accent" />
        <rect x="254" y="26" width="88" height="44" className="process-svg-box" />
        <rect x="76" y="112" width="88" height="44" className="process-svg-box" />
        <rect x="194" y="112" width="88" height="44" className="process-svg-box process-svg-box-calm" />
        <path d="M106 48 H136" className="process-svg-line" />
        <path d="M224 48 H254" className="process-svg-line" />
        <path d="M180 70 V112" className="process-svg-line" />
        <path d="M120 112 C142 94 158 88 180 88 C202 88 220 94 238 112" className="process-svg-line process-svg-line-accent" />
        <circle cx="180" cy="88" r="6" className="process-svg-dot" />
      </svg>
    </div>
  );
}

export function ProcessFlowEditorialIllustration() {
  return (
    <div className="process-flow-editorial-illustration" aria-hidden="true">
      <svg viewBox="0 0 920 360" role="presentation">
        <rect x="24" y="28" width="872" height="292" className="process-flow-shell" />
        <text x="56" y="68" className="process-flow-kicker">Flujo de trabajo</text>
        <text x="56" y="104" className="process-flow-title process-flow-title-large">
          Del alta legal al seguimiento comercial.
        </text>

        <rect x="56" y="144" width="224" height="132" className="process-flow-panel" />
        <rect x="348" y="144" width="224" height="132" className="process-flow-panel process-flow-panel-accent" />
        <rect x="640" y="144" width="224" height="132" className="process-flow-panel" />

        <path d="M280 210 H348" className="process-flow-line" />
        <path d="M572 210 H640" className="process-flow-line" />
        <circle cx="280" cy="210" r="6" className="process-flow-node" />
        <circle cx="348" cy="210" r="6" className="process-flow-node" />
        <circle cx="572" cy="210" r="6" className="process-flow-node" />
        <circle cx="640" cy="210" r="6" className="process-flow-node" />

        <text x="80" y="134" className="process-flow-step">01</text>
        <text x="372" y="134" className="process-flow-step">02</text>
        <text x="664" y="134" className="process-flow-step">03</text>

        <text x="80" y="176" className="process-flow-card-title">Registro por CUIT</text>
        <text x="80" y="208" className="process-flow-copy">Identidad legal, razón social</text>
        <text x="80" y="230" className="process-flow-copy">y perfil inicial de empresa.</text>
        <rect x="80" y="244" width="102" height="16" className="process-flow-tag" />

        <text x="372" y="176" className="process-flow-card-title">Discovery y scoring</text>
        <text x="372" y="208" className="process-flow-copy">Fuentes, prioridad, fechas</text>
        <text x="372" y="230" className="process-flow-copy">y explicación del match.</text>
        <rect x="372" y="244" width="116" height="16" className="process-flow-tag process-flow-tag-accent" />

        <text x="664" y="176" className="process-flow-card-title">Seguimiento y alertas</text>
        <text x="664" y="208" className="process-flow-copy">Pipeline, responsables</text>
        <text x="664" y="230" className="process-flow-copy">y vencimientos visibles.</text>
        <rect x="664" y="244" width="112" height="16" className="process-flow-tag" />
      </svg>
    </div>
  );
}

export function ExecutiveControlIllustration() {
  return (
    <div className="executive-control-illustration" aria-hidden="true">
      <svg viewBox="0 0 860 520" role="presentation">
        <rect x="24" y="24" width="812" height="472" className="executive-shell" />
        <text x="58" y="72" className="executive-kicker">EasyTaciones</text>
        <text x="58" y="114" className="executive-title">Discovery, prioridad y seguimiento</text>
        <text x="58" y="146" className="executive-title">en una sola superficie operativa.</text>

        <rect x="58" y="184" width="744" height="76" className="executive-band" />
        <text x="82" y="214" className="executive-band-label">Flujo principal</text>
        <text x="82" y="240" className="executive-band-copy">CUIT / fuentes / scoring / seguimiento / alertas</text>
        <path d="M92 244 H770" className="executive-path" />
        <circle cx="164" cy="244" r="6" className="executive-path-node" />
        <circle cx="310" cy="244" r="6" className="executive-path-node" />
        <circle cx="456" cy="244" r="6" className="executive-path-node" />
        <circle cx="602" cy="244" r="6" className="executive-path-node" />
        <circle cx="748" cy="244" r="6" className="executive-path-node" />
        <text x="136" y="228" className="executive-path-label">CUIT</text>
        <text x="274" y="228" className="executive-path-label">Fuentes</text>
        <text x="424" y="228" className="executive-path-label">Score</text>
        <text x="554" y="228" className="executive-path-label">Pipeline</text>
        <text x="704" y="228" className="executive-path-label">Alertas</text>

        <rect x="58" y="292" width="230" height="156" className="executive-panel" />
        <rect x="314" y="292" width="230" height="156" className="executive-panel executive-panel-accent" />
        <rect x="570" y="292" width="232" height="156" className="executive-panel" />

        <text x="82" y="324" className="executive-card-kicker">Problema</text>
        <text x="82" y="356" className="executive-card-title">Trabajo fragmentado</text>
        <text x="82" y="388" className="executive-card-copy">Portales, pliegos y planillas</text>
        <text x="82" y="408" className="executive-card-copy">sin una misma lectura.</text>

        <text x="338" y="324" className="executive-card-kicker">Sistema</text>
        <text x="338" y="356" className="executive-card-title">Orden operativo</text>
        <text x="338" y="388" className="executive-card-copy">Una cola clara para decidir</text>
        <text x="338" y="408" className="executive-card-copy">qué mirar y qué mover.</text>

        <text x="594" y="324" className="executive-card-kicker">Resultado</text>
        <text x="594" y="356" className="executive-card-title">Menos pérdida</text>
        <text x="594" y="388" className="executive-card-copy">Más control sobre timing,</text>
        <text x="594" y="408" className="executive-card-copy">responsables y próximas acciones.</text>
      </svg>
    </div>
  );
}

export function WorkspaceBoardIllustration() {
  return (
    <div className="workspace-board-illustration" aria-hidden="true">
      <svg viewBox="0 0 900 300" role="presentation">
        <rect x="22" y="26" width="856" height="248" className="workspace-shell" />
        <rect x="54" y="58" width="248" height="44" className="workspace-strip" />
        <rect x="326" y="58" width="248" height="44" className="workspace-strip workspace-strip-accent" />
        <rect x="598" y="58" width="248" height="44" className="workspace-strip" />

        <text x="74" y="86" className="workspace-strip-copy">Nuevas relevantes</text>
        <text x="346" y="86" className="workspace-strip-copy">Fechas críticas</text>
        <text x="618" y="86" className="workspace-strip-copy">En seguimiento</text>

        <rect x="54" y="126" width="248" height="112" className="workspace-panel" />
        <rect x="326" y="126" width="248" height="112" className="workspace-panel workspace-panel-accent" />
        <rect x="598" y="126" width="248" height="112" className="workspace-panel" />

        <text x="78" y="154" className="workspace-kicker">Inbox</text>
        <text x="78" y="186" className="workspace-title">Qué mirar hoy</text>
        <text x="78" y="214" className="workspace-copy">Match, motivo y deadline</text>

        <text x="350" y="154" className="workspace-kicker">Calendario</text>
        <text x="350" y="186" className="workspace-title">Qué vence primero</text>
        <text x="350" y="214" className="workspace-copy">Cierres y alertas críticas</text>

        <text x="622" y="154" className="workspace-kicker">Pipeline</text>
        <text x="622" y="186" className="workspace-title">Qué sigue ahora</text>
        <text x="622" y="214" className="workspace-copy">Estado, notas y responsable</text>
      </svg>
    </div>
  );
}
