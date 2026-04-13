import Link from "next/link";

export function SiteFooterCompact() {
  return (
    <footer className="site-footer site-footer--compact" role="contentinfo">
      <div className="site-footer-compact-inner">
        <span className="footer-compact-brand" translate="no">
          EasyTaciones
        </span>
        <nav className="site-footer-compact-nav" aria-label="Enlaces mínimos">
          <Link href="/">Inicio</Link>
          <Link href="/about">Cómo funciona</Link>
          <Link href="/contact">Contacto</Link>
        </nav>
      </div>
    </footer>
  );
}
