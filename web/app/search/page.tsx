import Link from 'next/link';
import { AlertTriangle, Briefcase, ShoppingBag, Building2 } from 'lucide-react';

type Result = {
  id: string;
  name: string;
  slug: string;
  kind: 'employer' | 'merchant' | 'both';
  review_count: number;
  is_scam_flagged: boolean;
  scam_reports_count: number;
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function searchCompanies(query: string, kind?: string): Promise<Result[]> {
  const params = new URLSearchParams();
  if (query) params.set('q', query);
  if (kind && kind !== 'all') params.set('kind', kind);
  params.set('limit', '50');
  try {
    const res = await fetch(`${API}/companies?${params}`, { next: { revalidate: 20 } });
    if (!res.ok) return [];
    return (await res.json()) as Result[];
  } catch {
    return [];
  }
}

const KIND_ICON = {
  employer: <Briefcase className="h-4 w-4 text-ocean" />,
  merchant: <ShoppingBag className="h-4 w-4 text-coral" />,
  both: <Building2 className="h-4 w-4 text-oceanDeep" />
};

export default async function SearchPage({
  searchParams
}: {
  searchParams: Promise<{ q?: string; kind?: string }>;
}) {
  const { q, kind } = await searchParams;
  const results = await searchCompanies(q ?? '', kind);

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>

      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Browse companies</h1>
        <form className="mt-6" action="/search">
          <input
            type="search"
            name="q"
            defaultValue={q ?? ''}
            placeholder="Search by company name or domain"
            className="w-full rounded-full border border-white/60 bg-white/80 px-5 py-3 text-ink outline-none placeholder:text-ink/40 focus:border-ocean"
            autoFocus
          />
          <div className="mt-4 flex flex-wrap gap-2 text-xs">
            <KindFilter active={kind} value="all" query={q}>All</KindFilter>
            <KindFilter active={kind} value="employer" query={q}>Employers</KindFilter>
            <KindFilter active={kind} value="merchant" query={q}>Merchants</KindFilter>
            <KindFilter active={kind} value="both" query={q}>Both</KindFilter>
          </div>
        </form>
      </div>

      <div className="mt-6 space-y-2">
        {results.length === 0 ? (
          <p className="text-sm text-ink/55">
            No matches. Try a different query, or{' '}
            <Link href="/review/new" className="underline">
              submit the first review
            </Link>
            .
          </p>
        ) : (
          results.map((c) => (
            <Link
              key={c.id}
              href={`/c/${c.slug}` as never}
              className="glass flex items-center justify-between rounded-xl px-5 py-4 transition hover:bg-white/85"
            >
              <div className="flex items-center gap-3">
                {KIND_ICON[c.kind] ?? KIND_ICON.both}
                <div>
                  <div className="font-medium text-ink">{c.name}</div>
                  <div className="text-xs text-ink/55">
                    {c.review_count} verified review{c.review_count === 1 ? '' : 's'}
                  </div>
                </div>
              </div>
              {c.is_scam_flagged ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-scam/15 px-2 py-1 text-[11px] font-medium text-scam">
                  <AlertTriangle className="h-3 w-3" />
                  {c.scam_reports_count} flag{c.scam_reports_count === 1 ? '' : 's'}
                </span>
              ) : (
                <span className="text-xs text-ink/40">view →</span>
              )}
            </Link>
          ))
        )}
      </div>
    </main>
  );
}

function KindFilter({
  active,
  value,
  query,
  children
}: {
  active?: string;
  value: string;
  query?: string;
  children: React.ReactNode;
}) {
  const params = new URLSearchParams();
  if (query) params.set('q', query);
  if (value !== 'all') params.set('kind', value);
  const href = `/search${params.toString() ? `?${params}` : ''}` as const;
  const selected = (active || 'all') === value;
  return (
    <Link
      href={href as never}
      className={
        'rounded-full px-3 py-1.5 ' +
        (selected
          ? 'bg-oceanDeep text-white'
          : 'bg-white/60 text-ink/75 hover:bg-white')
      }
    >
      {children}
    </Link>
  );
}
