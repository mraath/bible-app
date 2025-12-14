import type { Metadata } from "next";
import { Inter, Crimson_Pro } from "next/font/google";
import { Header } from "@/components/Layout/Header";
import { BackgroundLayer } from "@/components/Visuals/BackgroundLayer";
import { Timeline } from "@/components/Timeline/Timeline";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  display: "swap",
});

const crimsonPro = Crimson_Pro({
  subsets: ["latin"],
  variable: "--font-crimson",
  display: "swap",
});

export const metadata: Metadata = {
  title: "Bible App",
  description: "A beautiful, distraction-free Bible reading experience.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.variable} ${crimsonPro.variable}`}>
        <BackgroundLayer />
        <Header />
        <Timeline />
        {children}
      </body>
    </html>
  );
}
