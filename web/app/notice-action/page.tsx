import Link from 'next/link';
import NoticeForm from '@/components/NoticeForm';

export const metadata = { title: 'Notice & Action — True Review' };

export default function NoticeActionPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">
          Report content (Notice &amp; Action)
        </h1>
        <p className="mt-3 text-sm text-ink/75">
          Use this form to report content you believe is illegal, defamatory, infringes
          intellectual property, or otherwise violates our{' '}
          <Link href="/terms" className="underline">
            terms
          </Link>
          . We follow the EU Digital Services Act Article 16 process. You&apos;ll get a reference
          number and a decision within 7 days for most reports.
        </p>
        <NoticeForm className="mt-6" />
      </div>
    </main>
  );
}
