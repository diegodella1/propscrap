"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

type WizardVariant = "company" | "superadmin";

type Step = {
  title: string;
  body: string;
  href: string;
  cta: string;
};

const WIZARD_STEPS: Record<
  WizardVariant,
  {
    eyebrow: string;
    title: string;
    description: string;
    steps: Step[];
  }
> = {
  company: {
    eyebrow: "Primer recorrido",
    title: "Configurá la operación de tu empresa",
    description: "Este recorrido te deja listo para recibir oportunidades útiles, guardarlas y seguirlas con criterio.",
    steps: [
      {
        title: "1. Completá tu canal de alertas",
        body: "Definí email, WhatsApp o Telegram para no depender solo del dashboard.",
        href: "/mi-cuenta",
        cta: "Ir a mi cuenta",
      },
      {
        title: "2. Ajustá el perfil comercial",
        body: "Cargá buyers, keywords, exclusiones y jurisdicciones para mejorar el matching.",
        href: "/company-profile",
        cta: "Editar perfil",
      },
      {
        title: "3. Mirá oportunidades y guardá las relevantes",
        body: "Entrá al discovery, abrí dossiers y mandá al pipeline lo que vale seguir.",
        href: "/dashboard",
        cta: "Abrir oportunidades",
      },
      {
        title: "4. Ordená el seguimiento",
        body: "Usá pipeline y notas para sostener las licitaciones activas sin perder timing.",
        href: "/saved",
        cta: "Ver pipeline",
      },
    ],
  },
  superadmin: {
    eyebrow: "Primer recorrido",
    title: "Dejá la plataforma operativa",
    description: "Este recorrido te deja con fuentes, canales y automatización listos para trabajar con empresas reales.",
    steps: [
      {
        title: "1. Revisá las fuentes base",
        body: "Validá COMPR.AR, PBAC y Boletín Oficial, y agregá o editá fuentes desde la consola.",
        href: "/admin/platform#admin-sources",
        cta: "Ir a fuentes",
      },
      {
        title: "2. Configurá OpenAI y prompt maestro",
        body: "Definí API key, modelo y master prompt para scoring, resumen y extracción asistida.",
        href: "/admin/platform#admin-automation",
        cta: "Ir a IA",
      },
      {
        title: "3. Activá canales de delivery",
        body: "Cargá Resend, Meta WhatsApp o Telegram y dejá listos los canales instantáneos.",
        href: "/admin/platform#admin-automation",
        cta: "Ir a delivery",
      },
      {
        title: "4. Verificá usuarios y auditoría",
        body: "Controlá roles, ABM, eventos administrativos y corridas para salir a campo con criterio.",
        href: "/admin/platform#admin-users",
        cta: "Ir a usuarios",
      },
    ],
  },
};

export function OnboardingWizard({
  variant,
  forceOpen = false,
}: {
  variant: WizardVariant;
  forceOpen?: boolean;
}) {
  const storageKey = `easytaciones-onboarding-${variant}-v1`;
  const content = WIZARD_STEPS[variant];
  const [open, setOpen] = useState(false);
  const [stepIndex, setStepIndex] = useState(0);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const completed = window.localStorage.getItem(storageKey) === "done";
    if (forceOpen || !completed) {
      setOpen(true);
    }
  }, [forceOpen, storageKey]);

  function closeWizard() {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(storageKey, "done");
    }
    setOpen(false);
  }

  if (!open) return null;

  const currentStep = content.steps[stepIndex];
  const isLastStep = stepIndex === content.steps.length - 1;

  return (
    <div className="wizard-overlay" role="dialog" aria-modal="true" aria-labelledby={`wizard-title-${variant}`}>
      <div className="wizard-card">
        <div className="wizard-header">
          <span className="section-kicker">{content.eyebrow}</span>
          <h2 id={`wizard-title-${variant}`}>{content.title}</h2>
          <p>{content.description}</p>
        </div>

        <div className="wizard-progress" aria-label="Progreso del wizard">
          {content.steps.map((step, index) => (
            <button
              key={step.title}
              type="button"
              className={`wizard-progress-step${index === stepIndex ? " wizard-progress-step--active" : ""}`}
              onClick={() => setStepIndex(index)}
            >
              {index + 1}
            </button>
          ))}
        </div>

        <article className="wizard-step-card">
          <span className="section-kicker">Paso {stepIndex + 1}</span>
          <h3>{currentStep.title}</h3>
          <p>{currentStep.body}</p>
        </article>

        <div className="wizard-actions">
          <Link href={currentStep.href} className="button-primary">
            {currentStep.cta}
          </Link>
          {!isLastStep ? (
            <button type="button" className="button-secondary" onClick={() => setStepIndex((current) => current + 1)}>
              Siguiente
            </button>
          ) : (
            <button type="button" className="button-secondary" onClick={closeWizard}>
              Terminar
            </button>
          )}
          <button type="button" className="linkish" onClick={closeWizard}>
            Cerrar guía
          </button>
        </div>
      </div>
    </div>
  );
}
