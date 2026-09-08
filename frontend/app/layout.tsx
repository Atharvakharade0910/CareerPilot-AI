import localFont from "next/font/local";
import type { Metadata } from "next";
import { Providers } from "@/components/providers";
import "./globals.css";
const geist = localFont({
  src: [
    {
      path: "../node_modules/@fontsource/geist/files/geist-latin-400-normal.woff2",
      weight: "400",
    },
    {
      path: "../node_modules/@fontsource/geist/files/geist-latin-600-normal.woff2",
      weight: "600",
    },
  ],
  variable: "--font-geist",
  display: "swap",
});
export const metadata: Metadata = {
  title: "CareerPilot AI — Your next chapter",
  description:
    "From resume to opportunity, intelligently. Your evidence-first career workspace.",
};
export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className={geist.variable}>
        <Providers>{children}</Providers>
      </body>
    </html>
  );
}
