import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "TITOFLIX - Plataforma de Streaming",
  description: "Tu plataforma de streaming favorita. Peliculas, series y mucho mas.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="es" className="bg-background">
      <body className="min-h-screen bg-background text-foreground antialiased">
        {children}
      </body>
    </html>
  );
}
