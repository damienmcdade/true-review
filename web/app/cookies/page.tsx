import Link from 'next/link';

export const metadata = { title: 'Cookies — True Review' };

export default function CookiesPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <article className="glass mt-6 rounded-3xl p-8 text-sm text-ink/80">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Cookies</h1>
        <p className="mt-3">
          We use the minimum cookies needed to run the site, plus optional advertising cookies
          you can decline.
        </p>
        <h2 className="mt-5 text-base font-semibold text-ink">Essential</h2>
        <ul className="mt-1 list-disc space-y-1 pl-5">
          <li><code className="font-mono">tr-cookie-consent-v1</code> — stores your cookie choice. localStorage, no expiry.</li>
        </ul>
        <h2 className="mt-5 text-base font-semibold text-ink">Advertising (optional, requires consent)</h2>
        <ul className="mt-1 list-disc space-y-1 pl-5">
          <li>Google AdSense — sets identifiers for ad measurement and personalisation.</li>
        </ul>
        <p className="mt-5">
          You can change your choice any time by clearing site data in your browser, or by using
          the consent banner that re-appears on first visit.
        </p>
      </article>
    </main>
  );
}
