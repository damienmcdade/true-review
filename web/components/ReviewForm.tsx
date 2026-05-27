'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Send, AlertTriangle, Briefcase, ShoppingBag } from 'lucide-react';
import clsx from 'clsx';

type ReviewType = 'employment' | 'shopping' | 'scam_report';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

const SCAM_CATEGORIES = [
  ['non_delivery', 'Non-delivery'],
  ['phishing', 'Phishing'],
  ['fake_product', 'Fake product'],
  ['counterfeit', 'Counterfeit'],
  ['fake_job', 'Fake job listing'],
  ['fake_invoice', 'Fake invoice / fee scam'],
  ['subscription_trap', 'Subscription trap'],
  ['other', 'Other']
] as const;

export default function ReviewForm({ className }: { className?: string }) {
  const router = useRouter();
  const [type, setType] = useState<ReviewType>('employment');
  const [companySlug, setCompanySlug] = useState('');
  const [title, setTitle] = useState('');
  const [body, setBody] = useState('');
  const [rating, setRating] = useState(4);
  const [department, setDepartment] = useState('');
  const [product, setProduct] = useState('');
  const [scamCategory, setScamCategory] = useState<string>('non_delivery');
  const [moneyLost, setMoneyLost] = useState<string>('');
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  function slugify(s: string): string {
    return s
      .toLowerCase()
      .trim()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');
  }

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (body.trim().length < 20) {
      setError('Review body must be at least 20 characters.');
      return;
    }
    const slug = slugify(companySlug);
    if (!slug) {
      setError('Please enter a company name.');
      return;
    }
    const payload: Record<string, unknown> = {
      company_slug: slug,
      review_type: type,
      title: title.trim(),
      body: body.trim(),
      rating_overall: type === 'scam_report' ? 1 : rating
    };
    if (type === 'employment' && department) payload.department = department;
    if (type === 'shopping' && product) payload.product_or_service = product;
    if (type === 'scam_report') {
      payload.scam_category = scamCategory;
      if (moneyLost) payload.money_lost = parseFloat(moneyLost);
    }

    startTransition(async () => {
      try {
        const res = await fetch(`${API}/reviews`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });
        if (!res.ok) {
          const txt = await res.text();
          setError(`Submission failed: ${txt.slice(0, 200)}`);
          return;
        }
        router.push(`/c/${slug}` as never);
      } catch {
        setError('Could not reach the API.');
      }
    });
  }

  return (
    <form onSubmit={onSubmit} className={className}>
      <div className="grid grid-cols-3 gap-2">
        <TypeButton selected={type === 'employment'} onClick={() => setType('employment')} icon={<Briefcase className="h-4 w-4" />} label="Employment" />
        <TypeButton selected={type === 'shopping'} onClick={() => setType('shopping')} icon={<ShoppingBag className="h-4 w-4" />} label="Shopping" />
        <TypeButton selected={type === 'scam_report'} onClick={() => setType('scam_report')} icon={<AlertTriangle className="h-4 w-4" />} label="Scam" scam />
      </div>

      <Label className="mt-5">Company name</Label>
      <input
        value={companySlug}
        onChange={(e) => setCompanySlug(e.target.value)}
        placeholder="e.g. Patagonia or quickrich-invest-xyz"
        className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
      />

      <Label className="mt-4">Title</Label>
      <input
        value={title}
        onChange={(e) => setTitle(e.target.value)}
        maxLength={200}
        placeholder="Short summary of your experience"
        className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
      />

      <Label className="mt-4">Details</Label>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        rows={5}
        placeholder="What happened? Be specific. Evidence-based posts get higher trust scores."
        className="mt-1 w-full resize-none rounded-2xl border border-white/60 bg-white/80 p-4 text-ink outline-none focus:border-ocean"
      />

      {type === 'employment' ? (
        <>
          <Label className="mt-4">Department (optional)</Label>
          <input
            value={department}
            onChange={(e) => setDepartment(e.target.value)}
            placeholder="Engineering, Sales, Operations…"
            className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
          />
        </>
      ) : null}

      {type === 'shopping' ? (
        <>
          <Label className="mt-4">Product or service (optional)</Label>
          <input
            value={product}
            onChange={(e) => setProduct(e.target.value)}
            placeholder="e.g. Down Sweater jacket"
            className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
          />
        </>
      ) : null}

      {type === 'scam_report' ? (
        <>
          <Label className="mt-4">Scam category</Label>
          <select
            value={scamCategory}
            onChange={(e) => setScamCategory(e.target.value)}
            className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
          >
            {SCAM_CATEGORIES.map(([v, l]) => (
              <option key={v} value={v}>
                {l}
              </option>
            ))}
          </select>

          <Label className="mt-4">Money lost (USD, optional)</Label>
          <input
            type="number"
            min={0}
            step={0.01}
            value={moneyLost}
            onChange={(e) => setMoneyLost(e.target.value)}
            placeholder="0.00"
            className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
          />
        </>
      ) : (
        <>
          <Label className="mt-4">Overall rating</Label>
          <div className="mt-2 flex items-center gap-2">
            {[1, 2, 3, 4, 5].map((v) => (
              <button
                key={v}
                type="button"
                onClick={() => setRating(v)}
                className={clsx(
                  'h-9 w-9 rounded-full text-sm font-semibold',
                  v <= rating ? 'bg-sunset text-ink' : 'bg-white/60 text-ink/55 hover:bg-white'
                )}
              >
                {v}
              </button>
            ))}
          </div>
        </>
      )}

      {error ? (
        <p className="mt-4 rounded-2xl border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
          {error}
        </p>
      ) : null}

      <div className="mt-6 flex items-center justify-end">
        <button
          type="submit"
          disabled={pending}
          className="inline-flex items-center gap-2 rounded-full bg-ocean px-5 py-2.5 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          Submit review
        </button>
      </div>
    </form>
  );
}

function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <label className={'block text-xs font-semibold uppercase tracking-wider text-ink/55 ' + (className ?? '')}>
      {children}
    </label>
  );
}

function TypeButton({
  selected,
  onClick,
  icon,
  label,
  scam
}: {
  selected: boolean;
  onClick: () => void;
  icon: React.ReactNode;
  label: string;
  scam?: boolean;
}) {
  return (
    <button
      type="button"
      onClick={onClick}
      className={clsx(
        'flex items-center justify-center gap-2 rounded-2xl border px-3 py-2.5 text-sm font-medium transition',
        selected
          ? scam
            ? 'border-scam/60 bg-scam/15 text-scam'
            : 'border-ocean/60 bg-ocean/15 text-oceanDeep'
          : 'border-white/60 bg-white/40 text-ink/75 hover:bg-white/70'
      )}
    >
      {icon}
      {label}
    </button>
  );
}
