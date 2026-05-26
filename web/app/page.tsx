import Link from 'next/link';
import { ShieldCheck, Sparkles, Eye, BarChart3, Lock, Sun } from 'lucide-react';
import AdSlot from '@/components/AdSlot';

export default function HomePage() {
  return (
    <main className="mx-auto max-w-6xl px-6 py-12">
      <nav className="flex items-center justify-between pb-12">
        <div className="flex items-center gap-2 text-lg font-semibold text-ink">
          <Sun className="h-6 w-6 text-coral" />
          True Review
        </div>
        <div className="flex items-center gap-6 text-sm text-ink/70">
          <Link href="/search" className="hover:text-ink">Search</Link>
          <Link href="/transparency" className="hover:text-ink">Transparency</Link>
          <Link
            href="/verify"
            className="rounded-full bg-white/60 px-4 py-1.5 backdrop-blur hover:bg-white/80"
          >
            Verify employment
          </Link>
        </div>
      </nav>

      <section className="glass max-w-3xl rounded-3xl p-10">
        <span className="inline-flex items-center gap-2 rounded-full bg-white/60 px-3 py-1 text-xs font-medium text-oceanDeep">
          <ShieldCheck className="h-3.5 w-3.5" />
          Workplace truth, verified at the source
        </span>
        <h1 className="mt-5 font-display text-5xl font-semibold leading-[1.05] tracking-tight text-ink md:text-6xl">
          The calmest place
          <br />
          to read what work
          <br />
          <span className="text-ocean">is really like.</span>
        </h1>
        <p className="mt-6 max-w-xl text-lg leading-relaxed text-ink/75">
          True Review uses cryptographic employment proof, transparent moderation, and AI
          pattern detection to surface honest, evidence-backed workplace insight — without the
          noise and manipulation that have ruined every other review platform.
        </p>
        <div className="mt-8 flex flex-wrap gap-3">
          <Link
            href="/search"
            className="rounded-full bg-ocean px-5 py-2.5 font-medium text-white shadow-lg shadow-ocean/30 hover:bg-oceanDeep"
          >
            Search a company
          </Link>
          <Link
            href="/review/new"
            className="rounded-full bg-white/70 px-5 py-2.5 font-medium text-ink hover:bg-white"
          >
            Write a verified review
          </Link>
        </div>
      </section>

      <section className="mt-16 grid gap-5 md:grid-cols-3">
        <Feature
          icon={<ShieldCheck className="h-5 w-5 text-verified" />}
          title="Zero-knowledge verification"
          body="Prove you worked somewhere without exposing who you are. Work email, payroll API, or document — your choice."
        />
        <Feature
          icon={<Eye className="h-5 w-5 text-ocean" />}
          title="Public moderation logs"
          body="Every removal, edit, and decision is timestamped and explained. No silent censorship. No employer suppression."
        />
        <Feature
          icon={<Sparkles className="h-5 w-5 text-coral" />}
          title="AI copilot"
          body="Ask 'is this company stable?' Answers cite the specific verified reviews behind them."
        />
        <Feature
          icon={<BarChart3 className="h-5 w-5 text-ocean" />}
          title="Real-time health"
          body="Sentiment trends, layoff probability, leadership confidence, burnout risk."
        />
        <Feature
          icon={<Lock className="h-5 w-5 text-verified" />}
          title="Privacy by default"
          body="Metadata minimization, anti-doxxing protections, encrypted proofs. Your verification never leaks."
        />
        <Feature
          icon={<ShieldCheck className="h-5 w-5 text-warn" />}
          title="Reviewer trust scores"
          body="Every reviewer has a transparent credibility score. No popularity contests — just evidence."
        />
      </section>

      <AdSlot slot="home-mid" className="mt-16" />

      <footer className="mt-20 border-t border-white/40 pt-8 text-sm text-ink/55">
        <div className="flex flex-wrap justify-between gap-4">
          <span>© {new Date().getFullYear()} True Review</span>
          <div className="flex gap-6">
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
      <p className="mt-3 text-sm leading-relaxed text-ink/70">{body}</p>
    </div>
  );
}
