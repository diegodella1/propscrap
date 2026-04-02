import Link from "next/link";

export function SiteFooter() {
  return (
    <footer className="site-footer">
      <div className="site-footer-grid">
        <div>
          <span className="section-kicker">Licitaciones IA</span>
          <h2>Una mesa de control para detectar, evaluar y actuar sobre oportunidades públicas.</h2>
          <p>
            Consolida fuentes, ordena prioridades y deja una operación más sobria y más clara que revisar portales
            sueltos o planillas improvisadas.
          </p>
        </div>

        <div className="footer-column">
          <strong>Producto</strong>
          <Link href="/">Inicio</Link>
          <Link href="/about">Cómo funciona</Link>
          <Link href="/dashboard">Dashboard</Link>
          <Link href="/signup">Crear cuenta</Link>
        </div>

        <div className="footer-column">
          <strong>Cuenta</strong>
          <Link href="/login">Ingresar</Link>
          <Link href="/mi-cuenta">Mi cuenta</Link>
          <Link href="/tenders/1">Ver un dossier</Link>
        </div>
      </div>
    </footer>
  );
}
