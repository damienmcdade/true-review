import Link from 'next/link';

export default function TransparencyPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Transparency</h1>
        <p className="mt-4 text-ink/75">
          Every moderation decision on True Review is logged here. No silent removals. No
          employer suppression. If your content was edited or removed, the reason is public.
        </p>
      </div>
      <div className="mt-6">
        <div className="glass rounded-xl p-5 text-sm text-ink/60">
          The moderation log will populate when the platform opens to verified reviewers.
        </div>
      </div>
    </main>
  );
}
