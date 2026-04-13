import "./globals.css";
import type { Metadata } from "next";
import { DM_Sans, IBM_Plex_Mono, Space_Grotesk } from "next/font/google";
import { ConditionalFooter } from "../components/conditional-footer";

const bodyFont = DM_Sans({
  subsets: ["latin"],
  variable: "--font-body",
  weight: ["400", "500", "700"],
  display: "swap",
});

const displayFont = Space_Grotesk({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "700"],
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
  icons: {
    icon: "/icon.svg",
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className={`${bodyFont.variable} ${displayFont.variable} ${monoFont.variable}`}>
        <a href="#main-content" className="skip-link">
          Ir al contenido principal
        </a>
        <div id="main-content">{children}</div>
        <ConditionalFooter />
      </body>
    </html>
  );
}
