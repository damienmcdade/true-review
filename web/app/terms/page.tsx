import Link from 'next/link';

export const metadata = { title: 'Terms — True Review' };

export default function TermsPage() {
  const updated = new Date().toISOString().slice(0, 10);
  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <article className="glass mt-6 rounded-3xl p-8 text-sm leading-relaxed text-ink/80">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Terms of use</h1>
        <p className="mt-2 text-xs text-ink/55">Last updated {updated}</p>

        <Section title="User-generated content">
          <p>
            Reviews and scam reports on True Review are user-generated content. They reflect the
            views of the people who post them and have not been verified by us as factual claims
            of wrongdoing. Where required by law, we publish or remove content following the
            processes described below.
          </p>
        </Section>

        <Section title="Honest reviews are protected">
          <p>
            Consistent with the US Consumer Review Fairness Act (15 U.S.C. § 45b) and similar
            laws, we do not enforce or honour contractual clauses that prohibit, penalise, or
            condition refunds on positive reviews. You can&apos;t be retaliated against for
            posting an honest review.
          </p>
        </Section>

        <Section title="Anti-defamation rules">
          <p>You agree not to post:</p>
          <ul className="list-disc pl-5">
            <li>Statements you know to be false.</li>
            <li>Accusations of specific crimes against named individuals without evidence you can produce on demand.</li>
            <li>Content that identifies third parties&apos; personal data (SSN, payment card, phone, email — automatically blocked).</li>
            <li>Mass-coordinated posts (brigading) intended to manipulate ratings.</li>
          </ul>
        </Section>

        <Section title="Scam reports are claims, not verdicts">
          <p>
            A company is only marked <em>flagged</em> after three independent reports.
            Single-source claims appear as evidence on a company&apos;s page but do not trigger a
            scam label. Severity scores reflect community input, not platform judgements.
          </p>
        </Section>

        <Section title="DMCA — copyright complaints">
          <p>
            To report copyright infringement, send a DMCA-compliant notice to{' '}
            <span className="font-mono">legal@true-review.example</span> including:
          </p>
          <ul className="list-disc pl-5">
            <li>Identification of the copyrighted work.</li>
            <li>Identification of the allegedly infringing material with URL.</li>
            <li>Your contact information.</li>
            <li>A statement of good-faith belief and a statement under penalty of perjury that you are authorised to act.</li>
            <li>Your physical or electronic signature.</li>
          </ul>
          <p>Counter-notices follow the same channel and the procedure described in 17 U.S.C. § 512(g).</p>
        </Section>

        <Section title="EU Digital Services Act (DSA)">
          <p>
            Use the{' '}
            <Link href="/notice-action" className="underline">
              Notice &amp; Action form
            </Link>{' '}
            (DSA Art. 16) to report content. Trusted Flaggers (DSA Art. 22) can apply via{' '}
            <span className="font-mono">trustflagger@true-review.example</span>. We publish a transparency report annually.
          </p>
        </Section>

        <Section title="AI disclosures">
          <p>
            Where we display an AI-generated answer or summary, we label it visibly with the
            model name and the number of reviews used as evidence (EU AI Act Art. 50).
          </p>
        </Section>

        <Section title="Section 230 posture">
          <p>
            True Review is an interactive computer service within the meaning of 47 U.S.C. § 230.
            We do not adopt user statements as our own. Where moderation decisions are made, they
            are recorded in our public moderation log.
          </p>
        </Section>

        <Section title="Limitation of liability">
          <p>
            To the maximum extent permitted by law, True Review and its operators are not liable
            for indirect, incidental, or consequential damages arising from use of the service.
            Statutory consumer rights remain unaffected.
          </p>
        </Section>

        <Section title="Dispute resolution">
          <p>
            Disputes are governed by the laws of the State of Delaware, USA (excluding conflict
            of laws), or, for EU consumers, the law of their member state of residence. EU users
            may use the European Commission&apos;s online dispute resolution platform.
          </p>
        </Section>

        <Section title="Changes">
          <p>We&apos;ll post the &quot;Last updated&quot; date when these terms change. Material changes are highlighted on the home page for 14 days.</p>
        </Section>
      </article>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-6">
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      <div className="mt-2 space-y-2">{children}</div>
    </section>
  );
}
