import Link from 'next/link';
import { ShieldCheck } from 'lucide-react';

const TIERS = [
  {
    tier: 'T1',
    name: 'Work email OTP',
    desc: 'One-time code sent to your work address. Verified instantly, never displayed publicly.',
    trust: 'High'
  },
  {
    tier: 'T2',
    name: 'LinkedIn OAuth + employment match',
    desc: 'We confirm your LinkedIn employment matches your claim. No profile data is shared publicly.',
    trust: 'High'
  },
  {
    tier: 'T3',
    name: 'Document upload',
    desc: 'Upload a redacted W-2, offer letter, or pay stub. Reviewed by a human verifier with no employer access.',
    trust: 'Medium'
  },
  {
    tier: 'T4',
    name: 'Payroll API (Argyle / Pinwheel)',
    desc: 'Connect your payroll provider. The strongest proof — and your employer never sees the request.',
    trust: 'Gold'
  }
];

export default function VerifyPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-12">
      <Link href="/" className="text-sm text-ink/50 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <ShieldCheck className="h-7 w-7 text-verified" />
          Prove employment privately
        </h1>
        <p className="mt-4 text-ink/75">
          Choose a verification method. Your identity is never exposed — only an anonymous badge
          proving you worked at the company you&apos;re reviewing.
        </p>
      </div>
      <div className="mt-6 space-y-3">
        {TIERS.map((t) => (
          <div key={t.tier} className="glass rounded-xl p-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="rounded-full bg-ocean/15 px-2 py-0.5 text-xs text-oceanDeep">
                  {t.tier}
                </span>
                <span className="font-medium">{t.name}</span>
              </div>
              <span className="text-xs text-verified">{t.trust} trust</span>
            </div>
            <p className="mt-2 text-sm text-ink/65">{t.desc}</p>
          </div>
        ))}
      </div>
    </main>
  );
}
