'use client';

import { useState, useTransition } from 'react';
import { Loader2, Send, ShieldCheck, AlertCircle } from 'lucide-react';
import { apiFetch, type ApiError } from '@/lib/api';

type StartResp = {
  token: string;
  domain: string;
  expires_in_seconds: number;
  email_sent: boolean;
  delivery: 'resend' | 'log' | null;
  delivery_error?: string | null;
};

type ConfirmResp = {
  verified: boolean;
  domain: string;
  company_slug: string | null;
  tier: string;
  verification_token?: string | null;
};

function slugify(s: string): string {
  return s.toLowerCase().trim().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
}

// Stash the signed verification token so ReviewForm can attach it on submit and
// the author gets the "verified" badge. Keyed by company slug ('*' = any).
function stashVerificationToken(token: string, companySlug: string | null, typedSlug: string) {
  try {
    const slug = slugify(companySlug || typedSlug || '') || '*';
    sessionStorage.setItem(`tr_vtoken:${slug}`, token);
  } catch {
    /* sessionStorage unavailable (privacy mode) — badge just won't apply */
  }
}

export default function VerifyEmailFlow({ className }: { className?: string }) {
  const [email, setEmail] = useState('');
  const [companySlug, setCompanySlug] = useState('');
  const [started, setStarted] = useState<StartResp | null>(null);
  const [otp, setOtp] = useState('');
  const [done, setDone] = useState<ConfirmResp | null>(null);
  const [error, setError] = useState<ApiError | null>(null);
  const [pending, startTransition] = useTransition();

  function startVerify(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email)) {
      setError({ status: null, kind: 'client', message: 'Enter a valid email address.' });
      return;
    }
    startTransition(async () => {
      const { data, error } = await apiFetch<StartResp>('/verify/email/start', {
        method: 'POST',
        body: JSON.stringify({ email, company_slug: companySlug || undefined })
      });
      if (error) setError(error);
      if (data) setStarted(data);
    });
  }

  function confirmOtp(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    if (!/^\d{6}$/.test(otp)) {
      setError({ status: null, kind: 'client', message: 'OTP must be 6 digits.' });
      return;
    }
    if (!started) return;
    startTransition(async () => {
      const { data, error } = await apiFetch<ConfirmResp>('/verify/email/confirm', {
        method: 'POST',
        body: JSON.stringify({ token: started.token, otp })
      });
      if (error) setError(error);
      if (data) {
        if (data.verification_token) stashVerificationToken(data.verification_token, data.company_slug, companySlug);
        setDone(data);
      }
    });
  }

  if (done) {
    return (
      <div className={className}>
        <div className="rounded-2xl border border-verified/40 bg-verified/10 p-5">
          <div className="flex items-center gap-2 font-semibold text-verified">
            <ShieldCheck className="h-5 w-5" />
            Verified
          </div>
          <p className="mt-2 text-sm text-ink/80">
            You&apos;re verified at <strong>{done.domain}</strong> (tier {done.tier}). A review you
            submit{done.company_slug ? <> for <strong>{done.company_slug}</strong></> : null} in this
            browser will carry an anonymous &ldquo;verified employee&rdquo; badge. Your email is
            never shown or linked to the review.
          </p>
        </div>
      </div>
    );
  }

  if (started) {
    return (
      <form onSubmit={confirmOtp} className={className}>
        <p className="text-sm text-ink/80">
          We sent a 6-digit code to your work email at <strong>@{started.domain}</strong>. Enter
          it below within 10 minutes.
        </p>
        {!started.email_sent && started.delivery === 'log' ? (
          <div className="mt-3 flex items-start gap-2 rounded-2xl border border-warn/40 bg-warn/10 p-3 text-xs text-warn">
            <AlertCircle className="mt-0.5 h-4 w-4 shrink-0" />
            <div>
              Email delivery isn&apos;t configured on this preview deployment (Resend not set).
              For a live demo, the code is logged on the API server side. Once <code className="font-mono">RESEND_API_KEY</code> is set on Railway, real emails will go out.
            </div>
          </div>
        ) : null}

        <Label className="mt-5">6-digit code</Label>
        <input
          inputMode="numeric"
          autoFocus
          maxLength={6}
          value={otp}
          onChange={(e) => setOtp(e.target.value.replace(/\D/g, ''))}
          placeholder="123456"
          className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-3 text-center font-mono text-lg tracking-[0.5em] text-ink outline-none focus:border-ocean"
        />

        {error ? (
          <p className="mt-3 rounded-2xl border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
            {error.message}
          </p>
        ) : null}

        <div className="mt-5 flex items-center justify-between">
          <button
            type="button"
            onClick={() => {
              setStarted(null);
              setOtp('');
              setError(null);
            }}
            className="text-sm text-ink/55 hover:text-ink/80"
          >
            Start over
          </button>
          <button
            type="submit"
            disabled={pending || otp.length !== 6}
            className="inline-flex items-center gap-2 rounded-full bg-ocean px-5 py-2.5 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
          >
            {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <ShieldCheck className="h-4 w-4" />}
            Confirm
          </button>
        </div>
      </form>
    );
  }

  return (
    <form onSubmit={startVerify} className={className}>
      <Label>Work email</Label>
      <input
        type="email"
        autoCapitalize="off"
        autoCorrect="off"
        spellCheck={false}
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="you@yourcompany.com"
        className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-3 text-ink outline-none focus:border-ocean"
      />
      <p className="mt-1 text-xs text-ink/55">
        Gmail/Yahoo/Outlook are rejected — your address must be a company-issued mailbox.
      </p>

      <Label className="mt-4">Company slug (optional)</Label>
      <input
        value={companySlug}
        onChange={(e) => setCompanySlug(e.target.value)}
        placeholder="e.g. patagonia"
        className="mt-1 w-full rounded-full border border-white/60 bg-white/80 px-4 py-3 text-ink outline-none focus:border-ocean"
      />

      {error ? (
        <p className="mt-3 rounded-2xl border border-danger/30 bg-danger/5 p-3 text-sm text-danger">
          {error.message}
        </p>
      ) : null}

      <div className="mt-5 flex items-center justify-end">
        <button
          type="submit"
          disabled={pending}
          className="inline-flex items-center gap-2 rounded-full bg-ocean px-5 py-2.5 text-sm font-medium text-white hover:bg-oceanDeep disabled:opacity-50"
        >
          {pending ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          Send code
        </button>
      </div>
    </form>
  );
}

function Label({ children, className }: { children: React.ReactNode; className?: string }) {
  return (
    <label className={'block text-xs font-semibold uppercase tracking-wider text-ink/55 ' + (className ?? '')}>
      {children}
    </label>
  );
}
