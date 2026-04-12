"use client";

import { usePathname } from "next/navigation";

import { SiteFooter } from "./site-footer";
import { SiteFooterCompact } from "./site-footer-compact";

const COMPACT_PREFIXES = ["/dashboard", "/saved", "/company-profile", "/mi-cuenta", "/tenders", "/admin"];

export function ConditionalFooter() {
  const pathname = usePathname() ?? "";
  const useCompact = COMPACT_PREFIXES.some((p) => pathname === p || pathname.startsWith(`${p}/`));

  if (useCompact) {
    return <SiteFooterCompact />;
  }

  return <SiteFooter />;
}
