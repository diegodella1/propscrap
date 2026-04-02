import Link from "next/link";

import { SiteHeader } from "./site-header";
import { UserEditorList } from "./user-editor-list";
import type { User } from "../lib/api";

type Props = {
  currentUserName: string;
  users: User[];
};

export function CompanyAdminPage({ currentUserName, users }: Props) {
  return (
    <main className="page-shell">
      <SiteHeader section="admin" currentUserName={currentUserName} />

      <section className="hero hero-app">
        <div>
          <span className="eyebrow">Admin de empresa</span>
          <h1>Administración de tu empresa.</h1>
        </div>
        <p>Desde acá gestionás tu perfil comercial y tu equipo. No ves otras empresas ni la configuración global de la plataforma.</p>
      </section>

      <section className="stats-grid">
        <article className="stat-card">
          <div className="stat-label">Equipo</div>
          <div className="stat-value">{users.length}</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Rol</div>
          <div className="stat-value">Empresa</div>
        </article>
        <article className="stat-card">
          <div className="stat-label">Scope</div>
          <div className="stat-value">1 empresa</div>
        </article>
      </section>

      <section className="admin-control-grid">
        <article className="panel dispatch-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Perfil</span>
              <h2>Cómo quiere comprar tu empresa</h2>
            </div>
            <p>Definí keywords, compradores, jurisdicciones y criterios de matching solo para tu empresa.</p>
          </div>
          <div className="hero-actions">
            <Link href="/company-profile" className="button-primary">
              Editar perfil comercial
            </Link>
          </div>
        </article>
      </section>

      <section style={{ display: "grid", gap: 20 }}>
        <article className="panel table-panel">
          <div className="results-header">
            <div>
              <span className="section-kicker">Usuarios</span>
              <h2>Usuarios de tu empresa</h2>
            </div>
            <p>Solo podés ver y editar usuarios de tu empresa. No hay acceso a otras cuentas ni a configuración global.</p>
          </div>
          <UserEditorList users={users} />
        </article>
      </section>
    </main>
  );
}
