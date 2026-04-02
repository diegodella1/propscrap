export function HeroTechnicalIllustration() {
  return (
    <div className="hero-technical-illustration" aria-hidden="true">
      <svg viewBox="0 0 520 340" role="presentation">
        <defs>
          <linearGradient id="hero-grid-stroke" x1="0%" y1="0%" x2="100%" y2="100%">
            <stop offset="0%" stopColor="rgba(40,49,38,0.38)" />
            <stop offset="100%" stopColor="rgba(84,104,121,0.18)" />
          </linearGradient>
        </defs>
        <rect x="24" y="26" width="472" height="286" rx="18" className="hero-svg-panel" />
        <path d="M52 88 H468" className="hero-svg-line hero-svg-line-soft" />
        <path d="M52 188 H468" className="hero-svg-line hero-svg-line-soft" />
        <path d="M170 58 V284" className="hero-svg-line hero-svg-line-soft" />
        <path d="M330 58 V284" className="hero-svg-line hero-svg-line-soft" />
        <rect x="56" y="44" width="102" height="24" rx="12" className="hero-svg-chip" />
        <rect x="350" y="44" width="118" height="24" rx="12" className="hero-svg-chip hero-svg-chip-warm" />
        <path d="M74 130 C128 102 172 118 214 146 S304 198 356 164 418 118 448 128" className="hero-svg-trace" />
        <path d="M74 228 C126 212 168 224 214 246 S306 288 358 242 420 210 448 220" className="hero-svg-trace hero-svg-trace-alt" />
        <circle cx="74" cy="130" r="6" className="hero-svg-node" />
        <circle cx="214" cy="146" r="7" className="hero-svg-node hero-svg-node-strong" />
        <circle cx="356" cy="164" r="7" className="hero-svg-node hero-svg-node-calm" />
        <circle cx="448" cy="128" r="6" className="hero-svg-node" />
        <circle cx="74" cy="228" r="6" className="hero-svg-node" />
        <circle cx="214" cy="246" r="7" className="hero-svg-node hero-svg-node-warm" />
        <circle cx="358" cy="242" r="7" className="hero-svg-node hero-svg-node-strong" />
        <circle cx="448" cy="220" r="6" className="hero-svg-node" />
      </svg>
    </div>
  );
}

export function ProofRibbonIllustration() {
  return (
    <div className="proof-ribbon-illustration" aria-hidden="true">
      <svg viewBox="0 0 320 72" role="presentation">
        <path d="M10 36 H110" className="proof-svg-line" />
        <circle cx="116" cy="36" r="6" className="proof-svg-dot" />
        <path d="M122 36 H202" className="proof-svg-line proof-svg-line-accent" />
        <circle cx="208" cy="36" r="6" className="proof-svg-dot proof-svg-dot-accent" />
        <path d="M214 36 H310" className="proof-svg-line" />
      </svg>
    </div>
  );
}

export function ProcessDiagramIllustration() {
  return (
    <div className="process-diagram-illustration" aria-hidden="true">
      <svg viewBox="0 0 360 180" role="presentation">
        <rect x="18" y="26" width="88" height="44" rx="12" className="process-svg-box" />
        <rect x="136" y="26" width="88" height="44" rx="12" className="process-svg-box process-svg-box-accent" />
        <rect x="254" y="26" width="88" height="44" rx="12" className="process-svg-box" />
        <rect x="76" y="112" width="88" height="44" rx="12" className="process-svg-box" />
        <rect x="194" y="112" width="88" height="44" rx="12" className="process-svg-box process-svg-box-calm" />
        <path d="M106 48 H136" className="process-svg-line" />
        <path d="M224 48 H254" className="process-svg-line" />
        <path d="M180 70 V112" className="process-svg-line" />
        <path d="M120 112 C138 96 158 90 180 90 C202 90 222 96 238 112" className="process-svg-line process-svg-line-accent" />
        <circle cx="180" cy="90" r="7" className="process-svg-dot" />
      </svg>
    </div>
  );
}
