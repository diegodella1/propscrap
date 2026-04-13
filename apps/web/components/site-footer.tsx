import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-grid">
        <div className="footer-brand-block">
          <span className="section-kicker" translate="no">EasyTaciones</span>
          <h2>Una interfaz presentable para vender, explicar y operar licitaciones sin fricción.</h2>
          <p>
            EasyTaciones convierte un proceso manual y disperso en una operación clara: entrada por CUIT, fuentes gobernadas, oportunidades priorizadas y seguimiento trazable en un solo sistema.
          </p>
          <div className="footer-metrics">
            <span>Alta por CUIT</span>
            <span>Discovery Priorizado</span>
            <span>Seguimiento Trazable</span>
          </div>
        </div>

        <div className="footer-column">
          <strong>Mostrar</strong>
          <Link href="/">Inicio</Link>
          <Link href="/about">Cómo Funciona</Link>
          <Link href="/contact">Solicitar demo</Link>
          <Link href="/signup">Registrar Empresa</Link>
        </div>

        <div className="footer-column">
          <strong>Accesos</strong>
          <Link href="/login">Ingresar</Link>
          <Link href="/login/empresa">Ingreso empresa</Link>
          <Link href="/login/superadmin">Ingreso superadmin</Link>
          <Link href="/dashboard">Workspace</Link>
        </div>
      </div>
    </footer>
  );
}
