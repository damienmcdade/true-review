import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';
import ReviewForm from '@/components/ReviewForm';

export default function NewReviewPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <ShieldCheck className="h-7 w-7 text-verified" />
          Submit a review
        </h1>
        <p className="mt-3 text-ink/75">
          Share an employment experience, a shopping experience, or report a scam. Be specific —
          your post lands on the company&apos;s page and feeds the AI copilot&apos;s answers. Full
          identity verification is required before posts appear publicly; for this preview build,
          submissions go straight in as anonymous.
        </p>
        <ReviewForm className="mt-6" />
      </div>
    </main>
  );
}
