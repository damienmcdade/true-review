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
  },
  other: {
    'google-adsense-account': 'ca-pub-8731629548430880'
  }
};

const ADSENSE_CLIENT = process.env.NEXT_PUBLIC_ADSENSE_CLIENT;

import CookieConsent from '@/components/CookieConsent';

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen font-sans text-ink">
        <a
          href="#main"
          className="sr-only focus:not-sr-only focus:absolute focus:left-3 focus:top-3 focus:z-50 focus:rounded focus:bg-ink focus:px-3 focus:py-2 focus:text-white"
        >
          Skip to main content
        </a>
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
        <div id="main">{children}</div>
        <CookieConsent />
      </body>
    </html>
  );
}
