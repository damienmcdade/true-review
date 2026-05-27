"""Seed the database with substantial demo content.

LEGAL POSTURE — please read before editing:
- Every seeded review is is_demo=True. The frontend shows a visible
  "Demo content" badge.
- Seeded reviews are written naturalistically (varied voice, length,
  sentiment) so the platform demos well, but they are NOT attributed to
  real first-person reviewers. They are illustrative seed text and will
  be retired once real verified users start posting.
- Real, publicly-known companies are included as search targets with
  mild, balanced, mixed-sentiment reviews — nothing that would be
  defamatory if a court read it.
- "Scam-flagged" entities are ALL clearly fictional with a "-demo"
  slug and a name that no reasonable reader could mistake for a real
  business. They demonstrate the scam-report flow for each archetypal
  pattern (FTC Consumer Sentinel categories) without naming any real
  defendant.

This file is idempotent — re-running adds anything new, never replaces
anything that already exists.
"""
from datetime import datetime

from sqlmodel import Session, select

from .models import Company, CompanyKind, Review, ReviewType, User, VerificationTier


# --------------------------------------------------------------------------- #
# Companies: 20 real public companies + 8 fictional scam archetypes
# --------------------------------------------------------------------------- #

SAMPLE_COMPANIES = [
    # --- Employers / merchants (real, public) ---
    {"name": "Stripe", "slug": "stripe", "kind": "employer", "domain": "stripe.com",
     "description": "Payments infrastructure for the internet."},
    {"name": "Anthropic", "slug": "anthropic", "kind": "employer", "domain": "anthropic.com",
     "description": "AI safety company that builds Claude."},
    {"name": "Shopify", "slug": "shopify", "kind": "both", "domain": "shopify.com",
     "description": "Commerce platform powering millions of merchants."},
    {"name": "Patagonia", "slug": "patagonia", "kind": "both", "domain": "patagonia.com",
     "description": "Outdoor apparel; mission-driven sustainability brand."},
    {"name": "Costco", "slug": "costco", "kind": "merchant", "domain": "costco.com",
     "description": "Membership warehouse retailer."},
    {"name": "Apple", "slug": "apple", "kind": "both", "domain": "apple.com",
     "description": "Consumer electronics and services."},
    {"name": "Microsoft", "slug": "microsoft", "kind": "employer", "domain": "microsoft.com",
     "description": "Software, cloud, devices."},
    {"name": "Netflix", "slug": "netflix", "kind": "employer", "domain": "netflix.com",
     "description": "Streaming entertainment service."},
    {"name": "Amazon", "slug": "amazon", "kind": "both", "domain": "amazon.com",
     "description": "Online retail and cloud services."},
    {"name": "Google", "slug": "google", "kind": "employer", "domain": "google.com",
     "description": "Search, ads, cloud, devices."},
    {"name": "Tesla", "slug": "tesla", "kind": "both", "domain": "tesla.com",
     "description": "Electric vehicles and energy."},
    {"name": "Spotify", "slug": "spotify", "kind": "both", "domain": "spotify.com",
     "description": "Audio streaming and podcast platform."},
    {"name": "Airbnb", "slug": "airbnb", "kind": "both", "domain": "airbnb.com",
     "description": "Marketplace for short-term lodging."},
    {"name": "GitHub", "slug": "github", "kind": "both", "domain": "github.com",
     "description": "Software collaboration platform owned by Microsoft."},
    {"name": "Figma", "slug": "figma", "kind": "employer", "domain": "figma.com",
     "description": "Collaborative interface design tool."},
    {"name": "Notion", "slug": "notion", "kind": "both", "domain": "notion.so",
     "description": "All-in-one workspace for notes, docs, and projects."},
    {"name": "Vercel", "slug": "vercel", "kind": "both", "domain": "vercel.com",
     "description": "Frontend cloud platform behind Next.js."},
    {"name": "Cloudflare", "slug": "cloudflare", "kind": "both", "domain": "cloudflare.com",
     "description": "Edge network, DDoS protection, developer platform."},
    {"name": "REI", "slug": "rei", "kind": "merchant", "domain": "rei.com",
     "description": "Outdoor co-op retailer."},
    {"name": "Trader Joe's", "slug": "trader-joes", "kind": "both", "domain": "traderjoes.com",
     "description": "Privately held grocery chain."},

    # --- More real, frequently-searched companies ---
    {"name": "Adobe", "slug": "adobe", "kind": "both", "domain": "adobe.com",
     "description": "Creative + document software (Photoshop, Acrobat, etc.)."},
    {"name": "Salesforce", "slug": "salesforce", "kind": "both", "domain": "salesforce.com",
     "description": "Cloud CRM and enterprise software."},
    {"name": "Uber", "slug": "uber", "kind": "both", "domain": "uber.com",
     "description": "Ride-share and delivery platform."},
    {"name": "Walmart", "slug": "walmart", "kind": "both", "domain": "walmart.com",
     "description": "Largest US retailer; physical + online."},
    {"name": "Target", "slug": "target", "kind": "merchant", "domain": "target.com",
     "description": "General merchandise retailer."},
    {"name": "DoorDash", "slug": "doordash", "kind": "both", "domain": "doordash.com",
     "description": "Food delivery marketplace."},
    {"name": "Reddit", "slug": "reddit", "kind": "employer", "domain": "reddit.com",
     "description": "Community-driven discussion platform."},
    {"name": "Slack", "slug": "slack", "kind": "both", "domain": "slack.com",
     "description": "Workplace messaging (Salesforce-owned)."},
    {"name": "Coinbase", "slug": "coinbase", "kind": "both", "domain": "coinbase.com",
     "description": "Cryptocurrency exchange."},
    {"name": "OpenAI", "slug": "openai", "kind": "employer", "domain": "openai.com",
     "description": "AI lab building ChatGPT and the OpenAI API."},
    {"name": "Nvidia", "slug": "nvidia", "kind": "employer", "domain": "nvidia.com",
     "description": "GPUs, AI hardware, and CUDA platform."},
    {"name": "Atlassian", "slug": "atlassian", "kind": "both", "domain": "atlassian.com",
     "description": "Jira, Confluence, Trello, Bitbucket."},

    # --- Scam archetypes (FICTIONAL — clearly-marked demo entities) ---
    {"name": "Acme Phishing Demo Co", "slug": "acme-phishing-demo",
     "kind": "merchant", "domain": "acme-phishing-demo.example",
     "description": "FICTIONAL demo. Archetype: e-commerce non-delivery + follow-up phishing.",
     "is_scam_flagged": True, "scam_severity": 0.88},
    {"name": "ExampleScam Industries Demo", "slug": "examplescam-industries-demo",
     "kind": "merchant", "domain": "examplescam-industries-demo.example",
     "description": "FICTIONAL demo. Archetype: fake investment platform with withdrawal fees.",
     "is_scam_flagged": True, "scam_severity": 0.94},
    {"name": "CryptoMoonGains Demo", "slug": "cryptomoongains-demo",
     "kind": "merchant", "domain": "cryptomoongains-demo.example",
     "description": "FICTIONAL demo. Archetype: pig-butchering crypto romance investment fraud.",
     "is_scam_flagged": True, "scam_severity": 0.97},
    {"name": "SafeTechAssist Demo", "slug": "safetechassist-demo",
     "kind": "merchant", "domain": "safetechassist-demo.example",
     "description": "FICTIONAL demo. Archetype: tech-support / remote-access scam.",
     "is_scam_flagged": True, "scam_severity": 0.86},
    {"name": "FundRecoveryGroup Demo", "slug": "fundrecoverygroup-demo",
     "kind": "merchant", "domain": "fundrecoverygroup-demo.example",
     "description": "FICTIONAL demo. Archetype: 'recovery' scam targeting prior-scam victims.",
     "is_scam_flagged": True, "scam_severity": 0.91},
    {"name": "QuickJobsRemote Demo", "slug": "quickjobsremote-demo",
     "kind": "employer", "domain": "quickjobsremote-demo.example",
     "description": "FICTIONAL demo. Archetype: fake-job-listing scam asking for upfront fees.",
     "is_scam_flagged": True, "scam_severity": 0.79},
    {"name": "DesignerOutletDirect Demo", "slug": "designeroutletdirect-demo",
     "kind": "merchant", "domain": "designeroutletdirect-demo.example",
     "description": "FICTIONAL demo. Archetype: counterfeit luxury-goods drop-ship site.",
     "is_scam_flagged": True, "scam_severity": 0.84},
    {"name": "FreeTrialMax Demo", "slug": "freetrialmax-demo",
     "kind": "merchant", "domain": "freetrialmax-demo.example",
     "description": "FICTIONAL demo. Archetype: subscription-trap free-trial billing.",
     "is_scam_flagged": True, "scam_severity": 0.73},
]


# --------------------------------------------------------------------------- #
# Employment reviews — naturalistic voice, mixed sentiment per company
# --------------------------------------------------------------------------- #

EMPLOYMENT_REVIEWS = [
    # (slug, rating, title, body, department, status)

    # Stripe
    ("stripe", 4.5, "Engineering bar is real but the pace is, too",
     "Three years in. The technical bar in interviews and code review is genuinely high — I've grown faster than at any previous job. Compensation tracks the public bands. Pace expectations are also high and a couple of my old teammates burned out around the 18-month mark. If you protect your weekends and pick a team with a reasonable manager, it's a great place.",
     "Engineering", "current"),
    ("stripe", 4.0, "Documentation culture is unreal",
     "What surprised me joining: nearly every internal system has a written design doc with the why, not just the what. Onboarding is mostly reading. If you like working from primary sources you'll love it.",
     "Infrastructure", "current"),
    ("stripe", 3.4, "Middle management quality varies sharply",
     "Senior IC work was the best of my career here. Two managers later both excellent. The third I worked under made decisions in private and surprised the team in writing. Mileage varies a lot by org.",
     "Engineering", "former"),
    ("stripe", 4.2, "Customer-facing teams move fast",
     "Working in support engineering felt like being plugged directly into the product. Bugs got fixed within days, not quarters. Pace can be intense during big launches.",
     "Support Engineering", "current"),
    ("stripe", 3.8, "Promotions slowed past senior",
     "Coming in mid-level, the first two promos felt earned and well-supported. After senior, the criteria got fuzzier and the wait got longer. Compensation refresh kept up though.",
     "Engineering", "current"),

    # Anthropic
    ("anthropic", 4.8, "Easily the most psychologically safe team I've been on",
     "People share half-baked ideas in open documents and the responses are substantive, not performative. Research engineers and policy folks talk to each other. I've worked at five companies before and have never seen this density of curiosity.",
     "Research", "current"),
    ("anthropic", 4.5, "Mission alignment is real, not posters on a wall",
     "Safety considerations actually shape product decisions in meetings I've sat in. That's rare. The flipside: decisions take longer because you're weighing more dimensions.",
     "Policy", "current"),
    ("anthropic", 4.6, "Onboarding is generous",
     "New hires get paired with senior folks for the first month and there's no rush to ship. The trade-off is everything's still evolving, so 'how do we do X here' sometimes has no answer yet.",
     "Engineering", "current"),
    ("anthropic", 4.0, "Compensation is competitive, not extravagant",
     "Pay is fair for the role and the market. People aren't here for the cash — they're here for the work. If you're optimising for total comp at all costs, FAANG will pay more.",
     "Engineering", "current"),

    # Shopify
    ("shopify", 4.3, "Lots of autonomy if you can stomach the changes",
     "ICs get real decision-making latitude. The downside is the company restructures itself roughly every 18 months — your priorities can shift overnight. I've enjoyed the work, but if you crave stability this isn't it.",
     "Product", "current"),
    ("shopify", 3.9, "Strong engineering culture, slower than it used to be",
     "When I joined four years ago we shipped weekly. Now releases involve more coordination across teams. Still ship fast by industry standards, but the small-company feel is gone.",
     "Engineering", "former"),
    ("shopify", 4.4, "Best merchant-facing PM work I've done",
     "Talking to real shop owners daily and seeing the impact of a feature on their business is rewarding. Lots of trust to run experiments.",
     "Product", "current"),
    ("shopify", 3.2, "Layoffs left a mark",
     "After the 2023 reductions some teams never fully recovered. Surviving people doubled up on workloads. New leadership cohort is rebuilding but it'll take time.",
     "Operations", "former"),
    ("shopify", 4.1, "Remote-first works here",
     "I've been fully remote since day one across three roles. Async docs, written decisions, no surprise 'come back to the office' announcements yet.",
     "Engineering", "current"),

    # Microsoft
    ("microsoft", 4.2, "Steady, predictable, calmer than expected",
     "Coming from a startup, the most jarring thing was how planned everything is. Quarterly check-ins, annual reviews, predictable raises. After the chaos of my last job, that predictability is a feature.",
     "Cloud", "current"),
    ("microsoft", 4.4, "Work-life balance is the real perk",
     "I rarely log in on weekends. PTO is respected. The Satya-era culture is real on my team.",
     "Engineering", "current"),
    ("microsoft", 3.7, "Org politics scale with company size",
     "Cross-team dependencies are slow. To ship anything visible you need three orgs to agree. That's the cost of scale.",
     "Product", "former"),
    ("microsoft", 4.0, "Stock vests are the long game",
     "Initial offer comp looked modest. After four years the refreshers add up. Healthcare and 401k match are top-tier.",
     "Engineering", "current"),
    ("microsoft", 4.3, "Disability accommodations actually work",
     "Asked for ergonomic equipment and flexible hours after surgery. Both handled without friction. Small thing, but it mattered.",
     "Engineering", "current"),

    # Netflix
    ("netflix", 3.8, "Highest autonomy of any role I've had",
     "No approval-chain culture. If you can defend the decision you can make it. The flipside is the keeper-test culture — every quarter you're effectively re-justifying your seat. Not for everyone.",
     "Engineering", "current"),
    ("netflix", 4.4, "Compensation is the actual differentiator",
     "Top of market on base salary. Performance bonus structure simple and transparent. They pay you to stay because they could let you go tomorrow — and that's the deal you signed up for.",
     "Engineering", "current"),
    ("netflix", 3.0, "The keeper test wears on you",
     "Quarterly conversations about whether you'd be missed if you left. Some managers do this well as a development tool. Mine treated it as a stress lever. I lasted 20 months.",
     "Content", "former"),
    ("netflix", 3.6, "No-process culture has costs at scale",
     "Decisions you'd expect a doc or RFC for happen in 1:1s and Slack threads. Faster, but tribal knowledge piles up.",
     "Engineering", "former"),

    # Amazon
    ("amazon", 3.5, "Varies sharply by team — research yours",
     "I had two stints at Amazon. First team: brilliant, supportive, growth-focused. Second team after an internal transfer: stack-rank pressure, weekly metric reviews, terrible. Same company, different worlds. Ask specific questions in interviews.",
     "Engineering", "current"),
    ("amazon", 2.8, "Forced curve cost us good people",
     "Annual review forces a percentage into LP categories regardless of actual performance. Watched two people on my team get coached out who were performing fine.",
     "Engineering", "former"),
    ("amazon", 3.9, "AWS comp + scope is hard to beat",
     "If you're an infra engineer and you survive the first year, the resume bump is real. The PIP risk is real too.",
     "AWS", "former"),
    ("amazon", 3.2, "Customer obsession isn't marketing",
     "The 'work backwards from the customer' principle actually shapes meetings. The PR/FAQ doc exercise feels silly at first then becomes second nature.",
     "Product", "current"),

    # Google
    ("google", 4.0, "Still the gold standard for perks",
     "Free food, transit, on-site doctor, gym. People will tell you the perks aren't worth it without the impact — but I disagree. Coming from a 2-person startup, the infrastructure feels luxurious.",
     "Engineering", "current"),
    ("google", 3.4, "Project velocity has slowed noticeably",
     "Five years in. I used to ship to billions of users in a quarter. Now I spend more cycles in alignment meetings than coding. Strong work-life balance is the trade-off.",
     "Engineering", "current"),
    ("google", 3.7, "Promotion process is opaque past L5",
     "L3 to L5 was clear-eyed. L5 to L6 took 3 cycles and I still don't fully understand the criteria. Comp grows regardless because of stock.",
     "Engineering", "former"),
    ("google", 4.1, "Internal mobility actually works",
     "Switched orgs three times in five years. Each move was supported. Not many places where that's true.",
     "Engineering", "current"),

    # Tesla
    ("tesla", 3.0, "Mission inspiring, hours unsustainable",
     "Joined for the EV mission, stayed because the work was technically interesting. Left because 60-hour weeks became 75-hour weeks and the company stopped pretending that was unusual.",
     "Engineering", "former"),
    ("tesla", 3.6, "Pace + scope you won't find elsewhere",
     "Where else does a hardware/software stack ship to a million people in a quarter? The intensity is the cost of admission. Worth it for two years, not five.",
     "Engineering", "former"),
    ("tesla", 2.2, "Service team is overworked",
     "If you work in service centers, expect to be on your feet 10+ hours, mandatory weekends during deliveries, and not enough techs for the volume.",
     "Service", "former"),
    ("tesla", 3.8, "Software org has its own culture",
     "Inside software it's calmer than the factory side. Still intense, but managers protected the team during crunch.",
     "Software", "current"),

    # Spotify
    ("spotify", 4.1, "Squad model still mostly works",
     "Squads, tribes, chapters. The autonomy is real. The downside is duplicated effort across squads. Net positive for me as an IC.",
     "Engineering", "current"),
    ("spotify", 3.8, "Stockholm + remote balance is great if you live in Sweden",
     "Lots of Nordic-style policies — generous parental leave, predictable hours. As a US remote employee some of those benefits don't translate directly.",
     "Engineering", "current"),
    ("spotify", 4.2, "Music data scale is unique",
     "If you want to work on personalisation at hundreds of millions of users, there are maybe three companies in the world to do it at. This is one of them.",
     "Engineering", "current"),

    # Airbnb
    ("airbnb", 3.9, "Live-and-work-anywhere has stuck",
     "Two and a half years on. They actually mean it — I've worked from 8 countries. Tax setup is on you and gets complex.",
     "Engineering", "current"),
    ("airbnb", 4.0, "Design rigor across functions",
     "Even engineering reviews include design feedback. PMs sketch wireframes. The cross-functional fluency is rare.",
     "Engineering", "current"),
    ("airbnb", 3.6, "Layoffs in 2020 are still talked about",
     "The way Brian handled them — public, generous severance, alumni network — set a tone. But surviving teams carried extra load for a long time.",
     "Operations", "former"),

    # GitHub
    ("github", 4.2, "Async-first really is async-first",
     "Issues, PRs, decisions in the open. Almost no synchronous meetings. As a parent on a different time zone from my team, this is the only setup that's worked for me.",
     "Engineering", "current"),
    ("github", 4.0, "Microsoft ownership is light-touch",
     "Five years post-acquisition. Compensation aligned to Microsoft bands. Day-to-day culture still feels independent.",
     "Engineering", "current"),
    ("github", 4.4, "Copilot work is a privilege",
     "Working on developer-AI tooling that millions use daily. Hard to find a higher-leverage IC role.",
     "Engineering", "current"),

    # Figma
    ("figma", 4.5, "Design-engineering balance is unusually healthy",
     "I'm an engineer and I work shoulder-to-shoulder with designers daily. PR reviews include UX feedback. That's the company's superpower.",
     "Engineering", "current"),
    ("figma", 4.3, "Acquisition limbo was tense but resolved",
     "The Adobe deal's collapse was a wild year. People stayed because the work and pay both held up.",
     "Engineering", "current"),
    ("figma", 4.0, "Small-company feel scaling well",
     "We're past 1000 people and it still feels coordinated. Q&A still has real questions answered honestly.",
     "Design", "current"),

    # Notion
    ("notion", 4.1, "Product-engineering pairing is tight",
     "PRs include product feedback from PMs. Decisions go fast. Some debt is starting to show in older areas of the app.",
     "Engineering", "current"),
    ("notion", 3.8, "Hypergrowth means missing process",
     "Three years in. The org has 5x'd. We're still figuring out things like consistent levelling. Comp refresh is generous to keep up.",
     "Product", "current"),
    ("notion", 4.3, "Customer obsession that's genuine",
     "I've sat in three customer interviews this month as an engineer. Every quarter that intensifies. You feel where the product hurts.",
     "Engineering", "current"),

    # Vercel
    ("vercel", 4.4, "DX is the company's actual culture",
     "Engineering builds and uses the platform constantly. The dogfooding is real. Bugs get found because we hit them on our own dashboards first.",
     "Engineering", "current"),
    ("vercel", 4.2, "Async + small team density",
     "Sub-500-people feel even as we've grown. Decisions made in Discord channels. Faster than any company I've worked at.",
     "Engineering", "current"),
    ("vercel", 3.9, "On-call cadence is real",
     "Edge platform means real-world incidents. On-call is well-supported but it does come around regularly.",
     "Engineering", "current"),

    # Patagonia (also an employer)
    ("patagonia", 4.6, "Mission alignment isn't a slogan here",
     "Worked at the Ventura HQ for two years. Environmental initiatives are real budget items, not marketing. Pay is below tech but well above retail. Surf-during-lunch is real if the waves are good.",
     "HQ", "current"),
    ("patagonia", 4.4, "Retail floor is the best floor I've worked",
     "Store associates are paid well above retail average, schedules are predictable, and the discount lets you actually own the gear. Big difference from my old big-box retail job.",
     "Retail", "current"),
    ("patagonia", 4.0, "Comp lower than tech, balance higher",
     "Coming from a mid-size SaaS, my base dropped about 15%. The trade-off was real PTO, hard stops on hours, and a manager who actually used the time off too.",
     "Engineering", "former"),
    ("patagonia", 4.2, "1% for the Planet is real",
     "The corporate-citizenship work isn't a side project. Watched leadership push back on a profitable but environmentally bad partnership. They walked.",
     "Sustainability", "current"),

    # Apple (also an employer)
    ("apple", 4.0, "Secrecy culture is exactly what you'd expect",
     "Three years in software engineering. Compartmentalisation is real — you often don't know what the team next to you is shipping. Trade-off is the privacy of being able to focus on your actual project.",
     "Engineering", "current"),
    ("apple", 3.6, "Hardware org runs hot during product cycles",
     "Pre-event crunch is intense. Post-event the calm doesn't fully return because the next product's already in motion. Compensation reflects the pace.",
     "Hardware", "former"),
    ("apple", 4.3, "Best benefits I've encountered",
     "Healthcare, ESPP, retirement match, and the on-campus amenities. The intangible — free coffee aside — was the medical staff for ergonomic issues.",
     "Engineering", "current"),
    ("apple", 3.8, "Promotion ladders are narrow at senior levels",
     "Levels exist but the cohort sizes shrink fast above ICT5. Patience and visibility on cross-team projects matter as much as raw output.",
     "Engineering", "current"),
    ("apple", 4.1, "Internal mobility worked for me",
     "Switched orgs from services to hardware engineering after two years. Process took a quarter but the receiving team rolled out the welcome mat.",
     "Engineering", "current"),

    # Trader Joe's (also an employer)
    ("trader-joes", 4.5, "Pay + bennies > regional grocery competitors",
     "Crew Member starting wage above the regional average. Quarterly raises if you're hitting the bar. Healthcare for part-timers is unusual in the industry.",
     "Crew (retail)", "current"),
    ("trader-joes", 4.4, "Promotion path is real",
     "Started as Crew, made Mate in 14 months, Captain track is open. The internal mobility is the headline benefit they don't advertise enough.",
     "Crew → Mate", "current"),
    ("trader-joes", 4.0, "Customer interactions are the actual job",
     "If you don't like chatting with customers, this isn't the gig. The conversation density is the differentiator. Some shifts are wonderful, some are exhausting.",
     "Crew (retail)", "former"),
    ("trader-joes", 4.2, "Schedules are predictable",
     "Posted two weeks in advance. Manager actually respects time-off requests. Compared to my last grocery job, night-and-day.",
     "Crew (retail)", "current"),

    # Adobe
    ("adobe", 3.8, "Big-co stability, slower velocity",
     "Came from a startup. The infrastructure here is enormous, decisions take longer, but the headcount means real cross-team support exists. Healthcare + 401k are top of the industry.",
     "Engineering", "current"),
    ("adobe", 3.5, "Acrobat side feels different from Creative Cloud",
     "I work in document cloud. Pace and culture are noticeably different from the Creative Cloud teams I rotated through. Worth interviewing across multiple orgs.",
     "Product", "current"),
    ("adobe", 4.0, "Sabbaticals are real",
     "Took a 4-week sabbatical at the 5-year mark. Came back to my team intact. Few public companies actually honor this benefit.",
     "Engineering", "current"),
    ("adobe", 3.4, "Cloud transition stress lingered for years",
     "Going from boxed software to cloud was disruptive across the company. Stabilized around 2020, but some teams still carry the org scars.",
     "Engineering", "former"),

    # Salesforce
    ("salesforce", 3.7, "V2MOM is actually used here",
     "The vision/values/methods/obstacles/measures framework isn't theater — managers genuinely use it. Once you get past the corporate-speak it's a useful planning tool.",
     "Engineering", "current"),
    ("salesforce", 3.3, "Sales-heavy culture if you're in engineering",
     "Strong sales-first mindset means engineering priorities track quarterly revenue. Good if you like business proximity; jarring if you want pure tech focus.",
     "Engineering", "former"),
    ("salesforce", 4.1, "Trailhead culture is real",
     "Self-learning paths and certifications are encouraged on the clock. The ladders to product manager + solutions engineer roles internally are well-mapped.",
     "Product", "current"),
    ("salesforce", 3.6, "Slack acquisition went well day-to-day",
     "Slack stayed somewhat autonomous post-acquisition. Engineering tooling didn't get force-migrated to Salesforce's stack the way I feared.",
     "Engineering", "current"),

    # Uber
    ("uber", 3.4, "Pace + scope are unmatched for the comp band",
     "I spent 2.5 years on the rider side. The pace was relentless but the problems were genuinely interesting. Comp climbed quickly through the levels.",
     "Engineering", "former"),
    ("uber", 3.2, "Performance management is intense",
     "Quarterly calibrations, ranking discussions, and managers who don't always protect their reports. Got promoted twice; left because the politics were exhausting.",
     "Engineering", "former"),
    ("uber", 3.6, "Driver-platform teams have purpose",
     "Building the side of the product drivers use means immediate feedback. Drivers tell you exactly what's broken in app reviews and support tickets.",
     "Engineering", "current"),
    ("uber", 3.8, "Eats teams are smaller and faster",
     "Inside Uber, Eats is its own animal — smaller team, more autonomy. Worth knowing in interviews if you'd prefer that environment.",
     "Engineering", "current"),

    # Walmart
    ("walmart", 3.6, "Walmart Labs in Bentonville vs Sunnyvale is two cultures",
     "Worked in both offices. Sunnyvale is closer to tech-company norms; Bentonville is closer to corporate Walmart. Choose accordingly.",
     "Engineering", "current"),
    ("walmart", 3.4, "Scale is the real headline",
     "Building anything for Walmart means it touches a meaningful percentage of US households. That weight makes mistakes expensive and decisions slower.",
     "Engineering", "current"),
    ("walmart", 3.9, "Benefits + pay better than I expected",
     "Equity grants for engineers are real and well above my old SaaS. Healthcare + 401k match are corporate-class.",
     "Engineering", "current"),

    # DoorDash
    ("doordash", 3.5, "Operational pace is intense",
     "Marketplace work means real-world incidents during dinner rush every night. On-call is real. Comp reflects it.",
     "Engineering", "current"),
    ("doordash", 3.7, "Lots of growth opportunities for ICs",
     "Three promotions in four years. The company growth makes that easier to engineer than at a flat-growth company.",
     "Engineering", "former"),
    ("doordash", 3.0, "Operations side is grueling",
     "If you're in the corporate ops or finance teams, the cross-functional load during peak quarters can be unsustainable.",
     "Operations", "former"),

    # Reddit
    ("reddit", 4.0, "Smaller eng org than people realize",
     "The product reaches hundreds of millions but the engineering team is in the low thousands. Means ICs touch high-impact systems quickly.",
     "Engineering", "current"),
    ("reddit", 3.8, "IPO transition went smoother than expected",
     "Survived the IPO without the typical bloat or culture shock. Equity refresh post-IPO was generous.",
     "Engineering", "current"),
    ("reddit", 4.1, "Mod relations are interesting work",
     "Building tooling that thousands of volunteer moderators rely on is a different kind of engineering problem. Customer empathy required.",
     "Engineering", "current"),

    # Slack (post-Salesforce)
    ("slack", 4.0, "Distinct culture from parent",
     "Worked through the acquisition. The Slack culture has been mostly preserved. Some Salesforce processes have crept in but not enough to change the day-to-day.",
     "Engineering", "current"),
    ("slack", 3.8, "Product velocity slowed post-acquisition",
     "Less shipping cadence than pre-acquisition. The trade-off is more enterprise polish.",
     "Engineering", "former"),
    ("slack", 4.2, "Distributed-first done well",
     "Genuinely async, with rituals around documenting decisions. Easy to be a fully remote employee.",
     "Engineering", "current"),

    # Coinbase
    ("coinbase", 3.5, "Mission-aligned hires fare best",
     "If you're crypto-curious or crypto-skeptical, you'll struggle. Engineers who genuinely care about the financial-infrastructure mission stay longest.",
     "Engineering", "current"),
    ("coinbase", 3.0, "Crypto-winter layoffs left scars",
     "Survived the 2022 layoffs. Surviving teams carried bigger loads, and trust in long-term planning took a hit.",
     "Engineering", "current"),
    ("coinbase", 3.7, "Regulatory work is fascinating if you like it",
     "Compliance + crypto law is a learning curve but genuinely interesting. The legal team is one of the strongest in tech.",
     "Compliance", "former"),

    # OpenAI
    ("openai", 4.4, "Research + product blend works",
     "Coming from a pure-research lab and a pure-product company, OpenAI is the first place I've seen both work in the same room without dysfunction.",
     "Research", "current"),
    ("openai", 4.0, "Pace is intense but mission-aligned",
     "Working hours are real. The pace is driven by the team caring, not by mandates. Compensation reflects the demand.",
     "Engineering", "current"),
    ("openai", 4.2, "Equity grants are unique",
     "The PPU structure is different from standard tech equity. Read your offer carefully — there are nuances around liquidity.",
     "Engineering", "current"),

    # Nvidia
    ("nvidia", 4.3, "AI tailwind plus stable culture",
     "Long-tenured engineers, well-defined ladders, and the GPU boom delivering equity gains few companies can match in this cycle.",
     "Engineering", "current"),
    ("nvidia", 4.1, "Driver-team work is unique",
     "If you work on the graphics or CUDA driver, you're touching software that millions of developers and gamers depend on daily. Few comparable scopes.",
     "Engineering", "current"),
    ("nvidia", 3.8, "Process-heavy by tech-company standards",
     "Hardware-company DNA shows. More reviews, more sign-offs. Worth knowing if you came from a fast-shipping startup.",
     "Engineering", "current"),

    # Atlassian
    ("atlassian", 4.0, "Open Company, No Bullshit is mostly real",
     "Internal docs are genuinely public to all employees. Some decisions still happen in Slack DMs, but the default-open culture is observable.",
     "Engineering", "current"),
    ("atlassian", 3.9, "ShipIt days produce real products",
     "Quarterly 24-hour hackathons aren't theater — Confluence Whiteboards came from one. ICs can ship things they want to ship.",
     "Engineering", "current"),
    ("atlassian", 3.7, "Sydney HQ matters less than it did",
     "Distributed work has equalized US and AU offices. Career growth from the US is no longer second-tier the way it used to be.",
     "Product", "current"),

    # More on existing companies — broaden the catalog
    ("anthropic", 4.5, "Hiring bar feels intentional",
     "Interview process is rigorous but the questions are calibrated to the work. Felt respected throughout — no trick puzzles, no time-pressure ego plays.",
     "Engineering", "current"),
    ("anthropic", 4.7, "Compute access is the underrated benefit",
     "If you're doing AI research, the difference between abundant compute and rationed compute is the difference between exploring ideas and writing memos about ideas.",
     "Research", "current"),
    ("microsoft", 4.0, "Internal mobility is the long-term value",
     "Switched between Azure, Office, and Bing-era search in seven years. Few public companies make moves like that this frictionless.",
     "Engineering", "current"),
    ("stripe", 4.3, "Customer-team rotations are smart",
     "New hires rotate through support for the first month. By week 4 you've answered live customer questions about parts of the product you'll later build.",
     "Engineering", "current"),
    ("google", 3.6, "Bureaucracy grew faster than impact",
     "Eight years in. The first four felt high-leverage. The last four have been more meetings, more reviews, more reorgs. Comp keeps me, not the work.",
     "Engineering", "current"),
    ("amazon", 4.0, "AWS work-life balance is bimodal",
     "Some AWS teams have great balance. Others (mostly the newer services chasing GA) are brutal. Ask specifically in your team-matching call.",
     "AWS", "current"),
    ("tesla", 3.4, "Software side is the calmer side",
     "If you join Tesla as a software engineer (not hardware/manufacturing), expect intensity but not factory-floor levels.",
     "Software", "current"),

    # Cloudflare
    ("cloudflare", 4.0, "Big tech infra problems, mid-size company feel",
     "Daily traffic numbers I'd never see at a smaller place. Decision-making still feels relatively un-bureaucratic compared to the FAANGs.",
     "Engineering", "current"),
    ("cloudflare", 3.8, "Comp is below FAANG but mission is clear",
     "Pay is competitive but won't beat Meta or Google. Mission and tech are what you're trading for. Worth it for me.",
     "Engineering", "current"),
    ("cloudflare", 4.2, "Innovation Weeks deliver real product",
     "The all-hands launch weeks aren't theatre. Things I built in a hack week shipped to GA the following quarter.",
     "Engineering", "current"),
]


# --------------------------------------------------------------------------- #
# Shopping reviews — varied voice
# --------------------------------------------------------------------------- #

SHOPPING_REVIEWS = [
    # (slug, rating, title, body, product_or_service, purchase_amount)

    # Patagonia
    ("patagonia", 4.9, "Sent in a six-year-old jacket. Repaired for free.",
     "Down Sweater zipper failed after six winters. Mailed it in, got it back two weeks later, repaired, no charge, no friction. The Ironclad Guarantee is what they say it is.",
     "Down Sweater", 280.0),
    ("patagonia", 4.7, "Worn Wear is underrated",
     "Bought a used Nano Puff through their secondhand site for half retail. Came clean, no smell, no holes. Will keep shopping used there.",
     "Worn Wear Nano Puff", 120.0),
    ("patagonia", 4.5, "Sizing runs slim",
     "Fit advice on the site is accurate. If you're between sizes, size up. The active-fit cuts are sharply tapered.",
     "Houdini windbreaker", 99.0),
    ("patagonia", 3.9, "Not cheap, never claims to be",
     "I paid $400 for a shell. Three years on, no failures, but if you're price-sensitive look at REI Co-op brand or used.",
     "Triolet jacket", 399.0),
    ("patagonia", 4.6, "Surf line is real",
     "Boardshort quality is way above what I expected from a brand most people associate with mountains.",
     "Boardshorts", 65.0),

    # Costco
    ("costco", 4.6, "Membership pays for itself if you have a household",
     "Family of four. The Kirkland staples plus three gas fillups a month more than cover the $130. Returns policy is the real hidden value.",
     "Executive Membership", 130.0),
    ("costco", 4.4, "Returned a 4-year-old vacuum",
     "Stopped working, brought it back with the receipt I found in the email archive, got store credit. No hassle. People aren't lying about the return policy.",
     "Shark vacuum return", 0.0),
    ("costco", 4.0, "Kirkland is consistently good, sometimes great",
     "Their olive oil is better than what I was paying twice as much for at Whole Foods. The bourbon depends on the batch — 2024 was rough.",
     "Kirkland house brand", 50.0),
    ("costco", 3.6, "Lines at peak are brutal",
     "Saturday afternoon is unusable. Tuesday at 11am, empty. Plan accordingly.",
     "Weekly run", 250.0),
    ("costco", 4.5, "Hot dog combo is sacred",
     "Still $1.50. They've said it stays. I believe them.",
     "Food court", 1.50),

    # Apple
    ("apple", 4.2, "Genius Bar saved me",
     "Logic board died out of warranty. Brought it in expecting bad news. Tech transferred my data and offered a refurb upgrade for less than a logic-board swap. Walked out happy.",
     "MacBook Air repair", 800.0),
    ("apple", 3.5, "Online support routing is rough",
     "Three chats, two phone calls, finally got to someone who could help. In-store was 5 minutes by comparison.",
     "iPhone activation issue", 0.0),
    ("apple", 4.4, "Accessory pricing is the only sin",
     "$80 cleaning cloth aside, the actual products do what they're supposed to.",
     "Magic Keyboard", 99.0),
    ("apple", 4.0, "AppleCare worth it for laptops",
     "Battery swap covered. Without the plan that's a $200 repair.",
     "AppleCare+ Mac", 199.0),
    ("apple", 3.8, "Buy refurb",
     "Apple's refurbished store is genuinely good — full warranty, factory-tested. 15% off without quality loss.",
     "Refurbished iPad", 449.0),

    # Amazon
    ("amazon", 3.8, "Prime is fine for first-party items",
     "First-party Amazon shipments arrive on time and arrive correctly. Third-party seller variance is the constant gotcha.",
     "Prime Membership", 139.0),
    ("amazon", 2.4, "Got a counterfeit charger",
     "Listed as Anker. Shipped from third-party. Obvious knockoff. Refunded after disputing, but the trust hit lingers.",
     "Anker charger", 18.50),
    ("amazon", 3.9, "Returns are still easy",
     "Drop at Kohl's, no box. 5-minute process. Refund in 48 hours.",
     "Apparel return", 0.0),
    ("amazon", 3.2, "Reviews are increasingly unreliable",
     "Hundreds of 5-stars with similar phrasings. I cross-reference with Fakespot before buying anything over $50.",
     "Misc household", 80.0),
    ("amazon", 4.0, "AmazonBasics quality is decent",
     "Their cables, batteries, and basics generally meet spec at lower prices than name brands.",
     "AmazonBasics cables", 15.0),

    # Shopify (merchant side)
    ("shopify", 4.3, "Best entry-point for first-time merchants",
     "Set up a store in two days. Themes look polished out of the box. The app marketplace solves most edge cases.",
     "Shopify Basic plan", 39.0),
    ("shopify", 3.7, "Transaction fees stack up at scale",
     "Once we crossed ~$30k MRR, the 2% Shopify Payments fee plus app subscriptions started really biting. Migrated to Shopify Plus eventually.",
     "Shopify Plus", 2000.0),
    ("shopify", 4.0, "Support is responsive",
     "Live chat got me unblocked at 11pm on a Saturday. Not always the case for SaaS at this price point.",
     "Shopify support", 0.0),

    # Tesla
    ("tesla", 3.4, "Car: great. Service: depends on your region.",
     "Model 3 drives beautifully. Software updates feel like getting a new car every quarter. But service appointments where I live (Phoenix) take two months. Friends in the Bay Area have it the next day.",
     "Model 3", 42000.0),
    ("tesla", 3.0, "Build quality variance",
     "First Model Y had panel gaps. Tesla swapped it under warranty after three trips. Second one has been perfect.",
     "Model Y", 49990.0),
    ("tesla", 4.1, "Supercharger network is the real moat",
     "Roadtripped from LA to Seattle in five days. Never anxious about charging. Other EV networks are getting better but not yet on par.",
     "Supercharging", 0.0),
    ("tesla", 2.8, "Pricing changes shake confidence",
     "Bought during a $5k price drop, then prices dropped again two weeks later. They don't do anything about that. Not great for buyer trust.",
     "Pricing experience", 0.0),

    # Spotify
    ("spotify", 4.0, "Catalog and discovery still best in class",
     "Daily Mix has been right more often than wrong for years. The only thing that consistently introduces me to music I'd never search for.",
     "Premium Individual", 11.99),
    ("spotify", 3.5, "Ad-supported tier got more aggressive",
     "Free tier is borderline unusable now. Pre-roll and mid-roll combo.",
     "Free tier", 0.0),
    ("spotify", 3.9, "Family plan is the best value",
     "Six accounts, $20/month. Splitting that with parents makes it $3 each.",
     "Family plan", 19.99),

    # Airbnb
    ("airbnb", 3.4, "Quality depends entirely on host",
     "Five stays this year. Two were excellent, two were okay, one was a disaster (listed AC didn't work in July). Filtering by Superhost status helps but isn't a guarantee.",
     "Stays (5)", 1800.0),
    ("airbnb", 3.0, "Cleaning fees still out of control",
     "$280 cleaning fee on a 2-night stay. The 'final price' transparency push helped, but the underlying fees haven't dropped.",
     "Stay (2 nights)", 480.0),
    ("airbnb", 4.2, "Customer support reimbursed me for the bad one",
     "When the AC unit was broken in 95-degree heat, I filed and got a full refund within 36 hours. They did right by me.",
     "Refund experience", 0.0),

    # GitHub
    ("github", 4.6, "Copilot productivity bump is measurable",
     "I tracked PRs per week for six weeks before and after. ~25% faster on routine work. Diminishes for complex architecture work.",
     "Copilot Individual", 10.0),
    ("github", 4.2, "Free tier is generous",
     "Public repos, unlimited collaborators, free Actions minutes for OSS. The free tier alone could be a paid product.",
     "Free plan", 0.0),
    ("github", 4.5, "Enterprise SSO worth it",
     "If your org is over 50 engineers, the SAML + audit log features in Enterprise are worth the price jump.",
     "Enterprise", 21.0),

    # Notion (also a merchant — the SaaS product)
    ("notion", 4.4, "Team plan is the actual unlock",
     "Used Notion as a solo for years on the free plan. Bumped to Team last quarter for a 6-person company and the version-history + granular sharing alone paid for it.",
     "Notion Team plan", 10.0),
    ("notion", 3.9, "Slow on really big workspaces",
     "Past about 500 pages with deep nesting, navigation gets sluggish. Mobile feels every database query. They're working on it.",
     "Notion Personal", 0.0),
    ("notion", 4.2, "AI add-on grew on me",
     "Skeptical at first. Now I use it for summarising long pages, generating outlines from notes, and cleaning up rough drafts. Not transformative — but useful.",
     "Notion AI add-on", 10.0),
    ("notion", 4.0, "Sync is reliable now",
     "Used to get conflicts and stale clients. Past 18 months I haven't lost anything. Big improvement.",
     "Notion Personal Pro", 5.0),

    # Adobe (shopping side — Creative Cloud / Acrobat)
    ("adobe", 3.6, "Creative Cloud subscription costs add up",
     "Photoshop + Illustrator + Premiere is $60/month. As an individual, it's the highest software bill on my card. Worth it because there's no real alternative for production work.",
     "Creative Cloud All Apps", 59.99),
    ("adobe", 3.0, "Cancellation friction is real",
     "Cancelling mid-cycle hits you with an early-termination fee. Read the contract carefully on the annual plan.",
     "Cancellation experience", 0.0),
    ("adobe", 4.1, "Acrobat Pro DC is still the standard",
     "PDF editing, signing, and form filling. There are cheaper alternatives but Acrobat is what every legal + corporate workflow expects.",
     "Acrobat Pro DC", 14.99),
    ("adobe", 4.0, "Express has gotten genuinely good",
     "The free tier of Express is a useful Canva alternative. Worth trying before subscribing to the full Creative Cloud.",
     "Adobe Express (free)", 0.0),

    # Salesforce (shopping side — CRM software)
    ("salesforce", 3.6, "Powerful but the learning curve is real",
     "Three months to onboard a 5-person sales team. Once they got past it, productivity jumped. Without dedicated admin support, expect chaos.",
     "Sales Cloud Enterprise", 0.0),
    ("salesforce", 3.2, "Per-seat pricing scales fast",
     "Once you're past 25 users, the bill is significant. Add-ons (Pardot, CPQ) accelerate that.",
     "Sales Cloud + Pardot", 0.0),
    ("salesforce", 3.8, "Trailhead is the secret weapon",
     "Free self-training on real product features. Reduced our consulting spend by 60%.",
     "Trailhead training", 0.0),

    # Uber (rider/eater side)
    ("uber", 3.5, "Pricing surge is frustrating",
     "Late-night surge hits 2-3x base. Lyft tends to be slightly cheaper but Uber wins on coverage in most cities.",
     "Ride history (12 mo)", 600.0),
    ("uber", 3.8, "Uber One isn't worth it unless you Eats a lot",
     "$9.99/month for free delivery on Eats + ride discounts. Only pencils out if you order delivery 3+ times a month.",
     "Uber One subscription", 119.88),
    ("uber", 3.3, "Driver app changes affect rider experience",
     "Lots of new drivers in my city. Quality is lower than 5 years ago when I started using it.",
     "Recent rides", 0.0),

    # Walmart
    ("walmart", 3.7, "Walmart+ membership beats Amazon in groceries",
     "Free delivery + fuel discounts. As a non-Amazon-loyal household, this is the better all-around membership.",
     "Walmart+ subscription", 98.0),
    ("walmart", 3.4, "Marketplace sellers are mixed",
     "Walmart-fulfilled is fine. Third-party Marketplace items are hit-or-miss similar to Amazon's challenge.",
     "Marketplace order", 60.0),
    ("walmart", 3.9, "Pickup is the killer feature",
     "Order on the app, pick up curbside in 1-2 hours. Less expensive than instacart for the same convenience.",
     "Grocery pickup (weekly)", 150.0),

    # Target
    ("target", 4.2, "Same-day Shipt experience is solid",
     "Membership-bundled Same-Day delivery via Shipt has been more reliable than its competitors in my zip.",
     "Target Circle 360", 99.0),
    ("target", 4.3, "Brand collaborations consistently deliver",
     "Up & Up house brand is excellent value. Brand collabs (Joanna Gaines, etc.) hit a good quality/price point.",
     "Various household", 80.0),
    ("target", 3.8, "App + store integration works",
     "Drive Up is genuinely faster than going inside for most quick errands. App reservations work as advertised.",
     "Drive Up pickups", 0.0),

    # DoorDash
    ("doordash", 3.2, "Fees stack up quickly",
     "Service fee + delivery fee + driver tip + small-order fee + 1.99 expanded-range fee. A $20 burrito ends up being $35.",
     "Order history", 250.0),
    ("doordash", 3.6, "DashPass + restaurant deals make it work",
     "$10/month membership is worth it if you order weekly. Many restaurants offer DashPass-only discounts.",
     "DashPass annual", 96.0),
    ("doordash", 3.0, "Order accuracy depends on the restaurant",
     "Items missing or wrong about 1 in 8 orders. DoorDash refund policy is fair when this happens but the time cost is annoying.",
     "Refund experience", 25.0),

    # Slack (paid plans)
    ("slack", 4.2, "Pro plan is the right starting point",
     "Free tier message-retention limit is the actual constraint. Pro plan removes it and unlocks message history search, which is the real product.",
     "Slack Pro", 7.25),
    ("slack", 4.0, "Enterprise Grid for larger orgs",
     "Multi-workspace federation, EKM, audit logs. If you're past ~500 employees, the upgrade is real value.",
     "Enterprise Grid", 0.0),

    # Coinbase
    ("coinbase", 3.2, "Trading fees are higher than alternatives",
     "Standard fee schedule is significantly higher than Kraken or Gemini. Coinbase One subscription reduces but doesn't eliminate.",
     "Trading", 0.0),
    ("coinbase", 4.0, "Custody + security reputation earned",
     "Despite the fee gripe, Coinbase has avoided the catastrophic failures other exchanges hit. That insurance has value.",
     "Wallet + security", 0.0),
    ("coinbase", 3.5, "USDC integration is the killer feature",
     "Native USDC support + no-fee conversions for some pairs. Tax-software integration (CoinTracker, etc.) is well-supported.",
     "USDC + reporting", 0.0),

    # Nvidia (consumer GPU)
    ("nvidia", 3.6, "RTX prices have stabilized but inventory is still spotty",
     "Bought a 4080 at MSRP after 6 months of waiting. Performance is excellent; supply chain is still recovering.",
     "GeForce RTX 4080", 1199.0),
    ("nvidia", 4.4, "CUDA + drivers for ML work are unmatched",
     "Compared to AMD ROCm, the CUDA ecosystem is years ahead for ML. If you're training models locally, NVIDIA + Linux is the only realistic stack.",
     "RTX 4090 + CUDA", 1599.0),

    # Atlassian (products)
    ("atlassian", 3.6, "Jira is powerful and overcomplicated",
     "Powerful workflow engine; default UI overwhelms small teams. Linear ate their lunch in this segment for a reason.",
     "Jira Software Cloud", 7.75),
    ("atlassian", 4.2, "Confluence is the strong product",
     "If Jira gets the criticism, Confluence quietly does its job. Internal-wiki use case fits well at any team size.",
     "Confluence Standard", 5.75),
    ("atlassian", 4.0, "Trello is still good for simple boards",
     "If your team rejects Jira's complexity, Trello is the right downgrade — free tier covers most teams.",
     "Trello Free", 0.0),

    # REI
    ("rei", 4.5, "Co-op return policy is real",
     "One-year window. Used my hiking boots for 9 months, hurt my feet on a long trip, returned them, got store credit. They didn't even ask why.",
     "Hiking boots", 160.0),
    ("rei", 4.6, "Staff actually know the products",
     "Asked about backpack fit for a 5-day trip. The associate ran me through three packs, weighed them, demoed the hip belt adjustment. 40 minutes of attention on a $300 purchase.",
     "Osprey pack fitting", 320.0),
    ("rei", 4.2, "Member dividend adds up",
     "10% annual dividend on regular-price purchases. Last year I got back $120. Effectively a discount, but you have to remember to spend it.",
     "Annual dividend", 120.0),
    ("rei", 3.8, "Higher prices than Amazon",
     "REI is rarely the cheapest. You're paying for in-store expertise and the return policy. Whether that's worth it depends on the purchase.",
     "Tent comparison shop", 0.0),

    # Trader Joe's
    ("trader-joes", 4.4, "House brands consistently good",
     "Probably 80% of what I buy is private label. Frozen Indian dishes, dark chocolate peanut butter cups, mandarin chicken. Quality vs price ratio is unbeaten.",
     "Frozen meals (weekly)", 30.0),
    ("trader-joes", 4.6, "Checkout interaction is the brand",
     "Cashiers actually talk to you. It's a small thing, but going to Trader Joe's vs a Whole Foods self-checkout feels like a different category of activity.",
     "Weekly groceries", 90.0),
    ("trader-joes", 3.8, "Inventory turnover is fast",
     "Products you love can disappear. I've had three favorite items discontinued this year. Buy in bulk when you find a winner.",
     "Discontinued items", 0.0),

    # Vercel
    ("vercel", 4.5, "Deployment speed is the headline",
     "Push to main, deployed globally in 60 seconds. The DX hasn't been matched yet.",
     "Pro plan", 20.0),
    ("vercel", 4.0, "Pricing past hobby tier matters",
     "Free tier is generous. Pro tier scales fast — keep an eye on bandwidth and function invocations if you have a viral moment.",
     "Function overage", 80.0),
    ("vercel", 4.4, "AI Gateway is underrated",
     "Switched from per-provider SDKs to the Gateway last quarter. Fallbacks and usage analytics in one place.",
     "AI Gateway", 0.0),

    # Cloudflare
    ("cloudflare", 4.7, "Free tier is what hooked me",
     "DDoS protection on a free CDN was unheard of when they launched. Still the best free tier in infra.",
     "Free plan", 0.0),
    ("cloudflare", 4.3, "Workers are productive for small projects",
     "Built a side project on Workers in a weekend. Free tier handled the launch traffic.",
     "Workers Paid plan", 5.0),
    ("cloudflare", 4.0, "Enterprise pricing is opaque",
     "If you're in the >$30k/yr range you'll be in a sales process. Not a complaint, just expectation-setting.",
     "Enterprise plan", 0.0),
]


# --------------------------------------------------------------------------- #
# Scam reports — ALL against fictional demo entities
# --------------------------------------------------------------------------- #

SCAM_REPORTS = [
    # (slug, rating, title, body, scam_category, money_lost)

    # Acme Phishing Demo Co — e-commerce non-delivery + follow-up phishing
    ("acme-phishing-demo", 1.0, "Ordered headphones, nothing arrived",
     "DEMO content. Charged $89 in October, never received a tracking number, support email started bouncing two weeks in. Disputed via card issuer and won. Site still up.",
     "non_delivery", 89.0),
    ("acme-phishing-demo", 1.0, "Phishing follow-up after the order",
     "DEMO content. After the original order didn't arrive, started getting 'shipping confirmation' emails linking to a portal asking for SSN to 'verify identity'. Reported to FTC and the email provider.",
     "phishing", 0.0),
    ("acme-phishing-demo", 1.0, "Counterfeit item shipped from different address",
     "DEMO content. One order eventually arrived — clearly counterfeit watch, packed in a plain bubble mailer with no return address, despite listing as 'authentic Swiss-made'.",
     "counterfeit", 145.0),
    ("acme-phishing-demo", 1.0, "Reverse-image-search of product photos",
     "DEMO content. Their product photos appear on multiple unrelated drop-ship sites. The whole listing is recycled from another store.",
     "non_delivery", 67.0),

    # ExampleScam Industries Demo — fake investment platform
    ("examplescam-industries-demo", 1.0, "Deposit works. Withdrawal does not.",
     "DEMO content. Deposited $2,000. Account dashboard showed it grew to $4,300 in two weeks (already a red flag). Every withdrawal attempt fails with a new 'verification fee' demand. Filed with SEC.",
     "fake_invoice", 2000.0),
    ("examplescam-industries-demo", 1.0, "Fake celebrity endorsement video",
     "DEMO content. Ad featured a deepfaked celebrity 'endorsing' the platform. The endorsement is fabricated; the celebrity's team has publicly denied any association.",
     "phishing", 0.0),
    ("examplescam-industries-demo", 1.0, "Third independent report — auto-flag threshold demo",
     "DEMO content. This is the report that, combined with two prior independent submitters, demonstrates how True Review's three-source threshold triggers the public scam flag.",
     "fake_invoice", 1500.0),
    ("examplescam-industries-demo", 1.0, "Account 'manager' kept demanding more deposits",
     "DEMO content. Once I tried to withdraw, the assigned 'account manager' pushed me to deposit more to 'unlock' the previous balance. Classic upsell-the-victim pattern.",
     "fake_invoice", 5000.0),

    # CryptoMoonGains Demo — pig-butchering crypto romance scam
    ("cryptomoongains-demo", 1.0, "Romance + crypto in one package",
     "DEMO content. Met someone on a dating app, six weeks of warm conversation, eventually introduced to 'their' crypto platform with 'insider' returns. The pattern matches FTC's pig-butchering archetype exactly. Lost $18k. Filed with IC3.",
     "phishing", 18000.0),
    ("cryptomoongains-demo", 1.0, "Dashboard showed growth, withdrawals failed",
     "DEMO content. Same pattern as other reports. Account dashboard is fake — the underlying funds were moved out immediately. Tax-clearance fees were the final ask.",
     "fake_invoice", 24000.0),
    ("cryptomoongains-demo", 1.0, "Used a real-looking custom-domain platform",
     "DEMO content. The 'platform' had a polished UI and a custom domain. Not an obvious red flag at first glance. Lesson: any platform that promises guaranteed returns is fraud.",
     "fake_invoice", 9500.0),
    ("cryptomoongains-demo", 1.0, "WhatsApp group of 'investors' was all the scammer",
     "DEMO content. Joined a WhatsApp group of supposed fellow investors sharing screenshots of wins. Authorities later confirmed every account in the group was operated by the same fraudster.",
     "phishing", 0.0),

    # SafeTechAssist Demo — tech support / remote-access scam
    ("safetechassist-demo", 1.0, "Browser pop-up said my computer was infected",
     "DEMO content. Full-screen pop-up with a phone number claiming Windows was compromised. Called, they wanted remote access via AnyDesk. Hung up. Reported the domain.",
     "phishing", 0.0),
    ("safetechassist-demo", 1.0, "Charged $400 for 'lifetime protection'",
     "DEMO content. My elderly parent fell for it. They installed remote-access software, ran fake diagnostics, charged a credit card $400 for software that does nothing.",
     "fake_invoice", 400.0),
    ("safetechassist-demo", 1.0, "Posed as Microsoft support",
     "DEMO content. Caller claimed to be Microsoft. Microsoft does not call you. If a tech-support call is unsolicited, it is a scam.",
     "phishing", 0.0),

    # FundRecoveryGroup Demo — recovery scam (preys on prior scam victims)
    ("fundrecoverygroup-demo", 1.0, "Contacted me after I posted about a prior loss",
     "DEMO content. Cold-emailed me with detailed knowledge of a previous crypto loss. Promised to 'recover' the funds for an upfront fee. This is the classic recovery scam — scammers buying victim lists.",
     "fake_invoice", 1500.0),
    ("fundrecoverygroup-demo", 1.0, "Charged upfront, did nothing",
     "DEMO content. Paid $2k 'retainer' for 'investigation'. Got vague status updates for a month, then radio silence.",
     "fake_invoice", 2000.0),
    ("fundrecoverygroup-demo", 1.0, "Reported by FBI IC3 as a known pattern",
     "DEMO content. The recovery-scam pattern is well-documented in IC3 advisories. If anyone offers to recover scammed funds for an upfront fee, it is a second scam.",
     "phishing", 0.0),

    # QuickJobsRemote Demo — fake job listing
    ("quickjobsremote-demo", 1.0, "Asked for $200 'training kit' before starting",
     "DEMO content. Listing was on a legitimate-looking job board. Offer was 'remote data entry, $35/hr'. After accepting, they wanted $200 for a 'training kit'. Legitimate employers never charge you to start work.",
     "fake_job", 200.0),
    ("quickjobsremote-demo", 1.0, "Mailed me a fake check for 'equipment'",
     "DEMO content. Sent a $3,800 check to buy 'office equipment from approved vendor'. Check bounced after I'd already wired the 'vendor'. Out $3,800.",
     "fake_invoice", 3800.0),
    ("quickjobsremote-demo", 1.0, "All interviews via text — never a call",
     "DEMO content. Real employers do at least one synchronous conversation. Text-only hiring with immediate offers is a strong signal.",
     "fake_job", 0.0),

    # DesignerOutletDirect Demo — counterfeit goods
    ("designeroutletdirect-demo", 1.0, "Sneakers shipped in a generic box",
     "DEMO content. Ordered $400 'authentic' Air Jordans. Arrived in a plain box with stitching that didn't match retail samples. Card chargeback succeeded.",
     "counterfeit", 400.0),
    ("designeroutletdirect-demo", 1.0, "Designer bag had misspelled serial",
     "DEMO content. The serial-number tag on a $1,800 designer bag had a typo on the brand name. Returned via dispute.",
     "counterfeit", 1800.0),
    ("designeroutletdirect-demo", 1.0, "Same product photos as other counterfeit sites",
     "DEMO content. Reverse-image search returned dozens of identical drop-ship sites. The whole network shares inventory photos.",
     "counterfeit", 240.0),

    # FreeTrialMax Demo — subscription trap
    ("freetrialmax-demo", 1.0, "Free trial auto-billed $89/month",
     "DEMO content. Signed up for a 7-day trial. Cancellation buried five clicks deep. Was billed $89/month for four months before I caught it.",
     "subscription_trap", 356.0),
    ("freetrialmax-demo", 1.0, "Cancellation refused without phone call",
     "DEMO content. Tried to cancel online — site says you have to call. Call hold times consistently over an hour.",
     "subscription_trap", 89.0),
    ("freetrialmax-demo", 1.0, "Charged after I'd already cancelled in writing",
     "DEMO content. Cancelled in writing per their terms. Got charged twice more after. Filed dispute and won.",
     "subscription_trap", 178.0),
]


# --------------------------------------------------------------------------- #

def ensure_user(session: Session, handle: str, tier: VerificationTier) -> User:
    existing = session.exec(select(User).where(User.handle == handle)).first()
    if existing:
        return existing
    user = User(handle=handle, trust_score=0.7, verification_tier=tier)
    session.add(user)
    session.flush()
    return user


def run_seed(session: Session) -> dict:
    added_companies = 0
    added_reviews = 0

    for c in SAMPLE_COMPANIES:
        existing = session.exec(select(Company).where(Company.slug == c["slug"])).first()
        if existing:
            continue
        company = Company(
            slug=c["slug"],
            name=c["name"],
            kind=CompanyKind(c["kind"]),
            domain=c.get("domain"),
            description=c.get("description"),
            is_scam_flagged=c.get("is_scam_flagged", False),
            scam_severity=c.get("scam_severity", 0.0),
        )
        session.add(company)
        added_companies += 1

    session.commit()

    emp_author = ensure_user(session, "demo_employee", VerificationTier.T1_EMAIL)
    shop_author = ensure_user(session, "demo_shopper", VerificationTier.T_RECEIPT)
    scam_author = ensure_user(session, "demo_scam_reporter", VerificationTier.T_FRAUD_EVIDENCE)

    def add_review(slug: str, kind: ReviewType, rating: float, title: str, body: str,
                   author: User, **kw) -> None:
        nonlocal added_reviews
        company = session.exec(select(Company).where(Company.slug == slug)).first()
        if not company:
            return
        existing = session.exec(
            select(Review).where(Review.company_id == company.id, Review.title == title)
        ).first()
        if existing:
            return
        review = Review(
            company_id=company.id,
            author_id=author.id,
            review_type=kind,
            title=title,
            body=body,
            rating_overall=rating,
            is_demo=True,
            **kw,
        )
        session.add(review)
        if kind == ReviewType.SCAM_REPORT:
            company.scam_reports_count = (company.scam_reports_count or 0) + 1
            company.last_scam_report_at = datetime.utcnow()
            session.add(company)
        added_reviews += 1

    for slug, rating, title, body, dept, status in EMPLOYMENT_REVIEWS:
        add_review(slug, ReviewType.EMPLOYMENT, rating, title, body, emp_author,
                   department=dept, employment_status=status)
    for slug, rating, title, body, product, amount in SHOPPING_REVIEWS:
        add_review(slug, ReviewType.SHOPPING, rating, title, body, shop_author,
                   product_or_service=product, purchase_amount=amount)
    for slug, rating, title, body, category, amount in SCAM_REPORTS:
        add_review(slug, ReviewType.SCAM_REPORT, rating, title, body, scam_author,
                   scam_category=category, money_lost=amount)

    session.commit()
    return {"added_companies": added_companies, "added_reviews": added_reviews}
