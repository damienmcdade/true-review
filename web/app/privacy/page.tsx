import Link from 'next/link';

export const metadata = { title: 'Privacy — True Review' };

export default function PrivacyPage() {
  const updated = new Date().toISOString().slice(0, 10);
  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <article className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Privacy policy</h1>
        <p className="mt-2 text-xs text-ink/55">Last updated {updated}</p>

        <Section title="What we collect">
          <ul className="list-disc pl-5">
            <li>Review submissions you send us (title, body, ratings, category).</li>
            <li>A salted SHA-256 hash of your IP address for rate-limiting and abuse correlation. We never store the raw IP.</li>
            <li>If you provide a contact for a content-removal request, that contact email.</li>
            <li>Standard server logs (timestamp, route, status), kept only as long as needed for operations, security, and abuse prevention.</li>
          </ul>
        </Section>

        <Section title="What we don’t collect">
          <ul className="list-disc pl-5">
            <li>No account login is required to read content.</li>
            <li>Reviews are anonymous by default; we do not link your handle to a real identity unless you explicitly verify employment.</li>
            <li>We do not sell personal data.</li>
          </ul>
        </Section>

        <Section title="Cookies and ads">
          <p>
            We use a single essential cookie for cookie-consent state. With your consent, Google
            AdSense may set advertising cookies. You can change consent at any time by clearing
            site data in your browser. See{' '}
            <Link href="/cookies" className="underline">
              cookie details
            </Link>
            .
          </p>
        </Section>

        <Section title="Your rights (GDPR, CCPA/CPRA, and US state privacy laws)">
          <p>If you are in the EU, UK, California, Virginia, Colorado, Connecticut, Utah, or another jurisdiction with comparable rights, you can:</p>
          <ul className="list-disc pl-5">
            <li>Request a copy of any data we hold about you.</li>
            <li>Request correction or deletion of your reviews.</li>
            <li>Object to processing or withdraw consent.</li>
            <li>Opt out of personalised advertising (browser-level via consent banner).</li>
          </ul>
          <p className="mt-3">
            Use the{' '}
            <Link href="/data-request" className="underline">
              data-request form
            </Link>{' '}
            or email <span className="font-mono">info@cyberwaveglobal.com</span>. We respond within 30 days (GDPR) or 45 days (CCPA).
          </p>
        </Section>

        <Section title="Retention">
          <p>
            Reviews are retained while they remain useful to the community. Moderation actions are
            recorded in a tamper-evident audit log. IP-address hashes and server logs are retained
            only as long as necessary for security and abuse prevention, and removed when no longer
            needed. You can request deletion of content about you at any time (see above).
          </p>
        </Section>

        <Section title="Security">
          <p>
            Transport encrypted with TLS 1.2+. HSTS preload on all responses. Content Security
            Policy + COOP/COEP/CORP applied. Hardening aligned to DISA ASD STIG controls
            V-222394 (crypto), V-222459 (SQLi prevention via ORM), V-222461 (input validation),
            V-222489 (security headers), V-222496 (tamper-evident audit log).
          </p>
        </Section>

        <Section title="Children">
          <p>True Review is not intended for users under 16. We do not knowingly collect data from minors (COPPA / GDPR Art. 8).</p>
        </Section>

        <Section title="International transfers">
          <p>
            Servers are in the United States. EU/UK data transferred under Standard Contractual
            Clauses. We work to align with the EU-US Data Privacy Framework.
          </p>
        </Section>

        <Section title="Contact">
          <p>
            Privacy: <span className="font-mono">info@cyberwaveglobal.com</span>
            <br />
            Legal / DMCA: <span className="font-mono">info@cyberwaveglobal.com</span>
            <br />
            EU representative (DSA Art. 13): see{' '}
            <Link href="/transparency" className="underline">
              transparency page
            </Link>
            .
          </p>
        </Section>
      </article>
    </main>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="mt-6 text-sm leading-relaxed text-ink/80">
      <h2 className="text-base font-semibold text-ink">{title}</h2>
      <div className="mt-2 space-y-2">{children}</div>
    </section>
  );
}
