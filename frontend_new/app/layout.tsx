import type { Metadata } from "next";
import { Fraunces, Space_Grotesk } from "next/font/google";
import AppShell from "@/components/AppShell";
import "./globals.css";

const headingFont = Fraunces({
  variable: "--font-heading",
  subsets: ["latin"],
});

const bodyFont = Space_Grotesk({
  variable: "--font-body",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Plant Disease Classification",
  description: "Next.js frontend for plant disease prediction and model insights",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${headingFont.variable} ${bodyFont.variable}`}>
        <AppShell>{children}</AppShell>
      </body>
    </html>
  );
}
