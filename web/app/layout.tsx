import type { Metadata } from 'next';
import Script from 'next/script';
import BeachBackground from '@/components/BeachBackground';
import './globals.css';

export const metadata: Metadata = {
  title: 'True Review — Verified company culture intelligence',
  description:
    'AI-native company review platform with verified employment, transparent moderation, and real workplace truth. Free for everyone.',
  openGraph: {
    title: 'True Review',
    description: 'Verified company culture intelligence.',
    type: 'website'
  }
};

const ADSENSE_CLIENT = process.env.NEXT_PUBLIC_ADSENSE_CLIENT;

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans text-ink">
        <BeachBackground />
        {ADSENSE_CLIENT ? (
          <Script
            id="adsense"
            async
            strategy="afterInteractive"
            src={`https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=${ADSENSE_CLIENT}`}
            crossOrigin="anonymous"
          />
        ) : null}
        {children}
      </body>
    </html>
  );
}
