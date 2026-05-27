import Link from 'next/link';

type LogEntry = {
  id: string;
  review_id?: string | null;
  action: string;
  reason: string;
  moderator_handle: string;
  created_at: string;
};

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getLog(): Promise<LogEntry[]> {
  try {
    const res = await fetch(`${API}/moderation/log`, { next: { revalidate: 30 } });
    if (!res.ok) return [];
    return (await res.json()) as LogEntry[];
  } catch {
    return [];
  }
}

export const metadata = { title: 'Transparency — True Review' };

export default async function TransparencyPage() {
  const entries = await getLog();
  return (
    <main className="mx-auto max-w-3xl px-6 py-10">
      <Link href="/" className="text-sm text-ink/55 hover:text-ink/80">
        ← True Review
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="font-display text-3xl font-semibold tracking-tight">Transparency</h1>
        <p className="mt-3 text-ink/80">
          Every moderation decision on True Review is logged here — tamper-evident with a SHA-256
          hash chain so prior entries can&apos;t be silently rewritten. We publish:
        </p>
        <ul className="mt-3 list-disc space-y-1 pl-5 text-sm text-ink/75">
          <li>What action was taken (removed, edited, warned, reinstated).</li>
          <li>The reason and the moderator handle.</li>
          <li>When it happened.</li>
        </ul>
        <p className="mt-4 text-sm text-ink/65">
          For EU DSA Article 13 contact, see{' '}
          <Link href="/notice-action" className="underline">
            Notice &amp; Action
          </Link>
          . Trusted Flaggers (Art. 22):{' '}
          <span className="font-mono">trustflagger@true-review.example</span>.
        </p>
      </div>

      <div className="mt-6 space-y-2">
        {entries.length === 0 ? (
          <div className="glass rounded-xl p-5 text-sm text-ink/55">
            No moderation actions logged yet.
          </div>
        ) : (
          entries.map((e) => (
            <div key={e.id} className="glass rounded-xl p-4 text-sm">
              <div className="flex items-center justify-between">
                <span className="font-medium text-ink">{e.action}</span>
                <span className="text-xs text-ink/55">{new Date(e.created_at).toLocaleString()}</span>
              </div>
              <p className="mt-1 text-ink/70">{e.reason}</p>
              <p className="mt-2 text-xs text-ink/45">
                moderator: {e.moderator_handle}
                {e.review_id ? ` · review ${e.review_id}` : ''}
              </p>
            </div>
          ))
        )}
      </div>
    </main>
  );
}
