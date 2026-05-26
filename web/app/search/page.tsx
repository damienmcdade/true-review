import Link from 'next/link';

async function searchCompanies(query: string) {
  if (!query) return [];
  const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${api}/companies?q=${encodeURIComponent(query)}`, {
      next: { revalidate: 30 }
    });
    if (!res.ok) return [];
    return (await res.json()) as Array<{ id: string; name: string; slug: string; review_count: number }>;
  } catch {
    return [];
  }
}

export default async function SearchPage({
  searchParams
}: {
  searchParams: Promise<{ q?: string }>;
}) {
  const { q } = await searchParams;
  const results = await searchCompanies(q ?? '');

  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Search companies</h1>
        <form className="mt-6" action="/search">
          <input
            type="search"
            name="q"
            defaultValue={q ?? ''}
            placeholder="e.g. Acme Corp, Stripe, Anthropic"
            className="w-full rounded-full border border-white/60 bg-white/70 px-5 py-3 text-ink outline-none placeholder:text-ink/40 focus:border-ocean"
            autoFocus
          />
        </form>
      </div>

      <div className="mt-8 space-y-3">
        {q && results.length === 0 ? (
          <p className="text-sm text-ink/50">
            No matches yet. Once the API is live, verified company pages will load here.
          </p>
        ) : null}
        {results.map((c) => (
          <Link
            key={c.id}
            href={`/c/${c.slug}`}
            className="glass flex items-center justify-between rounded-xl px-5 py-4 hover:bg-white/70"
          >
            <span className="font-medium">{c.name}</span>
            <span className="text-xs text-ink/50">{c.review_count} verified reviews</span>
          </Link>
        ))}
      </div>
    </main>
  );
}
