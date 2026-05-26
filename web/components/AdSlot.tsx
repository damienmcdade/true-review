'use client';

import { useEffect } from 'react';
import clsx from 'clsx';

declare global {
  interface Window {
    adsbygoogle?: unknown[];
  }
}

type Props = {
  slot: string;
  className?: string;
  format?: 'auto' | 'rectangle' | 'horizontal' | 'vertical';
};

const ADSENSE_CLIENT = process.env.NEXT_PUBLIC_ADSENSE_CLIENT;

export default function AdSlot({ slot, className, format = 'auto' }: Props) {
  useEffect(() => {
    if (!ADSENSE_CLIENT) return;
    try {
      (window.adsbygoogle = window.adsbygoogle || []).push({});
    } catch {
      // ignore — adsense may not be ready
    }
  }, []);

  if (!ADSENSE_CLIENT) {
    return (
      <div
        className={clsx(
          'rounded-xl border border-dashed border-white/10 p-6 text-center text-xs text-white/30',
          className
        )}
      >
        ad slot · {slot} · set NEXT_PUBLIC_ADSENSE_CLIENT to enable
      </div>
    );
  }

  return (
    <ins
      className={clsx('adsbygoogle block', className)}
      style={{ display: 'block' }}
      data-ad-client={ADSENSE_CLIENT}
      data-ad-slot={slot}
      data-ad-format={format}
      data-full-width-responsive="true"
    />
  );
}
