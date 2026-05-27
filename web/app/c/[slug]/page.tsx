import Link from 'next/link';
import { AlertTriangle, Briefcase, ShoppingBag, Sparkles, Star, BookOpen, FileText, Building } from 'lucide-react';
import AdSlot from '@/components/AdSlot';
import ReviewVerifiedBadge from '@/components/ReviewVerifiedBadge';

type Company = {
  id: string;
  name: string;
  slug: string;
  kind: 'employer' | 'merchant' | 'both';
  trust_score: number;
  review_count: number;
  employment_review_count: number;
  shopping_review_count: number;
  scam_report_count: number;
  is_scam_flagged: boolean;
  scam_severity: number;
  health: { sentiment: number; layoff_risk: number; leadership_confidence: number };
  ai_summary?: string;
  description?: string;
  domain?: string;
};

type ReviewItem = {
  id: string;
  review_type: 'employment' | 'shopping' | 'scam_report';
  title: string;
  body: string;
  rating_overall: number;
  department?: string;
  product_or_service?: string;
  scam_category?: string;
  money_lost?: number;
  created_at: string;
  author_handle?: string;
  author_verification_tier?: string | null;
  verification_source?: string | null;
  verification_explainer?: string | null;
  is_demo?: boolean;
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getCompany(slug: string): Promise<Company | null> {
  try {
    const res = await fetch(`${API}/companies/${slug}`, { next: { revalidate: 30 } });
    if (!res.ok) return null;
    return (await res.json()) as Company;
  } catch {
    return null;
  }
}

async function getWikipedia(name: string) {
  try {
    const res = await fetch(`${API}/enrichment/wikipedia?name=${encodeURIComponent(name)}`, {
      next: { revalidate: 3600 }
    });
    if (!res.ok) return null;
    return (await res.json()) as { found: boolean; extract?: string; url?: string; thumbnail?: string };
  } catch {
    return null;
  }
}

async function getEdgar(name: string) {
  try {
    const res = await fetch(`${API}/enrichment/edgar?name=${encodeURIComponent(name)}`, {
      next: { revalidate: 3600 }
    });
    if (!res.ok) return null;
    return (await res.json()) as {
      found: boolean;
      ticker?: string;
      title?: string;
      sic?: string;
      recent_filings?: Array<{ form: string; date: string; url: string }>;
    };
  } catch {
    return null;
  }
}

async function getUrlhaus(domain?: string) {
  if (!domain) return null;
  try {
    const res = await fetch(`${API}/enrichment/urlhaus?domain=${encodeURIComponent(domain)}`, {
      next: { revalidate: 600 }
    });
    if (!res.ok) return null;
    return (await res.json()) as { checked: boolean; found?: boolean; threat_count?: number };
  } catch {
    return null;
  }
}

async function getReviews(slug: string, reviewType?: string): Promise<ReviewItem[]> {
  const params = new URLSearchParams();
  if (reviewType) params.set('review_type', reviewType);
  params.set('limit', '40');
  try {
    const res = await fetch(`${API}/companies/${slug}/reviews?${params}`, {
      next: { revalidate: 30 }
    });
    if (!res.ok) return [];
    return (await res.json()) as ReviewItem[];
  } catch {
    return [];
  }
}

const TAB_LABEL: Record<string, string> = {
  all: 'All',
  employment: 'Employment',
  shopping: 'Shopping',
  scam_report: 'Scam reports'
};

export default async function CompanyPage({
  params,
  searchParams
}: {
  params: Promise<{ slug: string }>;
  searchParams: Promise<{ tab?: string }>;
}) {
  const { slug } = await params;
  const { tab } = await searchParams;
  const activeTab = tab && ['employment', 'shopping', 'scam_report'].includes(tab) ? tab : 'all';

  const company = await getCompany(slug);
  const [reviews, wiki, edgar, urlhaus] = await Promise.all([
    getReviews(slug, activeTab === 'all' ? undefined : activeTab),
    company ? getWikipedia(company.name) : Promise.resolve(null),
    company ? getEdgar(company.name) : Promise.resolve(null),
    company?.domain ? getUrlhaus(company.domain) : Promise.resolve(null)
  ]);

  if (!company) {
    return (
      <main className="mx-auto max-w-3xl px-6 py-10">
        <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
          ← True Review
        </Link>
        <div className="glass mt-6 rounded-3xl p-8">
          <h1 className="font-display text-3xl font-semibold tracking-tight">{slug}</h1>
          <p className="mt-4 text-ink/70">
            No data for this company yet. Want to be the first?{' '}
            <Link href="/review/new" className="underline">
              Submit a verified review
            </Link>
            .
          </p>
        </div>
      </main>
    );
  }

  return (
    <main className="mx-auto max-w-4xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>

      <header className="glass mt-6 rounded-3xl p-8">
        <div className="flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="font-display text-4xl font-semibold tracking-tight">{company.name}</h1>
            {company.description ? (
              <p className="mt-2 max-w-xl text-sm text-ink/70">{company.description}</p>
            ) : null}
            <div className="mt-3 flex flex-wrap items-center gap-2 text-xs text-ink/55">
              {company.domain ? <span>{company.domain}</span> : null}
              {company.domain ? <span>·</span> : null}
              <span>{company.review_count} verified reviews</span>
              <span>·</span>
              <span>trust {company.trust_score.toFixed(2)}</span>
            </div>
          </div>
          <Link
            href={`/c/${company.slug}/ask` as never}
            className="inline-flex items-center gap-2 rounded-full bg-ocean px-4 py-2 text-sm font-medium text-white hover:bg-oceanDeep"
          >
            <Sparkles className="h-4 w-4" />
            Ask the AI copilot
          </Link>
        </div>

        {company.is_scam_flagged ? (
          <div className="mt-5 flex items-start gap-3 rounded-2xl border border-scam/40 bg-scam/10 p-4">
            <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-scam" />
            <div className="text-sm">
              <div className="font-semibold text-scam">Scam alert</div>
              <div className="text-ink/75">
                {company.scam_report_count} report{company.scam_report_count === 1 ? '' : 's'}{' '}
                logged. Severity {Math.round(company.scam_severity * 100)}%. Verify carefully
                before sharing money or personal info.
              </div>
            </div>
          </div>
        ) : null}
      </header>

      {urlhaus?.checked && urlhaus?.found ? (
        <div className="mt-4 flex items-start gap-3 rounded-2xl border border-scam/40 bg-scam/10 p-4 text-sm">
          <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-scam" />
          <div>
            <div className="font-semibold text-scam">URLhaus listing</div>
            <div className="text-ink/75">
              {company.domain} is on the live URLhaus malicious-URL feed
              {urlhaus.threat_count ? ` with ${urlhaus.threat_count} threat URL(s)` : ''}.
              Source: abuse.ch / Cisco Talos.
            </div>
          </div>
        </div>
      ) : null}

      {wiki?.found && wiki.extract ? (
        <section className="glass mt-6 rounded-2xl p-5">
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-oceanDeep">
            <BookOpen className="h-3.5 w-3.5" />
            Wikipedia
          </div>
          <p className="mt-2 text-sm leading-relaxed text-ink/80">{wiki.extract}</p>
          {wiki.url ? (
            <a
              href={wiki.url}
              target="_blank"
              rel="noopener noreferrer"
              className="mt-2 inline-block text-xs text-oceanDeep underline"
            >
              Read full article →
            </a>
          ) : null}
        </section>
      ) : null}

      {edgar?.found && edgar.recent_filings && edgar.recent_filings.length > 0 ? (
        <section className="glass mt-4 rounded-2xl p-5">
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-oceanDeep">
            <FileText className="h-3.5 w-3.5" />
            SEC EDGAR — recent filings
          </div>
          {edgar.ticker ? (
            <p className="mt-1 text-xs text-ink/55">
              {edgar.title} · {edgar.ticker} · {edgar.sic ?? ''}
            </p>
          ) : null}
          <ul className="mt-2 space-y-1 text-sm">
            {edgar.recent_filings.slice(0, 5).map((f) => (
              <li key={f.url} className="flex justify-between gap-2 text-ink/75">
                <a
                  href={f.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="font-mono text-xs underline"
                >
                  {f.form}
                </a>
                <span className="text-xs text-ink/45">{f.date}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}

      <section className="mt-6 grid gap-4 sm:grid-cols-3">
        <Stat icon={<Briefcase className="h-4 w-4 text-ocean" />} label="Employment reviews" value={company.employment_review_count} />
        <Stat icon={<ShoppingBag className="h-4 w-4 text-coral" />} label="Shopping reviews" value={company.shopping_review_count} />
        <Stat icon={<AlertTriangle className="h-4 w-4 text-scam" />} label="Scam reports" value={company.scam_report_count} highlight={company.scam_report_count > 0} />
      </section>

      <nav className="mt-8 flex flex-wrap gap-2 text-sm">
        {(['all', 'employment', 'shopping', 'scam_report'] as const).map((t) => (
          <Link
            key={t}
            href={t === 'all' ? `/c/${company.slug}` as never : `/c/${company.slug}?tab=${t}` as never}
            className={
              'rounded-full px-4 py-1.5 ' +
              (activeTab === t
                ? 'bg-oceanDeep text-white'
                : 'bg-white/60 text-ink/75 hover:bg-white')
            }
          >
            {TAB_LABEL[t]}
          </Link>
        ))}
      </nav>

      <section className="mt-5 space-y-4">
        {reviews.length === 0 ? (
          <div className="glass rounded-xl p-6 text-center text-sm text-ink/55">
            No reviews of this type yet.
          </div>
        ) : (
          reviews.map((r) => <ReviewCard key={r.id} r={r} />)
        )}
      </section>

      <AdSlot slot="company-mid" className="mt-12" />
    </main>
  );
}

function Stat({
  icon,
  label,
  value,
  highlight
}: {
  icon: React.ReactNode;
  label: string;
  value: number;
  highlight?: boolean;
}) {
  return (
    <div className={'glass rounded-2xl p-5 ' + (highlight ? 'border-scam/40' : '')}>
      <div className="flex items-center gap-2 text-xs uppercase tracking-wider text-ink/55">
        {icon}
        {label}
      </div>
      <div className={'mt-2 text-3xl font-semibold ' + (highlight ? 'text-scam' : 'text-ink')}>
        {value}
      </div>
    </div>
  );
}

function ReviewCard({ r }: { r: ReviewItem }) {
  const isScam = r.review_type === 'scam_report';
  return (
    <article
      className={
        'glass rounded-2xl p-5 ' +
        (isScam ? 'border-l-4 border-scam/70' : '')
      }
    >
      <div className="flex flex-wrap items-center justify-between gap-2">
        <div className="flex items-center gap-2 text-xs uppercase tracking-wider">
          <TypeBadge type={r.review_type} />
          {r.department ? <span className="text-ink/55">{r.department}</span> : null}
          {r.product_or_service ? (
            <span className="text-ink/55">{r.product_or_service}</span>
          ) : null}
          {r.scam_category ? (
            <span className="rounded-full bg-scam/15 px-2 py-0.5 text-[10px] font-medium text-scam">
              {r.scam_category.replaceAll('_', ' ')}
            </span>
          ) : null}
        </div>
        <Rating value={r.rating_overall} />
      </div>
      <h3 className="mt-2 font-semibold text-ink">{r.title}</h3>
      <p className="mt-1 whitespace-pre-wrap text-sm leading-relaxed text-ink/80">{r.body}</p>
      <div className="mt-3 flex flex-wrap items-center justify-between gap-2 text-[11px] text-ink/45">
        <ReviewVerifiedBadge
          source={r.verification_source}
          explainer={r.verification_explainer}
          isDemo={Boolean(r.is_demo)}
        />
        <span>
          {r.author_handle ?? 'anonymous'} · {new Date(r.created_at).toLocaleDateString()}
        </span>
      </div>
    </article>
  );
}

function TypeBadge({ type }: { type: ReviewItem['review_type'] }) {
  const map = {
    employment: { label: 'Employment', cls: 'bg-ocean/15 text-oceanDeep' },
    shopping: { label: 'Shopping', cls: 'bg-coral/15 text-coral' },
    scam_report: { label: 'Scam report', cls: 'bg-scam/15 text-scam' }
  } as const;
  const { label, cls } = map[type];
  return (
    <span className={'rounded-full px-2 py-0.5 text-[10px] font-medium ' + cls}>{label}</span>
  );
}

function Rating({ value }: { value: number }) {
  return (
    <div className="flex items-center gap-1 text-sunset">
      {[1, 2, 3, 4, 5].map((i) => (
        <Star
          key={i}
          className={
            'h-3.5 w-3.5 ' +
            (i <= Math.round(value) ? 'fill-sunset' : 'opacity-30')
          }
        />
      ))}
      <span className="ml-1 text-xs text-ink/55">{value.toFixed(1)}</span>
    </div>
  );
}
