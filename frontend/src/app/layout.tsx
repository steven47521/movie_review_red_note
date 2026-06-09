import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "片语 RedNote",
  description: "经典电影小红书创作助手",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="zh-CN">
      <body>{children}</body>
    </html>
  );
}
