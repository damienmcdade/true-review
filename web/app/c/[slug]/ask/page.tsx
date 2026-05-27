import Link from 'next/link';
import { Sparkles } from 'lucide-react';
import AskBox from '@/components/AskBox';

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

async function getCompany(slug: string) {
  try {
    const res = await fetch(`${API}/companies/${slug}`, { next: { revalidate: 30 } });
    if (!res.ok) return null;
    return (await res.json()) as { name: string; slug: string };
  } catch {
    return null;
  }
}

export default async function AskPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const company = await getCompany(slug);
  const name = company?.name ?? slug;

  return (
    <main className="mx-auto max-w-2xl px-6 py-10">
      <Link href={`/c/${slug}` as never} className="text-sm text-ink/55 hover:text-ink/80">
        ← Back to {name}
      </Link>
      <div className="glass mt-6 rounded-3xl p-8">
        <h1 className="flex items-center gap-3 font-display text-3xl font-semibold tracking-tight">
          <Sparkles className="h-7 w-7 text-coral" />
          Ask about {name}
        </h1>
        <p className="mt-3 text-ink/75">
          Type a plain-English question. The copilot answers using only the verified reviews on
          file for {name} — and tells you when there aren&apos;t enough to be confident.
        </p>
        <AskBox companySlug={slug} companyName={name} className="mt-6" />
      </div>
    </main>
  );
}
