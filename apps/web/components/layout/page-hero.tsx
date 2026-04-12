import type { ReactNode } from "react";

type Props = {
  eyebrow: string;
  title: ReactNode;
  description?: ReactNode;
  className?: string;
};

export function PageHero({ eyebrow, title, description, className = "hero hero-app" }: Props) {
  return (
    <section className={className}>
      <div>
        <span className="eyebrow">{eyebrow}</span>
        <h1>{title}</h1>
      </div>
      {description ? <p>{description}</p> : null}
    </section>
  );
}
