import Link from 'next/link';
import { Sparkles } from 'lucide-react';

export default async function AskPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  return (
    <main className="mx-auto max-w-2xl px-6 py-12">
      <Link href={`/c/${slug}` as const} className="text-sm text-ink/50 hover:text-ink/80">
        ← Back to {slug}
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <Sparkles className="h-7 w-7 text-coral" />
          Ask the AI copilot
        </h1>
        <p className="mt-4 text-ink/70">
          Ask anything about working at <span className="font-medium">{slug}</span>. Every answer
          will cite the verified reviews behind it.
        </p>

        <div className="mt-8 rounded-2xl bg-white/55 p-5">
          <textarea
            className="w-full resize-none bg-transparent text-ink placeholder:text-ink/40 focus:outline-none"
            rows={3}
            placeholder="e.g. Is leadership trusted by the engineering team?"
          />
          <div className="mt-3 flex justify-end">
            <button
              type="button"
              className="rounded-full bg-ocean px-4 py-2 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
              disabled
            >
              Ask (coming soon)
            </button>
          </div>
        </div>

        <p className="mt-6 text-xs text-ink/45">
          The copilot ships in milestone M4. For now this is a UI placeholder.
        </p>
      </div>
    </main>
  );
}
