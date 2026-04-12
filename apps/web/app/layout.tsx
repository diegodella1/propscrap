import "./globals.css";
import "./product-hardening.css";
import type { Metadata } from "next";
import { IBM_Plex_Mono, Inter, Manrope } from "next/font/google";
import { ConditionalFooter } from "../components/conditional-footer";

const bodyFont = Inter({
  subsets: ["latin"],
  variable: "--font-body",
  display: "swap",
});

const displayFont = Manrope({
  subsets: ["latin"],
  variable: "--font-display",
  weight: ["500", "600", "700", "800"],
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
        <a href="#main-content" className="skip-link">
          Ir al contenido principal
        </a>
        <div id="main-content">{children}</div>
        <ConditionalFooter />
      </body>
    </html>
  );
}
