import Link from 'next/link';

export const metadata = { title: 'Data request — True Review' };

export default function DataRequestPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8 text-sm text-ink/80">
        <h1 className="font-display text-3xl font-semibold tracking-tight">
          Data subject request
        </h1>
        <p className="mt-3">
          Under GDPR, UK GDPR, CCPA/CPRA, VCDPA, CPA, CTDPA, UCPA, and similar laws you can ask
          us to:
        </p>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Export the data we hold about you.</li>
          <li>Correct or delete your reviews.</li>
          <li>Opt out of advertising cookies (use the consent banner).</li>
          <li>Object to processing or withdraw consent.</li>
        </ul>
        <p className="mt-4">
          Email <span className="font-mono">info@cyberwaveglobal.com</span> with:
        </p>
        <ul className="mt-1 list-disc space-y-1 pl-5">
          <li>The request type.</li>
          <li>Enough detail for us to identify the relevant data (review URL, handle, or salted IP-hash reference).</li>
          <li>Verification: a brief statement that you are the data subject or their authorised agent.</li>
        </ul>
        <p className="mt-4">
          We respond within <strong>30 days</strong> (GDPR) or <strong>45 days</strong> (CCPA), free of charge for one request per year.
        </p>
      </div>
    </main>
  );
}
