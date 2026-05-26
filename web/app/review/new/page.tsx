import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';

export default function NewReviewPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <ShieldCheck className="h-7 w-7 text-verified" />
          Write a verified review
        </h1>
        <p className="mt-4 text-ink/70">
          Before you can submit a review, prove you worked at the company. Your identity is
          never exposed — only an anonymous badge proving the employment relationship.
        </p>
        <Link
          href="/verify"
          className="mt-6 inline-flex rounded-full bg-ocean px-5 py-2.5 font-medium text-white hover:bg-oceanDeep"
        >
          Start verification →
        </Link>
      </div>
    </main>
  );
}
