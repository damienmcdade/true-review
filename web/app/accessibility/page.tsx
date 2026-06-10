import Link from 'next/link';

export const metadata = { title: 'Accessibility — True Review' };

export default function AccessibilityPage() {
  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <article className="glass mt-6 rounded-3xl p-8 text-sm text-ink/80">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Accessibility statement</h1>
        <p className="mt-3">
          True Review targets <strong>WCAG 2.1 Level AA</strong> and is designed to be usable by
          people with a wide range of abilities and assistive technologies. Section 508 § 1194.22
          web content requirements have been considered in implementation.
        </p>
        <h2 className="mt-6 text-base font-semibold text-ink">What we do</h2>
        <ul className="mt-2 list-disc space-y-1 pl-5">
          <li>Skip-to-content link on every page (press Tab from the top).</li>
          <li>Keyboard-navigable controls with visible focus rings.</li>
          <li>Semantic HTML headings, lists, and landmarks.</li>
          <li>Honors <code className="font-mono">prefers-reduced-motion</code> — animations stop.</li>
          <li>Colour palette tested at AA contrast for body text on the beach backdrop.</li>
          <li>Form controls have associated labels and error messages.</li>
        </ul>
        <h2 className="mt-6 text-base font-semibold text-ink">Found a problem?</h2>
        <p className="mt-2">
          Email <span className="font-mono">info@cyberwaveglobal.com</span>. We aim to
          acknowledge within 2 business days and remediate AA-blocking issues within 30 days.
        </p>
      </article>
    </main>
  );
}
