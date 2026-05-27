'use client';

import { useEffect, useState, useTransition } from 'react';
import { useRouter } from 'next/navigation';
import { Loader2, Plus, BookOpen, Building } from 'lucide-react';
import { apiFetch, type ApiError } from '@/lib/api';

type ExternalHit = {
  source: 'wikipedia' | 'opencorporates';
  name: string;
  proposed_slug: string;
  description?: string;
  url?: string;
  jurisdiction?: string;
  registration_number?: string;
  status?: string;
  exists: boolean;
};

type DiscoverResponse = {
  query: string;
  internal: unknown[];
  external: ExternalHit[];
};

export default function DiscoverExternal({
  query,
  className
}: {
  query: string;
  className?: string;
}) {
  const router = useRouter();
  const [data, setData] = useState<DiscoverResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [creating, setCreating] = useState<string | null>(null);
  const [pending, startTransition] = useTransition();

  useEffect(() => {
    let cancelled = false;
    setError(null);
    setData(null);
    startTransition(async () => {
      const { data, error } = await apiFetch<DiscoverResponse>(
        `/companies/discover?q=${encodeURIComponent(query)}`,
        { timeoutMs: 20_000 }
      );
      if (cancelled) return;
      if (error) setError(error);
      if (data) setData(data);
    });
    return () => {
      cancelled = true;
    };
  }, [query]);

  async function claim(hit: ExternalHit) {
    setCreating(hit.proposed_slug);
    const { data, error } = await apiFetch<{ slug: string }>('/companies', {
      method: 'POST',
      body: JSON.stringify({
        name: hit.name,
        slug: hit.proposed_slug,
        kind: hit.source === 'opencorporates' ? 'both' : 'both',
        description: hit.description ?? null
      })
    });
    setCreating(null);
    if (error) {
      setError(error);
      return;
    }
    if (data) router.push(`/c/${data.slug}` as never);
  }

  if (pending) {
    return (
      <div className={(className ?? '') + ' flex items-center gap-2 text-sm text-ink/60'}>
        <Loader2 className="h-4 w-4 animate-spin" />
        Looking up &ldquo;{query}&rdquo;…
      </div>
    );
  }

  if (error) {
    return (
      <div className={(className ?? '') + ' rounded-2xl border border-warn/30 bg-warn/5 p-3 text-xs text-warn'}>
        Discovery is briefly unavailable: {error.message}
      </div>
    );
  }

  if (!data || data.external.length === 0) {
    return (
      <div className={(className ?? '') + ' rounded-2xl border border-white/40 bg-white/40 p-4 text-xs text-ink/60'}>
        No external matches for &ldquo;{query}&rdquo;. You can still{' '}
        <a href="/review/new" className="underline">
          create a page and submit a review
        </a>{' '}
        — companies are auto-created on first review.
      </div>
    );
  }

  return (
    <div className={(className ?? '') + ' space-y-2'}>
      {data.external.map((hit) => (
        <div
          key={`${hit.source}-${hit.proposed_slug}`}
          className="glass flex flex-col gap-2 rounded-xl px-4 py-3 sm:flex-row sm:items-center sm:justify-between"
        >
          <div className="flex items-start gap-2 text-sm">
            {hit.source === 'wikipedia' ? (
              <BookOpen className="mt-0.5 h-4 w-4 shrink-0 text-oceanDeep" />
            ) : (
              <Building className="mt-0.5 h-4 w-4 shrink-0 text-oceanDeep" />
            )}
            <div>
              <div className="font-medium text-ink">{hit.name}</div>
              <div className="text-[11px] text-ink/55">
                {hit.source === 'wikipedia'
                  ? hit.description
                  : [hit.jurisdiction, hit.registration_number, hit.status]
                      .filter(Boolean)
                      .join(' · ')}
              </div>
              <div className="mt-1 text-[10px] uppercase tracking-wider text-ink/40">
                {hit.source === 'wikipedia' ? 'Wikipedia' : 'OpenCorporates'}
                {hit.url ? (
                  <>
                    {' · '}
                    <a
                      href={hit.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="underline"
                    >
                      source
                    </a>
                  </>
                ) : null}
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={() => claim(hit)}
            disabled={creating === hit.proposed_slug}
            className="inline-flex items-center gap-1.5 self-end rounded-full bg-ocean px-3 py-1.5 text-xs font-medium text-white hover:bg-oceanDeep disabled:opacity-50 sm:self-auto"
          >
            {creating === hit.proposed_slug ? (
              <Loader2 className="h-3.5 w-3.5 animate-spin" />
            ) : (
              <Plus className="h-3.5 w-3.5" />
            )}
            Add this company
          </button>
        </div>
      ))}
    </div>
  );
}
