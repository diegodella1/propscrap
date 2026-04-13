import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-grid">
        <div className="footer-brand-block">
          <span className="section-kicker" translate="no">EasyTaciones</span>
          <h2>Discovery, seguimiento y alertas en una interfaz más clara.</h2>
          <p>
            EasyTaciones convierte un proceso manual y disperso en una operación más legible: alta por CUIT, fuentes gobernadas, top priorizado y seguimiento trazable en un solo sistema.
          </p>
          <div className="footer-metrics">
            <span>Alta por CUIT</span>
            <span>Top Priorizado</span>
            <span>Pipeline Activo</span>
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
