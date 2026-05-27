import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';
import VerifyEmailFlow from '@/components/VerifyEmailFlow';

const TIERS = [
  { tier: 'T1', name: 'Work email OTP', desc: 'One-time code to your work address. Free webmail (gmail, yahoo) is rejected.', trust: 'High', active: true },
  { tier: 'T2', name: 'LinkedIn OAuth + employment match', desc: 'We confirm your LinkedIn employment matches your claim.', trust: 'High', active: false },
  { tier: 'T3', name: 'Document upload', desc: 'Upload a redacted W-2, offer letter, or pay stub. Human review.', trust: 'Medium', active: false },
  { tier: 'T4', name: 'Payroll API (Argyle / Pinwheel)', desc: 'Connect your payroll provider. Gold-standard proof.', trust: 'Gold', active: false }
];

export const metadata = { title: 'Verify employment — True Review' };

export default function VerifyPage() {
  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>

      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <ShieldCheck className="h-7 w-7 text-verified" />
          Verify employment
        </h1>
        <p className="mt-3 text-sm text-ink/75">
          Prove you work or worked at a company. We never display your email or identity — only
          an anonymous &ldquo;verified employee&rdquo; badge on your reviews. Your address is
          hashed before storage so a database leak can&apos;t expose it.
        </p>

        <VerifyEmailFlow className="mt-6" />
      </div>

      <div className="mt-6 space-y-2">
        {TIERS.map((t) => (
          <div
            key={t.tier}
            className={
              'glass rounded-xl p-5 ' + (t.active ? '' : 'opacity-60')
            }
          >
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-ocean/15 px-2 py-0.5 text-xs text-oceanDeep">
                  {t.tier}
                </span>
                <span className="font-medium text-ink">{t.name}</span>
              </div>
              <span className="text-xs text-verified">
                {t.active ? `${t.trust} trust · live` : `${t.trust} trust · coming soon`}
              </span>
            </div>
            <p className="mt-2 text-sm text-ink/65">{t.desc}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
