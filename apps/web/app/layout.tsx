import "./globals.css";
import type { Metadata } from "next";
import { IBM_Plex_Mono, IBM_Plex_Sans, Public_Sans } from "next/font/google";
import { SiteFooter } from "../components/site-footer";

const bodyFont = Public_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const displayFont = IBM_Plex_Sans({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "600", "700"],
  display: "swap",
});

const monoFont = IBM_Plex_Mono({
  subsets: ["latin"],
  variable: "--font-mono",
  weight: ["400", "500"],
  display: "swap",
});

export const metadata: Metadata = {
  title: "EasyTaciones | Sistema Operativo de Licitaciones para Proveedores del Estado",
  description:
    "EasyTaciones ayuda a empresas que venden al Estado a ordenar discovery, seguimiento y alertas de licitaciones en un solo sistema.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={`${bodyFont.variable} ${displayFont.variable} ${monoFont.variable}`}>
        {children}
        <SiteFooter />
      </body>
    </html>
  );
}
