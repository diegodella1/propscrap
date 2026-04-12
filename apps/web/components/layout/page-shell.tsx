import type { ReactNode } from "react";

export type PageShellVariant = "marketing" | "workspace" | "auth" | "admin";

const variantClass: Record<PageShellVariant, string> = {
  marketing: "page-shell page-shell--marketing",
  workspace: "page-shell page-shell--workspace",
  auth: "page-shell page-shell--auth",
  admin: "page-shell page-shell--admin",
};

type Props = {
  variant?: PageShellVariant;
  className?: string;
  children: ReactNode;
};

export function PageShell({ variant = "workspace", className = "", children }: Props) {
  const base = variantClass[variant];
  return <main className={`${base} ${className}`.trim()}>{children}</main>;
}
