import Link from 'next/link';

export default function TermsPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Terms</h1>
        <div className="mt-4 space-y-4 text-ink/75">
          <p>
            True Review hosts opinions of verified employees. Reviews must be truthful,
            first-hand, and free of personally identifying claims about individuals.
          </p>
          <p>
            We do not remove negative reviews on request. We do correct factual errors with
            a public log entry on the transparency page.
          </p>
          <p className="text-sm text-ink/55">
            Full terms will be published before public launch.
          </p>
        </div>
      </div>
    </main>
  );
}
