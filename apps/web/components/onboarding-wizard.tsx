"use client";

import Link from "next/link";
import { useEffect, useMemo, useState } from "react";

type WizardVariant = "company" | "superadmin";

export type OnboardingStep = {
  id: string;
  title: string;
  body: string;
  href: string;
  cta: string;
  complete?: boolean;
  evidence?: string;
};

type WizardContent = {
  eyebrow: string;
  title: string;
  description: string;
  steps: OnboardingStep[];
};

const DEFAULT_WIZARD_STEPS: Record<WizardVariant, WizardContent> = {
  company: {
    eyebrow: "Primer recorrido",
    title: "Configurá la operación de tu empresa",
    description: "Este recorrido te deja listo para recibir oportunidades útiles, guardarlas y seguirlas con criterio.",
    steps: [
      {
        id: "alerts",
        title: "Completá tu canal de alertas",
        body: "Definí email, WhatsApp o Telegram para no depender solo del dashboard.",
        href: "/mi-cuenta",
        cta: "Ir a mi cuenta",
      },
      {
        id: "profile",
        title: "Ajustá el perfil comercial",
        body: "Cargá buyers, keywords, exclusiones y jurisdicciones para mejorar el matching.",
        href: "/company-profile",
        cta: "Editar perfil",
      },
      {
        id: "pipeline",
        title: "Guardá la primera licitación relevante",
        body: "Entrá al discovery, abrí dossiers y mandá al pipeline lo que vale seguir.",
        href: "/dashboard",
        cta: "Abrir oportunidades",
      },
      {
        id: "follow-up",
        title: "Ordená el seguimiento",
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
        id: "sources",
        title: "Revisá las fuentes base",
        body: "Validá COMPR.AR, PBAC y Boletín Oficial, y agregá o editá fuentes desde la consola.",
        href: "/admin/platform#admin-sources",
        cta: "Ir a fuentes",
      },
      {
        id: "llm",
        title: "Configurá OpenAI y prompt maestro",
        body: "Definí API key, modelo y prompt maestro para scoring, resumen y extracción asistida.",
        href: "/admin/platform#admin-automation",
        cta: "Ir a IA",
      },
      {
        id: "delivery",
        title: "Activá canales de delivery",
        body: "Cargá Resend, Meta WhatsApp o Telegram y dejá listos los canales instantáneos.",
        href: "/admin/platform#admin-automation",
        cta: "Ir a delivery",
      },
      {
        id: "users",
        title: "Verificá usuarios y auditoría",
        body: "Controlá roles, ABM, eventos administrativos y corridas para salir a campo con criterio.",
        href: "/admin/platform#admin-users",
        cta: "Ir a usuarios",
      },
    ],
  },
};

function countCompleted(steps: OnboardingStep[]) {
  return steps.filter((step) => step.complete).length;
}

export function OnboardingWizard({
  variant,
  forceOpen = false,
  content,
}: {
  variant: WizardVariant;
  forceOpen?: boolean;
  content?: Partial<WizardContent>;
}) {
  const mergedContent = useMemo<WizardContent>(() => {
    const defaults = DEFAULT_WIZARD_STEPS[variant];
    return {
      eyebrow: content?.eyebrow ?? defaults.eyebrow,
      title: content?.title ?? defaults.title,
      description: content?.description ?? defaults.description,
      steps: content?.steps ?? defaults.steps,
    };
  }, [content, variant]);

  const storageKey = `easytaciones-onboarding-${variant}-v2`;
  const completionToken = mergedContent.steps
    .map((step) => `${step.id}:${step.complete ? "1" : "0"}`)
    .join("|");
  const completedCount = countCompleted(mergedContent.steps);
  const firstIncompleteIndex = mergedContent.steps.findIndex((step) => !step.complete);
  const allDone = completedCount === mergedContent.steps.length;
  const recommendedIndex = firstIncompleteIndex >= 0 ? firstIncompleteIndex : mergedContent.steps.length - 1;

  const [open, setOpen] = useState(false);
  const [stepIndex, setStepIndex] = useState(recommendedIndex);

  useEffect(() => {
    setStepIndex(recommendedIndex);
  }, [recommendedIndex]);

  useEffect(() => {
    if (typeof window === "undefined") return;
    const completedSignature = window.localStorage.getItem(storageKey);
    const shouldOpen = forceOpen || !allDone || completedSignature !== completionToken;

    if (shouldOpen) {
      setOpen(true);
    }
  }, [allDone, completionToken, forceOpen, storageKey]);

  useEffect(() => {
    if (!open) return;

    function onKeyDown(event: KeyboardEvent) {
      if (event.key === "Escape") {
        if (typeof window !== "undefined") {
          window.localStorage.setItem(storageKey, completionToken);
        }
        setOpen(false);
      }
    }

    window.addEventListener("keydown", onKeyDown);
    return () => window.removeEventListener("keydown", onKeyDown);
  }, [completionToken, open, storageKey]);

  function closeWizard() {
    if (typeof window !== "undefined") {
      window.localStorage.setItem(storageKey, completionToken);
    }
    setOpen(false);
  }

  if (!open) return null;

  const currentStep = mergedContent.steps[stepIndex];
  const nextIncomplete = mergedContent.steps.find((step) => !step.complete && step.id !== currentStep.id);
  const isLastStep = stepIndex === mergedContent.steps.length - 1;

  return (
    <div className="wizard-overlay" role="dialog" aria-modal="true" aria-labelledby={`wizard-title-${variant}`}>
      <div className="wizard-card">
        <div className="wizard-header">
          <span className="section-kicker">{mergedContent.eyebrow}</span>
          <h2 id={`wizard-title-${variant}`}>{mergedContent.title}</h2>
          <p>{mergedContent.description}</p>
          <div className="wizard-status-bar" aria-live="polite">
            <span className="badge tone-calm">
              {completedCount}/{mergedContent.steps.length} completos
            </span>
            <span className={`badge ${allDone ? "tone-success" : ""}`}>
              {allDone ? "Checklist completo" : "Quedan pasos pendientes"}
            </span>
          </div>
        </div>

        <div className="wizard-progress" aria-label="Progreso del wizard">
          {mergedContent.steps.map((step, index) => (
            <button
              key={step.id}
              type="button"
              className={`wizard-progress-step${index === stepIndex ? " wizard-progress-step--active" : ""}${step.complete ? " wizard-progress-step--complete" : ""}`}
              onClick={() => setStepIndex(index)}
              aria-label={`Paso ${index + 1}: ${step.title}`}
            >
              {step.complete ? "✓" : index + 1}
            </button>
          ))}
        </div>

        <article className="wizard-step-card">
          <div className="wizard-step-meta">
            <span className="section-kicker">Paso {stepIndex + 1}</span>
            <span className={`badge ${currentStep.complete ? "tone-success" : "tone-calm"}`}>
              {currentStep.complete ? "Completo" : "Pendiente"}
            </span>
          </div>
          <h3>{currentStep.title}</h3>
          <p>{currentStep.body}</p>
          {currentStep.evidence ? <p className="wizard-step-evidence">{currentStep.evidence}</p> : null}
        </article>

        <div className="wizard-actions">
          <Link href={currentStep.href} className="button-primary">
            {currentStep.cta}
          </Link>
          {!isLastStep ? (
            <button type="button" className="button-secondary" onClick={() => setStepIndex((current) => current + 1)}>
              Siguiente paso
            </button>
          ) : nextIncomplete ? (
            <button
              type="button"
              className="button-secondary"
              onClick={() =>
                setStepIndex(mergedContent.steps.findIndex((step) => step.id === nextIncomplete.id))
              }
            >
              Ir al siguiente pendiente
            </button>
          ) : (
            <button type="button" className="button-secondary" onClick={closeWizard}>
              Cerrar checklist
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
