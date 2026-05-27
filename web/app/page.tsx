import Link from 'next/link';
import { ShieldCheck, Sparkles, Eye, BarChart3, ShoppingBag, AlertTriangle, Briefcase, Sun } from 'lucide-react';
import AdSlot from '@/components/AdSlot';
import AiSearch from '@/components/AiSearch';

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-10">
      <nav className="flex items-center justify-between pb-10">
        <Link href="/" className="flex items-center gap-2 text-lg font-semibold text-ink">
          <Sun className="h-6 w-6 text-coral" />
          True Review
        </Link>
        <div className="flex items-center gap-5 text-sm text-ink/75">
          <Link href="/search" className="hover:text-ink">Search</Link>
          <Link href="/scam-alerts" className="flex items-center gap-1 text-scam hover:text-danger">
            <AlertTriangle className="h-4 w-4" />
            Scam alerts
          </Link>
          <Link href="/transparency" className="hover:text-ink">Transparency</Link>
          <Link
            href="/verify"
            className="rounded-full bg-white/70 px-4 py-1.5 backdrop-blur hover:bg-white"
          >
            Verify
          </Link>
        </div>
      </nav>

      <section className="glass max-w-3xl rounded-3xl p-10">
        <span className="inline-flex items-center gap-2 rounded-full bg-white/70 px-3 py-1 text-xs font-medium text-oceanDeep">
          <ShieldCheck className="h-3.5 w-3.5" />
          Verified reviews for jobs, shopping &amp; scams
        </span>
        <h1 className="mt-5 font-display text-5xl font-semibold leading-[1.05] tracking-tight text-ink md:text-6xl">
          Real reviews from
          <br />
          <span className="text-oceanDeep">real humans.</span>
        </h1>
        <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink/80">
          Look up any company — by name or domain — and read verified reviews from employees and
          shoppers, plus active scam reports the community has flagged. Ask the AI copilot a
          plain-English question; it answers using only the verified reviews.
        </p>

        <AiSearch className="mt-8" />
      </section>

      <section className="mt-14 grid gap-5 md:grid-cols-3">
        <PurposeCard
          icon={<Briefcase className="h-5 w-5 text-ocean" />}
          title="Employment"
          body="Read what current and former employees actually say. Pay, culture, management — sourced from verified workers."
          href="/search?kind=employer"
          cta="Browse employers"
        />
        <PurposeCard
          icon={<ShoppingBag className="h-5 w-5 text-coral" />}
          title="Shopping"
          body="Real shopper experiences with merchants — product quality, shipping, returns, customer support. Cut through fake reviews."
          href="/search?kind=merchant"
          cta="Browse merchants"
        />
        <PurposeCard
          icon={<AlertTriangle className="h-5 w-5 text-scam" />}
          title="Scam alerts"
          body="Companies the community has flagged for non-delivery, phishing, counterfeits, and fraud. Check before you buy or apply."
          href="/scam-alerts"
          cta="See active flags"
          urgent
        />
      </section>

      <section className="mt-14 grid gap-5 md:grid-cols-3">
        <Feature
          icon={<ShieldCheck className="h-5 w-5 text-verified" />}
          title="Zero-knowledge verification"
          body="Prove you worked or shopped somewhere without exposing who you are."
        />
        <Feature
          icon={<Eye className="h-5 w-5 text-ocean" />}
          title="Public moderation logs"
          body="Every removal and edit is timestamped and explained. No silent censorship."
        />
        <Feature
          icon={<Sparkles className="h-5 w-5 text-coral" />}
          title="AI copilot"
          body="Ask 'is this company a scam?' or 'is leadership trusted?' Answers cite the verified reviews."
        />
        <Feature
          icon={<BarChart3 className="h-5 w-5 text-ocean" />}
          title="Trust scores"
          body="Per-company and per-reviewer scores based on verification, evidence, and consistency."
        />
        <Feature
          icon={<AlertTriangle className="h-5 w-5 text-scam" />}
          title="Scam flagging"
          body="Community-flagged with categories: non-delivery, phishing, counterfeits, fake jobs, fake invoices."
        />
        <Feature
          icon={<ShieldCheck className="h-5 w-5 text-warn" />}
          title="Privacy by default"
          body="Metadata minimization, anti-doxxing protections, encrypted employment proofs."
        />
      </section>

      <AdSlot slot="home-mid" className="mt-14" />

      <footer className="mt-20 border-t border-white/40 pt-8 text-sm text-ink/60">
        <div className="flex flex-wrap justify-between gap-4">
          <span>© {new Date().getFullYear()} True Review</span>
          <div className="flex gap-6">
            <Link href="/scam-alerts">Scam alerts</Link>
            <Link href="/transparency">Transparency</Link>
            <Link href="/privacy">Privacy</Link>
            <Link href="/terms">Terms</Link>
          </div>
        </div>
      </footer>
    </main>
  );
}

function Feature({ icon, title, body }: { icon: React.ReactNode; title: string; body: string }) {
  return (
    <div className="glass rounded-2xl p-6">
      <div className="flex items-center gap-2 text-sm font-medium text-ink">
        {icon}
        {title}
      </div>
      <p className="mt-3 text-sm leading-relaxed text-ink/75">{body}</p>
    </div>
  );
}

function PurposeCard({
  icon,
  title,
  body,
  href,
  cta,
  urgent
}: {
  icon: React.ReactNode;
  title: string;
  body: string;
  href: string;
  cta: string;
  urgent?: boolean;
}) {
  return (
    <Link
      href={href as never}
      className="glass group flex flex-col rounded-2xl p-6 transition hover:bg-white/80"
    >
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2 text-sm font-semibold text-ink">
          {icon}
          {title}
        </div>
        {urgent ? (
          <span className="rounded-full bg-scam/15 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wider text-scam">
            Active
          </span>
        ) : null}
      </div>
      <p className="mt-3 grow text-sm leading-relaxed text-ink/75">{body}</p>
      <span className="mt-4 inline-flex items-center text-sm font-medium text-oceanDeep group-hover:underline">
        {cta} →
      </span>
    </Link>
  );
}
