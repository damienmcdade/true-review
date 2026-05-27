import { NextResponse, type NextRequest } from 'next/server';

/**
 * Security headers — aligned to:
 * - DISA ASD STIG V-222489 (web app security headers)
 * - NIST 800-53 SC-7, SC-8, SI-10, SI-11
 * - OWASP Secure Headers Project
 *
 * Notes on CSP:
 *  - 'strict-dynamic' is intentionally NOT used because we need adsense + the
 *    Vercel runtime helpers, both of which load additional scripts. We
 *    explicitly allow the minimum domains.
 *  - 'unsafe-inline' on style-src is required for Tailwind + Next inline
 *    style tags; mitigated by very tight script-src and DOM XSS-safe React.
 */
export function middleware(req: NextRequest) {
  const res = NextResponse.next();

  const apiOrigin = process.env.NEXT_PUBLIC_API_URL?.replace(/\/$/, '') ?? '';
  const adsenseOrigins =
    'https://pagead2.googlesyndication.com https://googleads.g.doubleclick.net https://www.googletagservices.com https://ep1.adtrafficquality.google https://www.google.com';

  const csp = [
    "default-src 'self'",
    `script-src 'self' 'unsafe-inline' ${adsenseOrigins}`,
    "style-src 'self' 'unsafe-inline'",
    `img-src 'self' data: blob: ${adsenseOrigins} https://*.googleusercontent.com`,
    "font-src 'self' data:",
    `connect-src 'self' ${apiOrigin} ${adsenseOrigins}`,
    `frame-src ${adsenseOrigins}`,
    "object-src 'none'",
    "base-uri 'self'",
    "form-action 'self'",
    "frame-ancestors 'none'",
    'upgrade-insecure-requests'
  ].join('; ');

  res.headers.set('Content-Security-Policy', csp);
  res.headers.set('X-Content-Type-Options', 'nosniff');
  res.headers.set('X-Frame-Options', 'DENY');
  res.headers.set('Referrer-Policy', 'strict-origin-when-cross-origin');
  res.headers.set(
    'Permissions-Policy',
    'geolocation=(), microphone=(), camera=(), payment=(), accelerometer=(), gyroscope=()'
  );
  res.headers.set('Strict-Transport-Security', 'max-age=63072000; includeSubDomains; preload');
  res.headers.set('Cross-Origin-Opener-Policy', 'same-origin');
  res.headers.set('Cross-Origin-Resource-Policy', 'same-origin');
  res.headers.set('X-DNS-Prefetch-Control', 'off');

  return res;
}

export const config = {
  matcher: [
    // Apply to all paths except static assets that don't benefit from the headers.
    '/((?!_next/static|_next/image|favicon.ico).*)'
  ]
};
