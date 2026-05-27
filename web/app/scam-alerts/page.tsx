import Link from 'next/link';
import { AlertTriangle, ShieldOff } from 'lucide-react';

type Alert = {
  id: string;
  name: string;
  slug: string;
  scam_reports_count: number;
  scam_severity: number;
  last_scam_report_at: string | null;
  top_categories: string[];
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getAlerts(): Promise<Alert[]> {
  try {
    const res = await fetch(`${API}/scam-alerts?limit=50`, { next: { revalidate: 30 } });
    if (!res.ok) return [];
    return (await res.json()) as Alert[];
  } catch {
    return [];
  }
}

const CATEGORY_LABEL: Record<string, string> = {
  fake_product: 'Fake product',
  non_delivery: 'Non-delivery',
  phishing: 'Phishing',
  fake_job: 'Fake job listing',
  fake_invoice: 'Fake invoice',
  subscription_trap: 'Subscription trap',
  counterfeit: 'Counterfeit',
  other: 'Other'
};

export default async function ScamAlertsPage() {
  const alerts = await getAlerts();

  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>

      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <AlertTriangle className="h-7 w-7 text-scam" />
          Scam alerts
        </h1>
        <p className="mt-3 text-ink/75">
          Companies the community has flagged with multiple verified scam reports. Severity is a
          rolling score based on report count, recency, and money lost. Treat these as cautionary —
          but verify with your own due diligence before any action.
        </p>
      </div>

      <div className="mt-6 space-y-3">
        {alerts.length === 0 ? (
          <div className="glass rounded-xl p-6 text-center text-sm text-ink/55">
            <ShieldOff className="mx-auto mb-2 h-6 w-6 text-ink/40" />
            No active flags right now.
          </div>
        ) : (
          alerts.map((a) => (
            <Link
              key={a.id}
              href={`/c/${a.slug}` as never}
              className="glass block rounded-2xl border-l-4 border-scam/70 px-5 py-4 transition hover:bg-white/80"
            >
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="font-semibold text-ink">{a.name}</div>
                  <div className="mt-1 text-xs text-ink/60">
                    {a.scam_reports_count} report{a.scam_reports_count === 1 ? '' : 's'}
                    {a.last_scam_report_at
                      ? ` · last ${new Date(a.last_scam_report_at).toLocaleDateString()}`
                      : ''}
                  </div>
                  {a.top_categories.length > 0 ? (
                    <div className="mt-2 flex flex-wrap gap-1.5">
                      {a.top_categories.map((c) => (
                        <span
                          key={c}
                          className="rounded-full bg-scam/15 px-2 py-0.5 text-[11px] font-medium text-scam"
                        >
                          {CATEGORY_LABEL[c] ?? c}
                        </span>
                      ))}
                    </div>
                  ) : null}
                </div>
                <SeverityBadge value={a.scam_severity} />
              </div>
            </Link>
          ))
        )}
      </div>

      <div className="mt-10 glass rounded-2xl p-5 text-sm text-ink/70">
        <p className="font-medium text-ink">Reporting a scam</p>
        <p className="mt-1">
          Anyone affected can file a scam report on a company&apos;s page. Reports must include
          evidence (order ID, charge amount, dates, screenshots described). False reports erode
          your trust score; verified reports raise it.
        </p>
      </div>
    </main>
  );
}

function SeverityBadge({ value }: { value: number }) {
  const pct = Math.round(value * 100);
  const level = value >= 0.75 ? 'Critical' : value >= 0.5 ? 'High' : value >= 0.25 ? 'Moderate' : 'Low';
  return (
    <div className="text-right">
      <div className="text-2xl font-semibold text-scam">{pct}%</div>
      <div className="text-[10px] uppercase tracking-wider text-ink/45">{level}</div>
    </div>
  );
}
