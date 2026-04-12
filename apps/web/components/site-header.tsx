"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useCallback, useEffect, useId, useState } from "react";

type Props = {
  /** @deprecated El estado activo usa la ruta (pathname); se mantiene por compatibilidad. */
  section?: "landing" | "about" | "dashboard" | "detail" | "saved" | "admin" | "profile" | "auth" | "account" | "contact";
  currentUserName?: string | null;
  currentUserRole?: string | null;
};

export function SiteHeader({ currentUserName, currentUserRole }: Props) {
  const pathname = usePathname() ?? "";
  const [navOpen, setNavOpen] = useState(false);
  const navRegionId = useId();
  const isCompanyAdmin = currentUserRole === "manager";
  const isPlatformAdmin = currentUserRole === "admin";
  const isAuthenticated = Boolean(currentUserName);

  const closeNav = useCallback(() => setNavOpen(false), []);

  useEffect(() => {
    closeNav();
  }, [pathname, closeNav]);

  useEffect(() => {
    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        setNavOpen(false);
      }
    }
    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, []);

  const active = {
    home: pathname === "/",
    about: pathname.startsWith("/about"),
    signup: pathname.startsWith("/signup"),
    contact: pathname.startsWith("/contact"),
    login: pathname.startsWith("/login"),
    dashboard: pathname.startsWith("/dashboard") || pathname.startsWith("/tenders/"),
    saved: pathname.startsWith("/saved"),
    profile: pathname.startsWith("/company-profile"),
    adminCompany: pathname.startsWith("/admin/company"),
    adminPlatform: pathname.startsWith("/admin/platform"),
    account: pathname.startsWith("/mi-cuenta"),
  };

  return (
    <header className="site-header">
      <Link href="/" className="brand-lockup" onClick={closeNav}>
        <span className="brand-mark">ET</span>
        <span>
          <strong translate="no">EasyTaciones</strong>
          <small>Infraestructura operativa para ventas al Estado</small>
        </span>
      </Link>

      <button
        type="button"
        className="site-nav-toggle"
        aria-expanded={navOpen}
        aria-controls={navRegionId}
        onClick={() => setNavOpen((open) => !open)}
      >
        {navOpen ? "Cerrar" : "Menú"}
      </button>

      <div id={navRegionId} className={`site-nav-wrap${navOpen ? " site-nav-wrap--open" : ""}`}>
        <nav className="site-nav" aria-label="Navegación principal">
          <Link href="/" data-active={active.home} onClick={closeNav}>
            Inicio
          </Link>
          <Link href="/about" data-active={active.about} onClick={closeNav}>
            Cómo funciona
          </Link>
          {!isAuthenticated ? (
            <>
              <Link href="/signup" data-active={active.signup} onClick={closeNav}>
                Alta por CUIT
              </Link>
              <Link href="/contact" data-active={active.contact} onClick={closeNav}>
                Contacto
              </Link>
            </>
          ) : (
            <>
              <Link href="/dashboard" data-active={active.dashboard} onClick={closeNav}>
                Oportunidades
              </Link>
              <Link href="/saved" data-active={active.saved} onClick={closeNav}>
                Seguimiento
              </Link>
              <Link href="/company-profile" data-active={active.profile} onClick={closeNav}>
                Empresa
              </Link>
              {isCompanyAdmin ? (
                <Link href="/admin/company" data-active={active.adminCompany} onClick={closeNav}>
                  Equipo
                </Link>
              ) : null}
              {isPlatformAdmin ? (
                <Link href="/admin/platform" data-active={active.adminPlatform} onClick={closeNav}>
                  Plataforma
                </Link>
              ) : null}
            </>
          )}
        </nav>

        <div className="site-auth-actions">
          {isAuthenticated ? (
            <span className="mini-pill" aria-label={`Sesión activa: ${currentUserName}`}>
              {isPlatformAdmin ? "Superadmin" : isCompanyAdmin ? "Manager" : "Usuario"} · {currentUserName}
            </span>
          ) : null}

          {isAuthenticated ? (
            <>
              <Link
                href="/mi-cuenta"
                className="button-secondary site-auth-button"
                data-active={active.account}
                onClick={closeNav}
              >
                Mi cuenta
              </Link>
              <Link href="/dashboard" className="button-primary site-auth-button" onClick={closeNav}>
                Ir al workspace
              </Link>
            </>
          ) : (
            <>
              <Link
                href="/login"
                className="button-secondary site-auth-button"
                data-active={active.login}
                onClick={closeNav}
              >
                Ingresar
              </Link>
              <Link href="/contact" className="button-primary site-auth-button" onClick={closeNav}>
                Hablar con Ventas
              </Link>
            </>
          )}
        </div>
      </div>
    </header>
  );
}
