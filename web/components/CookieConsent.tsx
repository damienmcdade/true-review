'use client';

import { useEffect, useState } from 'react';
import Link from 'next/link';

const STORAGE_KEY = 'tr-cookie-consent-v1';

export default function CookieConsent() {
  const [show, setShow] = useState(false);

  useEffect(() => {
    try {
      const v = localStorage.getItem(STORAGE_KEY);
      if (!v) setShow(true);
    } catch {
      // localStorage blocked — assume EU/UK and show banner conservatively.
      setShow(true);
    }
  }, []);

  function decide(value: 'accepted' | 'rejected') {
    try {
      localStorage.setItem(STORAGE_KEY, value);
    } catch {
      // ignore
    }
    setShow(false);
  }

  if (!show) return null;

  return (
    <div
      role="dialog"
      aria-live="polite"
      aria-label="Cookie preferences"
      className="fixed inset-x-3 bottom-3 z-50 mx-auto max-w-2xl"
    >
      <div className="glass rounded-2xl p-4 text-sm shadow-2xl">
        <p className="text-ink/85">
          We use essential cookies for the site and, if you consent, ad cookies via Google
          AdSense to keep True Review free. See our{' '}
          <Link href="/privacy" className="underline">
            privacy policy
          </Link>{' '}
          and{' '}
          <Link href="/cookies" className="underline">
            cookie details
          </Link>
          .
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <button
            onClick={() => decide('rejected')}
            className="rounded-full border border-ink/15 bg-white/60 px-4 py-1.5 text-sm hover:bg-white"
          >
            Reject non-essential
          </button>
          <button
            onClick={() => decide('accepted')}
            className="rounded-full bg-ocean px-4 py-1.5 text-sm font-medium text-white hover:bg-oceanDeep"
          >
            Accept all
          </button>
        </div>
      </div>
    </div>
  );
}
