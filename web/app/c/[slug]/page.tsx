import Link from 'next/link';
import AdSlot from '@/components/AdSlot';

type Company = {
  id: string;
  name: string;
  slug: string;
  trust_score: number;
  review_count: number;
  health: { sentiment: number; layoff_risk: number; leadership_confidence: number };
  ai_summary?: string;
};

async function getCompany(slug: string): Promise<Company | null> {
  const api = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
  try {
    const res = await fetch(`${api}/companies/${slug}`, { next: { revalidate: 60 } });
    if (!res.ok) return null;
    return (await res.json()) as Company;
  } catch {
    return null;
  }
}

export default async function CompanyPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const company = await getCompany(slug);
  if (!company) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-12">
        <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
          ← True Review
        </Link>
        <div className="glass mt-6 rounded-3xl p-8">
          <h1 className="font-display text-3xl font-semibold tracking-tight">{slug}</h1>
          <p className="mt-4 text-ink/65">
            No data yet. Once the API is deployed and verified reviews exist, this company&apos;s
            health dashboard will appear here.
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-12">
      <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
        ← True Review
      </Link>
      <header className="glass mt-6 flex items-end justify-between rounded-3xl p-8">
        <div>
          <h1 className="font-display text-4xl font-semibold tracking-tight">{company.name}</h1>
          <p className="mt-2 text-sm text-ink/55">
            {company.review_count} verified reviews · trust score {company.trust_score.toFixed(2)}
          </p>
        </div>
        <Link
          href={`/c/${company.slug}/ask`}
          className="rounded-full bg-ocean px-4 py-2 text-sm text-white hover:bg-oceanDeep"
        >
          Ask the AI copilot →
        </Link>
      </header>

      {company.ai_summary ? (
        <section className="glass mt-8 rounded-2xl p-6">
          <h2 className="text-xs font-medium uppercase tracking-wider text-ink/40">AI summary</h2>
          <p className="mt-3 leading-relaxed text-ink/85">{company.ai_summary}</p>
        </section>
      ) : null}

      <section className="mt-8 grid gap-4 md:grid-cols-3">
        <HealthCard label="Sentiment" value={company.health.sentiment} />
        <HealthCard label="Layoff risk" value={company.health.layoff_risk} inverted />
        <HealthCard label="Leadership confidence" value={company.health.leadership_confidence} />
      </section>

      <AdSlot slot="company-mid" className="mt-12" />
    </main>
  );
}

function HealthCard({
  label,
  value,
  inverted = false
}: {
  label: string;
  value: number;
  inverted?: boolean;
}) {
  const pct = Math.round(value * 100);
  const good = inverted ? value < 0.4 : value > 0.6;
  const color = good ? 'text-verified' : value > 0.5 ? 'text-warn' : 'text-danger';
  return (
    <div className="glass rounded-xl p-5">
      <div className="text-xs uppercase tracking-wider text-ink/40">{label}</div>
      <div className={`mt-2 text-3xl font-semibold ${color}`}>{pct}%</div>
    </div>
  );
}
