'use client';

import { useState } from 'react';
import { Info, ChevronDown, ShieldCheck, AlertCircle } from 'lucide-react';
import clsx from 'clsx';

type Props = {
  source: string | null | undefined;
  explainer: string | null | undefined;
  isDemo: boolean;
  className?: string;
};

/**
 * Compact verification badge with a collapsible "ⓘ" info popover.
 *
 * - Default state: collapsed. Only the badge text + an info icon are visible.
 * - When the user clicks the badge OR the info icon, a 1-2 sentence
 *   explanation expands inline beneath it.
 * - Keyboard accessible: button with aria-expanded; explanation has role=region.
 * - Demo content is visually distinct (warn color) from real verification.
 */
export default function ReviewVerifiedBadge({ source, explainer, isDemo, className }: Props) {
  const [open, setOpen] = useState(false);
  if (!source) return null;

  const tone = isDemo
    ? 'bg-warn/15 text-warn'
    : source === 'Unverified'
      ? 'bg-ink/10 text-ink/55'
      : 'bg-verified/15 text-verified';

  return (
    <div className={clsx('w-full', className)}>
      <button
        type="button"
        aria-expanded={open}
        aria-controls={`verif-${useId(source + explainer)}`}
        onClick={() => setOpen((v) => !v)}
        className={clsx(
          'inline-flex items-center gap-1.5 rounded-full px-2 py-0.5 text-[11px] font-medium transition',
          tone,
          'hover:opacity-90'
        )}
      >
        {isDemo ? (
          <AlertCircle className="h-3 w-3" />
        ) : source === 'Unverified' ? (
          <Info className="h-3 w-3" />
        ) : (
          <ShieldCheck className="h-3 w-3" />
        )}
        {source}
        <ChevronDown
          className={clsx('h-3 w-3 transition-transform', open && 'rotate-180')}
        />
      </button>

      {open && explainer ? (
        <div
          id={`verif-${useId(source + explainer)}`}
          role="region"
          className="mt-2 rounded-xl bg-white/55 px-3 py-2 text-[11px] leading-relaxed text-ink/70"
        >
          {explainer}
        </div>
      ) : null}
    </div>
  );
}

// Stable hash for ARIA ids. Avoids importing useId from react to keep
// this file React 17/18 friendly across hosts.
function useId(seed: string): string {
  let h = 0;
  for (let i = 0; i < seed.length; i++) h = (h * 31 + seed.charCodeAt(i)) | 0;
  return Math.abs(h).toString(36);
}
