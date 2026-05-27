'use client';

import { useState, useTransition } from 'react';
import { Loader2, Send } from 'lucide-react';
import { apiFetch, type ApiError } from '@/lib/api';

export default function NoticeForm({ className }: { className?: string }) {
  const [reviewId, setReviewId] = useState('');
  const [reason, setReason] = useState('defamatory');
  const [details, setDetails] = useState('');
  const [contact, setContact] = useState('');
  const [done, setDone] = useState<{ status: string } | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [pending, startTransition] = useTransition();

  function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (details.trim().length < 20) {
      setError({
        status: null,
        kind: 'client',
        message: 'Please describe the problem in at least 20 characters.'
      });
      return;
    }
    startTransition(async () => {
      const { data, error } = await apiFetch<{ status: string }>('/notice-action', {
        method: 'POST',
        body: JSON.stringify({
          review_id: reviewId.trim(),
          reason,
          details: details.trim(),
          reporter_contact: contact.trim()
        })
      });
      if (error) setError(error);
      if (data) setDone(data);
    });
  }

  if (done) {
    return (
      <div className={'rounded-2xl border border-verified/40 bg-verified/10 p-4 text-sm ' + (className ?? '')}>
        <div className="font-semibold text-verified">Report received</div>
        <p className="mt-1 text-ink/75">
          Status: {done.status}. We log every notice in our tamper-evident audit trail and review
          within 7 days. If you provided a contact, we&apos;ll email you the outcome.
        </p>
      </div>
    );
  }

  return (
    <form onSubmit={onSubmit} className={className}>
      <Field label="Content URL or review ID (optional)">
        <input
          value={reviewId}
          onChange={(e) => setReviewId(e.target.value)}
          placeholder="paste the URL of the page or the review id"
          className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
        />
      </Field>

      <Field label="Reason">
        <select
          value={reason}
          onChange={(e) => setReason(e.target.value)}
          className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
        >
          <option value="defamatory">Defamatory / false statement of fact</option>
          <option value="copyright">Copyright infringement (DMCA)</option>
          <option value="pii">Personal data of a third party</option>
          <option value="illegal">Otherwise illegal content</option>
          <option value="impersonation">Impersonation</option>
          <option value="harassment">Harassment / threats</option>
          <option value="other">Other</option>
        </select>
      </Field>

      <Field label="Describe the issue">
        <textarea
          value={details}
          onChange={(e) => setDetails(e.target.value)}
          rows={5}
          placeholder="What is wrong with this content? Include any evidence we should consider."
          className="mt-1 w-full resize-none rounded-2xl border border-white/60 bg-white/80 p-4 text-ink outline-none focus:border-ocean"
        />
      </Field>

      <Field label="Your email (optional, for our response)">
        <input
          type="email"
          value={contact}
          onChange={(e) => setContact(e.target.value)}
          placeholder="you@example.com"
          className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-2.5 text-ink outline-none focus:border-ocean"
        />
      </Field>

      {error ? (
        <p className="mt-4 rounded-2xl border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
          {error.message}
        </p>
      ) : null}

      <div className="mt-6 flex justify-end">
        <button
          type="submit"
          disabled={pending}
          className="inline-flex items-center gap-2 rounded-full bg-ocean px-5 py-2.5 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          Submit notice
        </button>
      </div>
    </form>
  );
}

function Field({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="mt-4 block text-xs font-semibold uppercase tracking-wider text-ink/55">
      {label}
      {children}
    </label>
  );
}
