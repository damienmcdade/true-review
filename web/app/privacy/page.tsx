import Link from 'next/link';

export default function PrivacyPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Privacy</h1>
        <div className="mt-4 space-y-4 text-ink/75">
          <p>
            True Review minimizes metadata. We never publish your employer, role, or any
            identifying detail unless you explicitly opt in.
          </p>
          <p>
            Employment proofs are encrypted at rest and only used to issue an anonymous
            verification badge.
          </p>
          <p>
            We use Google AdSense for free-tier monetization. AdSense may set cookies for ad
            personalization. See <a href="https://policies.google.com/technologies/ads" className="underline">Google&apos;s ad policy</a>.
          </p>
          <p className="text-sm text-ink/55">
            Full privacy policy will be published before public launch.
          </p>
        </div>
      </div>
    </main>
  );
}
