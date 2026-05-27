import type { MetadataRoute } from 'next';

const SITE = process.env.NEXT_PUBLIC_SITE_URL || 'https://truereview.dev';
const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

type SearchHit = { slug: string };

async function getRecentCompanies(): Promise<string[]> {
  // Pull all companies the search endpoint will return for an empty/wildcard
  // query. We use a short timeout so a slow API doesn't tank the sitemap.
  try {
    const res = await fetch(`${API}/companies?q=&limit=100`, {
      next: { revalidate: 600 }
    });
    if (!res.ok) return [];
    const data = (await res.json()) as SearchHit[];
    return data.map((c) => c.slug).filter(Boolean);
  } catch {
    return [];
  }
}

export default async function sitemap(): Promise<MetadataRoute.Sitemap> {
  const now = new Date();

  const staticRoutes: MetadataRoute.Sitemap = [
    { url: `${SITE}/`, lastModified: now, changeFrequency: 'daily', priority: 1.0 },
    { url: `${SITE}/search`, lastModified: now, changeFrequency: 'daily', priority: 0.9 },
    { url: `${SITE}/scam-alerts`, lastModified: now, changeFrequency: 'hourly', priority: 0.9 },
    { url: `${SITE}/scam-check`, lastModified: now, changeFrequency: 'weekly', priority: 0.8 },
    { url: `${SITE}/verify`, lastModified: now, changeFrequency: 'monthly', priority: 0.6 },
    { url: `${SITE}/review/new`, lastModified: now, changeFrequency: 'monthly', priority: 0.6 },
    { url: `${SITE}/transparency`, lastModified: now, changeFrequency: 'daily', priority: 0.5 },
    { url: `${SITE}/privacy`, lastModified: now, changeFrequency: 'monthly', priority: 0.3 },
    { url: `${SITE}/terms`, lastModified: now, changeFrequency: 'monthly', priority: 0.3 },
    { url: `${SITE}/cookies`, lastModified: now, changeFrequency: 'monthly', priority: 0.3 },
    { url: `${SITE}/accessibility`, lastModified: now, changeFrequency: 'monthly', priority: 0.3 }
  ];

  const slugs = await getRecentCompanies();
  const companyRoutes: MetadataRoute.Sitemap = slugs.map((slug) => ({
    url: `${SITE}/c/${slug}`,
    lastModified: now,
    changeFrequency: 'daily',
    priority: 0.7
  }));

  return [...staticRoutes, ...companyRoutes];
}
