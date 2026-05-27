'use client';

import { useState, useTransition } from 'react';
import { Loader2, Send, Sparkles } from 'lucide-react';
import { apiFetch, type ApiError } from '@/lib/api';

type AnswerResponse = {
  answer: string;
  citations: number[];
  source: string;
  model: string;
  context_used: number;
};

const SUGGESTIONS = [
  'How is the work-life balance?',
  'Is leadership trusted?',
  'Any reports of fraud or non-delivery?',
  'What do shoppers say about quality?'
];

export default function AskBox({
  companySlug,
  companyName,
  className
}: {
  companySlug: string;
  companyName: string;
  className?: string;
}) {
  const [question, setQuestion] = useState('');
  const [answer, setAnswer] = useState<AnswerResponse | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [pending, startTransition] = useTransition();

  async function ask(q: string) {
    setError(null);
    setAnswer(null);
    startTransition(async () => {
      const { data, error } = await apiFetch<AnswerResponse>('/ai/ask', {
        method: 'POST',
        body: JSON.stringify({ question: q, company_slug: companySlug, limit: 60 }),
        timeoutMs: 40_000
      });
      if (error) setError(error);
      if (data) setAnswer(data);
    });
  }

  return (
    <div className={className}>
      <form
        onSubmit={(e) => {
          e.preventDefault();
          if (question.trim()) void ask(question.trim());
        }}
      >
        <textarea
          value={question}
          onChange={(e) => setQuestion(e.target.value)}
          rows={3}
          placeholder={`Ask anything about ${companyName}…`}
          className="w-full resize-none rounded-2xl border border-white/60 bg-white/80 p-4 text-ink outline-none placeholder:text-ink/40 focus:border-ocean"
        />
        <div className="mt-3 flex flex-wrap items-center justify-between gap-3">
          <div className="flex flex-wrap gap-1.5">
            {SUGGESTIONS.map((s) => (
              <button
                key={s}
                type="button"
                onClick={() => {
                  setQuestion(s);
                  void ask(s);
                }}
                className="rounded-full bg-white/60 px-3 py-1 text-xs text-ink/70 hover:bg-white"
              >
                {s}
              </button>
            ))}
          </div>
          <button
            type="submit"
            disabled={pending || !question.trim()}
            className="inline-flex items-center gap-2 rounded-full bg-ocean px-4 py-2 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
          >
            {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
            Ask
          </button>
        </div>
      </form>

      {error ? (
        <div className="mt-5 rounded-2xl border border-danger/30 bg-danger/5 p-4 text-sm text-danger">
          <div className="font-semibold">
            {error.kind === 'rate_limit'
              ? 'Slow down'
              : error.kind === 'timeout'
                ? 'Request timed out'
                : error.kind === 'network'
                  ? 'Network issue'
                  : 'Something went wrong'}
          </div>
          <p className="mt-1 text-ink/70">{error.message}</p>
          <button
            type="button"
            onClick={() => void ask(question.trim())}
            className="mt-3 rounded-full border border-ink/15 bg-white/60 px-3 py-1 text-xs font-medium text-ink hover:bg-white"
          >
            Retry
          </button>
        </div>
      ) : null}

      {answer ? (
        <div className="glass mt-6 rounded-2xl p-5">
          <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wider text-oceanDeep">
            <Sparkles className="h-3.5 w-3.5" />
            AI copilot · <span className="font-mono text-[10px] text-ink/45">{answer.model}</span>
            <span className="text-ink/40">· {answer.context_used} reviews considered</span>
          </div>
          <p className="mt-3 whitespace-pre-wrap text-sm leading-relaxed text-ink/85">
            {answer.answer}
          </p>
        </div>
      ) : null}
    </div>
  );
}
