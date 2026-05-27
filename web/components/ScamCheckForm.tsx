'use client';

import { useState, useTransition } from 'react';
import { AlertTriangle, ShieldCheck, Loader2, Search } from 'lucide-react';
import clsx from 'clsx';
import { apiFetch, type ApiError } from '@/lib/api';

type ScamResult = {
  domain: string;
  verdict: 'flagged' | 'pending_review' | 'no_signal';
  internal: {
    company: {
      name: string;
      slug: string;
      is_scam_flagged: boolean;
      scam_reports_count: number;
    } | null;
    report_count: number;
  };
  urlhaus: {
    checked: boolean;
    found?: boolean;
    threat_count?: number;
    first_seen?: string;
    listings?: Array<{ url: string; threat: string; tags: string[]; date_added: string }>;
    error?: string;
  };
};

export default function ScamCheckForm({ className }: { className?: string }) {
  const [domain, setDomain] = useState('');
  const [result, setResult] = useState<ScamResult | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [pending, startTransition] = useTransition();

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setResult(null);
    const cleaned = domain
      .trim()
      .toLowerCase()
      .replace(/^https?:\/\//, '')
      .split('/')[0];
    if (cleaned.length < 3 || !cleaned.includes('.')) {
      setError({ status: null, kind: 'client', message: 'Enter a valid domain like example.com' });
      return;
    }
    startTransition(async () => {
      const { data, error } = await apiFetch<ScamResult>(
        `/scam-check?domain=${encodeURIComponent(cleaned)}`
      );
      if (error) setError(error);
      if (data) setResult(data);
    });
  }

  return (
    <div className={className}>
      <form onSubmit={onSubmit} className="relative">
        <Search className="absolute left-4 top-1/2 h-4 w-4 -translate-y-1/2 text-ink/45" />
        <input
          type="text"
          value={domain}
          onChange={(e) => setDomain(e.target.value)}
          placeholder="example.com"
          autoCapitalize="off"
          autoCorrect="off"
          spellCheck={false}
          className="w-full rounded-full border border-white/60 bg-white/80 px-12 py-3.5 text-ink shadow-sm outline-none placeholder:text-ink/40 focus:border-ocean"
        />
        <button
          type="submit"
          disabled={pending || !domain.trim()}
          className="absolute right-1.5 top-1/2 inline-flex -translate-y-1/2 items-center gap-1.5 rounded-full bg-ocean px-4 py-2 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : 'Check'}
        </button>
      </form>

      {error ? (
        <div className="mt-5 rounded-2xl border border-danger/30 bg-danger/5 p-4 text-sm text-danger">
          {error.message}
        </div>
      ) : null}

      {result ? <Result r={result} /> : null}
    </div>
  );
}

function Result({ r }: { r: ScamResult }) {
  const verdict = r.verdict;
  const flagged = verdict === 'flagged';
  const pending = verdict === 'pending_review';

  return (
    <div className="mt-6 space-y-4">
      <div
        className={clsx(
          'rounded-2xl border-l-4 p-5',
          flagged
            ? 'border-scam/70 bg-scam/10 text-scam'
            : pending
              ? 'border-warn/70 bg-warn/10 text-warn'
              : 'border-verified/70 bg-verified/10 text-verified'
        )}
      >
        <div className="flex items-center gap-2 text-sm font-semibold uppercase tracking-wider">
          {flagged ? <AlertTriangle className="h-5 w-5" /> : <ShieldCheck className="h-5 w-5" />}
          {flagged ? 'Flagged' : pending ? 'Pending review' : 'No signal'}
        </div>
        <p className="mt-2 text-base font-medium text-ink">{r.domain}</p>
        <p className="mt-1 text-sm text-ink/75">
          {flagged
            ? 'This domain has live evidence of malicious activity or verified scam reports. Treat with caution.'
            : pending
              ? `${r.internal.report_count} scam report(s) on file. Below the 3-source threshold for an auto-flag — treat as a single user claim, not a verdict.`
              : 'No scam signal found on either source right now. A clean check is not a guarantee — new scams appear constantly.'}
        </p>
      </div>

      <div className="grid gap-3 md:grid-cols-2">
        <div className="glass rounded-2xl p-4 text-sm">
          <div className="font-semibold text-ink">True Review internal</div>
          {r.internal.company ? (
            <>
              <p className="mt-1 text-ink/75">
                Matched company: <strong>{r.internal.company.name}</strong>
              </p>
              <p className="text-ink/60">
                {r.internal.report_count} scam report{r.internal.report_count === 1 ? '' : 's'} ·{' '}
                {r.internal.company.is_scam_flagged ? 'flagged' : 'not flagged'}
              </p>
            </>
          ) : (
            <p className="mt-1 text-ink/60">No matching company in our database.</p>
          )}
        </div>

        <div className="glass rounded-2xl p-4 text-sm">
          <div className="font-semibold text-ink">URLhaus (abuse.ch / Cisco Talos)</div>
          {!r.urlhaus.checked ? (
            <p className="mt-1 text-ink/60">
              {r.urlhaus.error || 'Not configured. Set URLHAUS_AUTH_KEY on the API.'}
            </p>
          ) : r.urlhaus.found ? (
            <>
              <p className="mt-1 text-scam">
                Listed — {r.urlhaus.threat_count} malicious URL
                {(r.urlhaus.threat_count ?? 1) === 1 ? '' : 's'} on file.
              </p>
              {r.urlhaus.first_seen ? (
                <p className="text-xs text-ink/55">First seen {r.urlhaus.first_seen}</p>
              ) : null}
              {r.urlhaus.listings?.length ? (
                <ul className="mt-2 space-y-1 text-xs text-ink/70">
                  {r.urlhaus.listings.slice(0, 3).map((l) => (
                    <li key={l.url}>
                      <span className="font-mono break-all">{l.url}</span>
                      <span className="ml-1 text-ink/45">({l.threat})</span>
                    </li>
                  ))}
                </ul>
              ) : null}
            </>
          ) : (
            <p className="mt-1 text-verified">Not on the live malicious-URL feed.</p>
          )}
        </div>
      </div>
    </div>
  );
}
