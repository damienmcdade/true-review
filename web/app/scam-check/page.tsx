import Link from 'next/link';
import { AlertTriangle, ShieldCheck, Search } from 'lucide-react';
import ScamCheckForm from '@/components/ScamCheckForm';

export const metadata = { title: 'Scam check — True Review' };

export default function ScamCheckPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <Search className="h-7 w-7 text-oceanDeep" />
          Scam check
        </h1>
        <p className="mt-3 text-sm text-ink/75">
          Enter a domain or URL. We cross-reference our internal scam reports with the live{' '}
          <a
            href="https://urlhaus.abuse.ch/"
            target="_blank"
            rel="noreferrer noopener"
            className="underline"
          >
            URLhaus
          </a>{' '}
          malicious-URL database (Cisco Talos / abuse.ch) and show the verdict with evidence.
        </p>
        <ScamCheckForm className="mt-6" />
      </div>

      <div className="mt-6 grid gap-3 md:grid-cols-2">
        <div className="glass rounded-2xl p-4 text-xs text-ink/70">
          <ShieldCheck className="mb-1 inline h-4 w-4 text-verified" /> A <strong>clean</strong>{' '}
          result means the domain isn&apos;t on either list right now. It is not a guarantee the
          site is safe — new scams appear constantly.
        </div>
        <div className="glass rounded-2xl p-4 text-xs text-ink/70">
          <AlertTriangle className="mb-1 inline h-4 w-4 text-scam" /> A <strong>flagged</strong>{' '}
          result is direct evidence from a reputable threat-intelligence feed or from verified
          scam reports on True Review. Treat as cautionary.
        </div>
      </div>
    </main>
  );
}
