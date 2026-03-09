import type { Metadata } from "next";
import "../styles/globals.css";

export const metadata: Metadata = {
  title: "Aura Stock | Mexican Online Brokerage",
  description: "Secure, modern stock trading for everyone in Mexico.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className="antialiased selection:bg-primary/30">
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_50%_50%,rgba(112,0,255,0.15),transparent_50%)]" />
        <div className="fixed inset-0 -z-10 bg-[radial-gradient(circle_at_80%_20%,rgba(0,209,255,0.1),transparent_40%)]" />
        <main className="min-h-screen flex flex-col items-center justify-center p-8">
          {children}
        </main>
      </body>
    </html>
  );
}
