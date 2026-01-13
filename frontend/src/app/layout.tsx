import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import { ClerkProvider } from "@clerk/nextjs";
import { Toaster } from "sonner";
import { ErrorBoundary } from "@/components/error-boundary";
import { BackendGate } from "@/components/backend-gate";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Prompt Master - AI Prompt Optimizer",
  description: "Multi-Agent Prompt Reviewer & Optimizer",
  icons: {
    icon: "/favicon.ico",
    shortcut: "/favicon.ico",
    apple: "/favicon.ico",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <ClerkProvider>
      <html lang="en" className="dark">
        <head>
          <link rel="icon" href="/favicon.ico" />
          {/* Google tag (gtag.js) - placed immediately after <head> */}
          <script
            async
            src="https://www.googletagmanager.com/gtag/js?id=G-1M7VGBTNWX"
          />
          <script
            dangerouslySetInnerHTML={{
              __html: `
                window.dataLayer = window.dataLayer || [];
                function gtag(){dataLayer.push(arguments);}
                gtag('js', new Date());
                gtag('config', 'G-1M7VGBTNWX');
              `,
            }}
          />
        </head>
        <body
          className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background`}
        >
          <ErrorBoundary>
            <BackendGate>{children}</BackendGate>
          </ErrorBoundary>
          <Toaster position="top-right" theme="dark" richColors />
        </body>
      </html>
    </ClerkProvider>
  );
}
