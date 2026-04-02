import Link from "next/link";

type Props = {
  section: "landing" | "about" | "dashboard" | "detail" | "admin" | "profile" | "auth" | "account";
  currentUserName?: string | null;
};

export function SiteHeader({ section, currentUserName }: Props) {
  return (
    <header className="site-header">
      <Link href="/" className="brand-lockup">
        <span className="brand-mark">LI</span>
        <span>
          <strong>Licitaciones IA</strong>
          <small>Inteligencia operativa para compras públicas</small>
        </span>
      </Link>

      <div className="site-nav-wrap">
        <nav className="site-nav" aria-label="Navegación principal">
          <Link href="/" data-active={section === "landing"}>
            Inicio
          </Link>
          <Link href="/about" data-active={section === "about"}>
            Cómo funciona
          </Link>
          <Link href="/dashboard" data-active={section === "dashboard" || section === "detail"}>
            Dashboard
          </Link>
        </nav>
        <div className="site-auth-actions">
          {currentUserName ? (
            <span className="mini-pill">Hola, {currentUserName}</span>
          ) : null}
          {currentUserName ? (
            <Link
              href="/mi-cuenta"
              className="button-secondary site-auth-button"
              data-active={section === "account"}
            >
              Mi cuenta
            </Link>
          ) : (
            <>
              <Link href="/login" className="button-secondary site-auth-button" data-active={section === "auth"}>
                Ingresar
              </Link>
              <Link href="/signup" className="button-primary site-auth-button">
                Crear cuenta
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
