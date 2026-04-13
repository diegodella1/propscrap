import Link from "next/link";

import { ContactRequestForm } from "../../../components/contact-request-form";
import { PageShell } from "../../../components/layout/page-shell";
import { SiteHeader } from "../../../components/site-header";
import { fetchPublicPlatformSettings } from "../../../lib/api";

export default async function ContactPage() {
  const platformSettings = await fetchPublicPlatformSettings();

  return (
    <PageShell variant="marketing" className="page-screen page-screen--contact">
      <SiteHeader section="contact" audience="public" />

      <section className="hero hero-app about-hero">
        <div>
          <span className="eyebrow">Solicitar Demo</span>
          <h1>La demo tiene que dejar una prueba de 30 días lista para usar.</h1>
        </div>
        <p>En pocos minutos se ve cómo entra la empresa, cómo aparece el discovery y qué tendría que pasar para que el equipo adopte el producto de verdad.</p>
      </section>

      <section className="auth-layout auth-layout-upgraded signup-shell contact-shell">
        <ContactRequestForm platformSettings={platformSettings} />

        <article className="panel dispatch-panel onboarding-companion signup-companion contact-companion">
          <span className="section-kicker">Qué se ve en la demo</span>
          <h2>El flujo completo de una prueba útil.</h2>
          <div className="onboarding-proof-list">
            <article>
              <strong>Empresa por CUIT</strong>
              <p>Alta rápida con base legal y perfil inicial para no empezar desde cero.</p>
            </article>
            <article>
              <strong>Discovery ordenado</strong>
              <p>Una sola vista para oportunidades, prioridad, fecha límite y contexto.</p>
            </article>
            <article>
              <strong>Seguimiento real</strong>
              <p>Pipeline, notas, alertas y rutina diaria dentro de la misma plataforma.</p>
            </article>
          </div>
          <div className="hero-actions">
            <Link href="/signup" className="button-secondary">
              Registrar Empresa
            </Link>
            {platformSettings.demo_booking_url ? (
              <a href={platformSettings.demo_booking_url} className="button-primary">
                Agendar demo
              </a>
            ) : null}
            <Link href="/about" className="button-secondary">
              Ver Cómo Funciona
            </Link>
          </div>

          {platformSettings.contact_whatsapp_number || platformSettings.contact_telegram_handle ? (
            <div className="signup-confidence-bar">
              {platformSettings.contact_whatsapp_number ? <span>WhatsApp {platformSettings.contact_whatsapp_number}</span> : null}
              {platformSettings.contact_telegram_handle ? <span>Telegram {platformSettings.contact_telegram_handle}</span> : null}
            </div>
          ) : null}
        </article>

        <article className="panel dispatch-panel contact-qualification-panel">
          <span className="section-kicker">Calce comercial</span>
          <h2>Cuándo conviene verla.</h2>
          <div className="source-stack">
            <article className="source-card">
              <strong>Volumen</strong>
              <p>Tu equipo revisa muchas fuentes, documentos y cierres y ya siente el costo del seguimiento manual.</p>
            </article>
            <article className="source-card">
              <strong>Buyer</strong>
              <p>Dueño, gerente comercial o responsable de licitaciones que hoy carga el peso operativo del proceso.</p>
            </article>
            <article className="source-card">
              <strong>Resultado</strong>
              <p>Menos tiempo perdido y una operación diaria que un cliente pueda sostener durante 30 días.</p>
            </article>
          </div>

          <div className="detail-note-card">
            <span className="section-kicker">Ideal para la demo</span>
            <p>Empresas proveedoras con responsables comerciales que hoy hacen discovery y seguimiento a mano.</p>
          </div>
        </article>
      </section>
    </PageShell>
  );
}
