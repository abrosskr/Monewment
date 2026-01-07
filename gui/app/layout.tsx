import type { Metadata } from "next";
import "./globals.css";
import LayoutProvider from "@/components/LayoutProvider";
import MasterLayout from "@/components/MasterLayout";

export const metadata: Metadata = {
  title: "Monewment Platform",
  description: "Enterprise GenAI Cluster System",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" suppressHydrationWarning>
      <body className="bg-[#0f172a] text-[#E5E5E5] font-sans antialiased overflow-hidden">
        <LayoutProvider>
          <MasterLayout>
            {children}
          </MasterLayout>
        </LayoutProvider>
      </body>
    </html>
  );
}