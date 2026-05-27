import type { MetadataRoute } from 'next';

const SITE = process.env.NEXT_PUBLIC_SITE_URL || 'https://truereview.dev';

export default function robots(): MetadataRoute.Robots {
  return {
    rules: [
      {
        userAgent: '*',
        allow: '/',
        // Don't index server-rendered detail pages whose state changes
        // every few seconds, or the moderation appeal flow.
        disallow: ['/api/', '/notice-action', '/data-request']
      }
    ],
    sitemap: `${SITE}/sitemap.xml`,
    host: SITE
  };
}
