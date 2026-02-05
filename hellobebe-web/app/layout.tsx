import type { Metadata } from "next";
import { Inter, Playfair_Display } from "next/font/google";
import "./globals.css";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

const playfair = Playfair_Display({
  subsets: ["latin"],
  variable: "--font-playfair",
});

export const metadata: Metadata = {
  title: "헬로베베 | 5,900원에 만나는 우리 아이 첫 실사화",
  description: "흐릿한 입체 초음파 사진을 AI 기술로 선명한 아기 얼굴로 변환해드립니다.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ko" className={`${inter.variable} ${playfair.variable}`}>
      <body className="antialiased bg-[var(--color-bg-main)] text-[var(--color-text-main)]">
        {children}
      </body>
    </html>
  );
}
