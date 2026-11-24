import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { WakeUpBanner } from "@/components/WakeUpBanner";

export const metadata: Metadata = {
  title: "Automated Full-Stack Code Reviewer & Bug-Hunting Bot",
  description: "Enterprise-grade static analysis, isolated sandboxing, and LangGraph agent review platform.",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-[#0a0e17] text-gray-100 antialiased min-h-screen flex flex-col">
        <WakeUpBanner />
        <Navbar />
        <main className="flex-1">{children}</main>
      </body>
    </html>
  );
}
