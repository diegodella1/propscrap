import Link from "next/link";

type Props = {
  section: "landing" | "about" | "dashboard" | "detail" | "saved" | "admin" | "profile" | "auth" | "account" | "contact";
  currentUserName?: string | null;
  currentUserRole?: string | null;
};

export function SiteHeader({ section, currentUserName, currentUserRole }: Props) {
  const isCompanyAdmin = currentUserRole === "manager";
  const isPlatformAdmin = currentUserRole === "admin";

  return (
    <header className="site-header">
      <Link href="/" className="brand-lockup">
        <span className="brand-mark">ET</span>
        <span>
          <strong translate="no">EasyTaciones</strong>
          <small>Inteligencia operativa para licitaciones</small>
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
          {!currentUserName ? (
            <>
              <Link href="/signup" data-active={section === "auth"}>
                Registro por CUIT
              </Link>
              <Link href="/contact" data-active={section === "contact"}>
                Demo
              </Link>
            </>
          ) : (
            <>
              <Link href="/dashboard" data-active={section === "dashboard" || section === "detail"}>
                Oportunidades
              </Link>
              <Link href="/saved" data-active={section === "saved"}>
                Seguimiento
              </Link>
              <Link href="/company-profile" data-active={section === "profile"}>
                Empresa
              </Link>
              {isCompanyAdmin ? (
                <Link href="/admin/company" data-active={section === "admin"}>
                  Equipo
                </Link>
              ) : null}
              {isPlatformAdmin ? (
                <Link href="/admin/platform" data-active={section === "admin"}>
                  Plataforma
                </Link>
              ) : null}
            </>
          )}
        </nav>

        <div className="site-auth-actions">
          {currentUserName ? (
            <span className="mini-pill">
              {isPlatformAdmin ? "Superadmin" : isCompanyAdmin ? "Manager" : "Usuario"} · {currentUserName}
            </span>
          ) : null}

          {currentUserName ? (
            <>
              <Link
                href="/mi-cuenta"
                className="button-secondary site-auth-button"
                data-active={section === "account"}
              >
                Mi cuenta
              </Link>
              <Link href="/dashboard" className="button-primary site-auth-button">
                Ir al workspace
              </Link>
            </>
          ) : (
            <>
              <Link href="/login" className="button-secondary site-auth-button" data-active={section === "auth"}>
                Ingresar
              </Link>
              <Link href="/contact" className="button-primary site-auth-button">
                Solicitar Demo
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
