import "./globals.css";
import type { Metadata } from "next";
import { SiteFooter } from "../components/site-footer";

export const metadata: Metadata = {
  title: "Licitaciones IA | Tender intelligence para Argentina",
  description: "POC funcional de inteligencia, priorización y seguimiento de licitaciones en Argentina.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body>
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
