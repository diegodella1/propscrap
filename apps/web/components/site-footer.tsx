import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-grid">
        <div className="footer-brand-block">
          <span className="section-kicker" translate="no">EasyTaciones</span>
          <h2>Una plataforma seria para descubrir, evaluar y seguir licitaciones.</h2>
          <p>
            EasyTaciones ordena fuentes, oportunidades y seguimiento en un solo sistema de trabajo para equipos que
            necesitan criterio, trazabilidad y timing.
          </p>
          <div className="footer-metrics">
            <span>Alta por CUIT</span>
            <span>Discovery Priorizado</span>
            <span>Seguimiento Trazable</span>
          </div>
        </div>

        <div className="footer-column">
          <strong>Producto</strong>
          <Link href="/">Inicio</Link>
          <Link href="/about">Cómo Funciona</Link>
          <Link href="/contact">Solicitar Demo</Link>
          <Link href="/signup">Registrar Empresa</Link>
        </div>

        <div className="footer-column">
          <strong>Operación</strong>
          <Link href="/login">Ingresar</Link>
          <Link href="/dashboard">Workspace</Link>
          <Link href="/mi-cuenta">Mi Cuenta</Link>
          <Link href="/saved">Seguimiento</Link>
        </div>
      </div>
    </footer>
  );
}
