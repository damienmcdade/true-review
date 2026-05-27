'use client';

import { useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { Sparkles, Search, AlertTriangle, Loader2 } from 'lucide-react';
import clsx from 'clsx';

type SearchResult = {
  query: string;
  companies: Array<{
    id: string;
    name: string;
    slug: string;
    kind: string;
    is_scam_flagged: boolean;
    scam_reports_count: number;
    review_count: number;
  }>;
  summary: { answer: string; citations: number[]; source: string; model: string };
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export default function AiSearch({ className }: { className?: string }) {
  const router = useRouter();
  const [query, setQuery] = useState('');
  const [result, setResult] = useState<SearchResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    const q = query.trim();
    if (!q) return;
    setError(null);
    setResult(null);
    startTransition(async () => {
      try {
        const res = await fetch(`${API}/ai/search?q=${encodeURIComponent(q)}`, {
          cache: 'no-store'
        });
        if (!res.ok) {
          setError(`API error ${res.status}`);
          return;
        }
        setResult((await res.json()) as SearchResult);
      } catch (e) {
        setError('Could not reach the API.');
      }
    });
  }

  return (
    <div className={className}>
      <form onSubmit={onSubmit} className="relative">
        <Sparkles className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-coral" />
        <input
          type="search"
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Try “Is Patagonia a fair employer?” or “Reports of fraud at quickrich-invest-xyz”"
          className="w-full rounded-full border border-white/60 bg-white/80 px-12 py-3.5 text-ink shadow-sm outline-none placeholder:text-ink/40 focus:border-ocean"
          autoFocus
        />
        <button
          type="submit"
          disabled={pending || !query.trim()}
          className="absolute right-1.5 top-1/2 inline-flex -translate-y-1/2 items-center gap-1.5 rounded-full bg-ocean px-4 py-2 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Search className="h-4 w-4" />}
          Ask
        </button>
      </form>

      <div className="mt-3 flex flex-wrap gap-2 text-xs text-ink/60">
        <SuggestionChip onPick={setQuery}>Is Stripe a good place to work?</SuggestionChip>
        <SuggestionChip onPick={setQuery}>Patagonia warranty experience</SuggestionChip>
        <SuggestionChip onPick={setQuery}>Reports of phishing at primedealsdirect-xy</SuggestionChip>
      </div>

      {error ? (
        <div className="mt-5 rounded-2xl border border-danger/30 bg-danger/5 p-4 text-sm text-danger">
          {error}
        </div>
      ) : null}

      {result ? (
        <div className="mt-6 space-y-4">
          <div className="glass rounded-2xl p-5">
            <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-oceanDeep">
              <Sparkles className="h-3.5 w-3.5" />
              AI copilot ·{' '}
              <span className="font-mono text-[10px] text-ink/45">{result.summary.model}</span>
            </div>
            <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-ink/85">
              {result.summary.answer}
            </p>
          </div>

          {result.companies.length > 0 ? (
            <div className="space-y-2">
              {result.companies.map((c) => (
                <Link
                  key={c.id}
                  href={`/c/${c.slug}` as never}
                  className={clsx(
                    'glass flex items-center justify-between rounded-xl px-5 py-3 transition hover:bg-white/85',
                    c.is_scam_flagged && 'border-scam/40 bg-scam/10'
                  )}
                >
                  <div className="flex items-center gap-3">
                    {c.is_scam_flagged ? (
                      <AlertTriangle className="h-4 w-4 text-scam" />
                    ) : (
                      <span className="h-2 w-2 rounded-full bg-verified" />
                    )}
                    <div>
                      <div className="font-medium text-ink">{c.name}</div>
                      <div className="text-xs text-ink/55">
                        {c.review_count} reviews · {c.kind}
                        {c.is_scam_flagged
                          ? ` · ${c.scam_reports_count} scam report${c.scam_reports_count === 1 ? '' : 's'}`
                          : ''}
                      </div>
                    </div>
                  </div>
                  <span className="text-xs text-ink/50">view →</span>
                </Link>
              ))}
            </div>
          ) : (
            <p className="text-sm text-ink/55">
              No companies matched. Try a different query, or{' '}
              <Link href="/search" className="underline">
                browse the catalog
              </Link>
              .
            </p>
          )}
        </div>
      ) : null}
    </div>
  );
}

function SuggestionChip({
  children,
  onPick
}: {
  children: string;
  onPick: (s: string) => void;
}) {
  return (
    <button
      type="button"
      onClick={() => onPick(children)}
      className="rounded-full border border-white/60 bg-white/40 px-3 py-1 hover:bg-white/70"
    >
      {children}
    </button>
  );
}
