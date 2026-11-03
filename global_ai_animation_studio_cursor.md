# GLOBAL AI ANIMATION STUDIO — Cursor Project Instructions

## Project vision

Build a production-grade, globally oriented **autonomous AI animation studio and YouTube channel operating system**.

This is not merely a video generator or a dashboard. The goal is to create an original, family-friendly animated series with recurring characters, relationships, a consistent visual world, and evolving stories. An AI-driven workflow should ideate, write, produce, review, schedule, publish, analyze, and improve episodes with minimal routine human intervention.

The owner should be able to configure the studio once, connect approved providers and a YouTube channel, set budgets and safety rules, and enable automation. The system should then run unattended within those configured limits, while preserving auditability, retries, monitoring, and emergency pause controls.

**Never promise zero errors or guaranteed YouTube recommendations.** Design for reliability and graceful recovery. No provider can guarantee perfect character consistency, flawless animation, or distribution to YouTube's recommendation surfaces. Use quality gates, fallbacks, monitoring, and human review where needed.

## 1. Global audience and language strategy

The project is global-first, not Turkey-first.

- Do not default to Turkish character names, settings, cultural references, metadata, or narration.
- The initial primary language should be **English**, with localization architecture for future languages.
- Character names must be short, pronounceable, memorable, and broadly usable internationally.
- Prefer original, distinctive names rather than common localized names.
- Before finalizing a channel or series name, run checks for trademark conflicts, domain/social handle availability, and potential pronunciation or cultural issues. Do not assume a name is legally clear.
- The series should be understandable to children across different countries and cultures.
- Avoid region-specific slang, political/religious messaging, or culturally narrow assumptions unless deliberately selected in a later configuration.
- Store language, locale, voice, captions, metadata, and publishing settings per channel and per episode.

## 2. Original animated series and story bible

Create a persistent **Series Bible** that AI agents must consult before writing or generating any episode.

The Series Bible should contain:

- Series title and premise
- Intended age range
- Tone, themes, and educational/positive values
- Main and supporting characters
- Family relationships (parents, siblings, caregivers, grandparents where relevant)
- Character personalities, motivations, habits, strengths, and flaws
- Character visual descriptions and approved reference assets
- Voice and speech patterns
- Locations and world rules
- Canonical timeline
- Previous episode summaries
- Ongoing story arcs
- Content boundaries and safety rules

### Original character world

Create a globally appealing original family-friendly animated world. The initial concept may center on a young, adorable animal character and their family, but the system must not hard-code one animal, one name, or one story.

AI should propose several original series concepts and character/name options. The owner selects or configures the preferred concept before autonomous production is enabled.

Characters should have emotionally recognizable relationships and development. Parents and family members should be meaningful characters, not merely background decoration. Stories can include everyday family life, friendship, discovery, gentle challenges, play, learning, and imaginative adventures.

### Story continuity

Each episode must:

- Fit the Series Bible and character canon.
- Have a clear beginning, middle, and end.
- Be understandable as a standalone episode.
- Contribute to character or world continuity where appropriate.
- Avoid abrupt, arbitrary changes in character appearance or personality.
- Avoid manipulative cliffhangers or distressing story beats.
- Include a positive, emotionally satisfying resolution.

Maintain a structured continuity memory:
- Episode summaries
- Character state and relationships
- Unresolved arcs
- Previously used plots
- Repeated phrases / catchphrases
- Approved visual and audio references

Before approving a new script, run continuity checks against this memory.

## 3. Autonomous operating loop

Implement a reliable workflow engine. The system should not rely on a single long-running AI prompt or one fragile cron job.

Suggested workflow:

1. **Planning agent**: reviews schedule, backlog, channel goals, previous performance, budget, and series canon.
2. **Story agent**: generates several episode ideas and chooses one according to configured editorial criteria.
3. **Script agent**: writes the episode script and dialogue.
4. **Continuity agent**: checks canon, family relationships, chronology, character traits, and story repetition.
5. **Safety/editorial agent**: checks child suitability, dangerous imitation, frightening content, misleading claims, and policy risks.
6. **Storyboard agent**: splits script into scenes and creates shot plans.
7. **Visual production agent**: creates character references, scene images, and video clips using provider adapters.
8. **Voice/audio agent**: generates dialogue, narration, sound effects, and properly licensed music.
9. **Assembly agent**: combines clips, voice, music, captions, transitions, and end card into a final video.
10. **Quality assurance agent**: checks duration, resolution, audio, scene continuity, missing frames/assets, captions, metadata, and safety checklist.
11. **Thumbnail/metadata agent**: creates honest thumbnail variants, title, description, and playlist metadata.
12. **Scheduler/publisher**: publishes only when all required gates pass and the configured policy allows it.
13. **Analytics agent**: reads available channel/video metrics and prepares future planning suggestions.
14. **Memory updater**: records episode summary and canonical changes only after successful production/publication.

Every stage must be a durable job with status, logs, input/output references, retry policy, and idempotency key.

## 4. Automation modes and controls

Provide three operating modes:

### Manual
AI prepares ideas, scripts, assets, and metadata. Owner approves each stage.

### Assisted
AI produces complete draft episodes. Owner approves final episode before publishing.

### Autonomous
AI can produce and publish unattended only within explicitly configured guardrails:
- Approved series bible and character set
- Allowed topics and age range
- Maximum episode duration
- Maximum number of uploads per week
- Publishing windows and timezone
- Per-episode and monthly provider budget
- Maximum retries
- Approved providers
- Required quality/safety checks
- Emergency stop
- Automatic pause on repeated failures, budget breach, policy warning, or suspicious output

Default mode must be **Assisted**, not Autonomous. Autonomous publishing must require an explicit owner action and channel authorization.

Add a global **Pause Automation** control that stops new production/publishing jobs safely. Do not delete already-produced assets or job logs.

## 5. AI provider selection and quality strategy

Do not hard-code one AI vendor or claim that one model is always the best. Build provider adapters and select providers based on current availability, quality, cost, latency, commercial rights, supported duration/resolution, consistency features, and API limits.

Provider categories:
- Text/script generation
- Image and character reference generation
- Video generation
- Text-to-speech / dialogue
- Music and sound effects
- Video assembly / transcoding
- Safety and quality evaluation

Create provider interfaces such as:
- `TextGenerationProvider`
- `ImageGenerationProvider`
- `VideoGenerationProvider`
- `TextToSpeechProvider`
- `AudioGenerationProvider`
- `VideoAssemblyProvider`
- `SafetyReviewProvider`
- `YouTubeProvider`

Provider adapters must be independently configurable. Use official APIs and current documentation. Verify provider terms, commercial usage rights, rate limits, pricing, and API availability before integration. Do not invent endpoints or pretend a mock result is a real generation.

### Video production strategy

Prefer a scene-based production pipeline:
- Stable character reference images and approved character sheets
- Scene/shot prompts derived from the approved storyboard
- Short clips generated per shot
- Audio and dialogue synchronized during assembly
- Final render validated before upload

Character consistency should be supported through reference assets, repeated visual descriptions, seeds or reference features where available, and a continuity review. Do not claim absolute consistency if the provider cannot guarantee it.

If a provider is unavailable:
- Retry with bounded exponential backoff
- Use a configured fallback provider only if approved
- Pause and alert when quality or budget limits are reached
- Never silently publish a degraded or incomplete video

## 6. Episode length and format

Make episode duration configurable. The system may test several suitable long-form durations based on the chosen age range, narrative quality, production cost, and audience response.

Do not optimize solely for maximum watch time or use manipulative retention tactics. Prefer complete, coherent, age-appropriate stories with a natural pace.

Each episode should have:
- Opening that introduces the story naturally
- Scene progression with clear cause and effect
- Dialogue suitable for the intended age
- Gentle transitions
- Ending with emotional closure
- Optional natural invitation to watch another episode, without pressure

## 7. Global publishing and scheduling

Implement a publication planner that supports:
- Channel timezone and target audience locales
- Configurable upload cadence
- Publishing windows
- Calendar and queue
- YouTube upload and scheduled publication
- Status monitoring
- Retry and failure handling
- Published URL storage
- Duplicate-upload prevention

Starting hypothesis for a new channel:
- Begin with **2–3 quality episodes per week**, rather than automatically uploading every day.
- Test a few reasonable publishing windows in the target audience's local timezone.
- Do not present any time as a guaranteed “YouTube discovery hour.”
- Use YouTube Analytics, including audience activity reports when available, to adjust scheduling after sufficient data accumulates.
- Increase cadence only if production quality, originality, budget, and channel policy compliance remain strong.

All dates must be stored consistently and displayed in the configured timezone. Use `Europe/Istanbul` only as a default owner timezone, not as the assumed audience timezone.

## 8. YouTube integration and policy

Use YouTube Data API v3 and OAuth 2.0 through official documented flows.

Support:
- Connect/disconnect channel
- Upload video
- Upload thumbnail
- Set title, description, language, playlist, and supported metadata
- Set audience designation correctly
- Schedule publication where supported
- Track upload/publish status
- Store video ID and URL
- Handle quota limits and API errors

The series is intended for children. The owner must correctly designate content as **Made for Kids** when applicable, in accordance with YouTube requirements. Do not bypass child-directed content rules, platform restrictions, or API limitations.

Before publishing:
- Confirm all assets have appropriate usage rights.
- Check title and thumbnail accurately represent the episode.
- Check for unsafe imitation, frightening or inappropriate content, privacy issues, and policy concerns.
- Ensure the episode is complete and not a repetitive, low-value mass-produced template.
- Ensure the required audience designation is set correctly.
- Respect YouTube policies and API terms.

Do not promise recommendation placement, views, subscribers, or revenue.

## 9. Thumbnail and metadata generation

Generate thumbnail variants for owner review or configured automated selection.

Requirements:
- 16:9, target 1280 × 720
- Main character prominent and visually consistent
- Readable at small sizes
- Clear emotional/story focus
- Short text only when helpful
- Honest representation of the episode
- No misleading, shocking, or fear-based clickbait

Generate:
- Title options
- Description
- Episode synopsis
- Playlist recommendation
- Language/locale metadata
- Thumbnail concepts

Metadata should be natural and useful. Avoid keyword stuffing and false claims.

## 10. Analytics and adaptive planning

Use available YouTube Analytics data to evaluate:
- Views
- Watch time
- Average view duration
- Audience retention
- Impressions
- Click-through rate
- Subscriber changes
- Performance by episode/topic/format
- Audience activity windows when available

The planning agent can use evidence to propose future topics, episode lengths, publishing windows, and thumbnail approaches.

Rules:
- Do not treat small samples as definitive.
- Show sample size and time range.
- Separate correlation from causation.
- Do not fabricate missing analytics.
- Optimize for quality, audience fit, and sustainable publishing, not manipulative tactics.
- AI recommendations should be explainable and logged.

## 11. Dashboard UX

Build a polished, responsive SaaS dashboard with:
- Sidebar navigation
- Clear status cards
- Calendar/queue
- Production pipeline view
- Episode detail page
- Series Bible editor
- Character and family relationship manager
- AI provider settings
- Budget and usage controls
- Quality review checklist
- Analytics charts
- Job logs and failure alerts
- Automation mode and global pause control

Suggested routes:
- `/dashboard`
- `/series`
- `/series/bible`
- `/characters`
- `/ideas`
- `/episodes`
- `/episodes/[id]`
- `/production`
- `/calendar`
- `/library`
- `/quality-review`
- `/analytics`
- `/automation`
- `/settings/providers`
- `/settings/youtube`
- `/settings/budget`

All buttons and forms must be functional. Include loading, empty, error, and success states. Do not build a static mock dashboard and call it complete.

## 12. Recommended technology stack

- Next.js App Router
- TypeScript
- Tailwind CSS
- shadcn/ui
- PostgreSQL
- Prisma
- Auth.js or another maintained authentication solution
- Redis + BullMQ (or durable managed queue)
- S3-compatible object storage
- React Hook Form + Zod
- Recharts
- Vitest and Playwright
- FFmpeg for media assembly/transcoding where appropriate

Use server-side APIs for secrets and provider calls. Never expose API keys or OAuth secrets in browser code.

## 13. Core database models

Create and refine Prisma models for:

- `User`
- `Channel`
- `Series`
- `SeriesBible`
- `Character`
- `CharacterRelationship`
- `StoryIdea`
- `Episode`
- `Scene`
- `Asset`
- `ProviderConfig`
- `ProductionJob`
- `PublishJob`
- `QualityReview`
- `AnalyticsSnapshot`
- `AutomationPolicy`
- `BudgetLedger`
- `AuditLog`

Include:
- Created/updated timestamps
- Status enums
- Relations and indexes
- Provider/job identifiers
- Cost and usage tracking
- Approval timestamps and reviewer
- Error details
- Idempotency keys

Encrypt OAuth credentials and sensitive provider secrets. Keep credentials out of logs.

## 14. Job orchestration and resilience

Use durable background jobs for all lengthy AI/media tasks.

Requirements:
- Each job has a stable ID and state.
- Retry only retryable errors.
- Use bounded retries and exponential backoff.
- Enforce per-job timeouts.
- Track provider request IDs.
- Prevent duplicate uploads and duplicate scheduled episodes.
- Resume safely after server restart.
- Record job history and cost.
- Pause workflows when configured limits are exceeded.
- Provide manual retry and cancel controls when supported.

Do not run lengthy video generation in a synchronous HTTP request.

## 15. Safety, legal, and quality controls

The content is child-directed. Implement a strict pre-publication review pipeline:
- Age suitability
- Unsafe behavior / dangerous imitation
- Violence, fear, or distress
- Sexual or inappropriate content
- Personal data and privacy
- Misleading titles/thumbnails
- Character continuity
- Audio clarity and loudness
- Visual glitches, black frames, missing clips
- Rights/license metadata
- YouTube audience designation and policy checklist

The AI reviewer is not infallible. In autonomous mode, if a safety check is uncertain, fails, or a provider reports a policy issue, the episode must be held for owner review rather than published.

Maintain audit logs for autonomous decisions and publication actions.

## 16. Environment variables

Create `.env.example` with placeholders:

```env
DATABASE_URL=
AUTH_SECRET=
REDIS_URL=

AI_TEXT_PROVIDER=
AI_TEXT_API_KEY=

AI_IMAGE_PROVIDER=
AI_IMAGE_API_KEY=

AI_VIDEO_PROVIDER=
AI_VIDEO_API_KEY=

AI_TTS_PROVIDER=
AI_TTS_API_KEY=

AI_AUDIO_PROVIDER=
AI_AUDIO_API_KEY=

S3_ENDPOINT=
S3_BUCKET=
S3_ACCESS_KEY_ID=
S3_SECRET_ACCESS_KEY=

YOUTUBE_CLIENT_ID=
YOUTUBE_CLIENT_SECRET=
YOUTUBE_REDIRECT_URI=

APP_URL=http://localhost:3000
DEFAULT_TIMEZONE=Europe/Istanbul
```

Never commit actual credentials.

## 17. Development phases

### Phase 1 — App foundation
- Next.js app
- Auth
- Dashboard shell
- Database and Prisma
- Responsive UI
- Demo seed data

### Phase 2 — Series Bible
- Series concept and title
- Characters
- Family relationships
- Canon/continuity memory
- Owner approval of initial series setup

### Phase 3 — AI story pipeline
- Idea generation
- Script generation
- Continuity review
- Scene/shot planning
- Editable outputs

### Phase 4 — Media production
- Provider adapters
- Reference assets
- Video/audio generation jobs
- Assembly/transcoding
- Asset library and cost tracking

### Phase 5 — Quality and publishing
- Safety/quality gates
- Thumbnail and metadata
- YouTube OAuth
- Upload and scheduling
- Publishing status

### Phase 6 — Autonomous operation
- Automation policy
- Schedule planner
- Durable orchestration
- Budget guardrails
- Global pause
- Alerts and audit logs

### Phase 7 — Analytics
- YouTube Analytics
- Performance-informed planning
- Explainable AI suggestions
- Localization and additional channels

## 18. Cursor execution instructions

When this file is provided to Cursor:

1. Inspect the repository and identify existing code.
2. Summarize architecture, assumptions, and risks.
3. Propose a phased implementation plan.
4. Start Phase 1 without waiting for further approval.
5. Build working features, not just static mockups.
6. Use mock providers only when real credentials/API access are absent; clearly label them.
7. Verify current provider and YouTube documentation before integrating APIs.
8. Add tests for key state transitions, authorization, job retries, publishing gates, and idempotency.
9. Add README and `.env.example`.
10. Run lint, typecheck, and tests; report any remaining failures honestly.
11. Do not enable autonomous publication by default.
12. Do not claim the channel can run without errors; design for recovery and safe pause.

## 19. MVP acceptance criteria

The MVP is ready when:
- Owner can sign in and create a series.
- Owner can configure a global series concept and Series Bible.
- AI can create ideas and scripts using the approved canon.
- Scripts can be split into scenes.
- Jobs can be tracked in a production pipeline.
- Mock providers allow the full workflow to be demoed without paid API credentials.
- Provider credentials can be configured securely.
- Quality review and owner approval exist.
- Publishing calendar works.
- YouTube connection and upload can be implemented using official API flows.
- Automation settings, budgets, pause, logs, and failure states are visible.
- No episode is published automatically unless owner explicitly enables autonomous mode and all configured gates pass.

**Begin by inspecting the repository, then implement Phase 1. Keep the architecture ready for the autonomous production pipeline described above.**


## 20. Multi-channel, multilingual, and global localization

The studio must support multiple YouTube channels and multiple languages from one central dashboard. It must not be limited to a single English channel.

Examples:
- English channel for a global audience
- Turkish channel for Türkiye
- Spanish channel for Spanish-speaking audiences
- German channel for German-speaking audiences

Each channel is a separate configurable publishing destination with its own:
- YouTube OAuth connection and channel ID
- Display name and channel description
- Language and locale
- Target countries/regions (optional)
- Keywords and metadata preferences
- Audience designation and content settings
- Upload cadence and publishing windows
- Timezone
- Playlists
- Thumbnail style preferences
- Budget and provider settings
- Analytics and performance history
- Automation mode and approval policy

### Global source series and localized channel variants

Support a central source series and localized variants.

Example:
- Source series / canonical episode: created using the approved Series Bible.
- English localized episode: English script, dialogue, voice, captions, title, description, and thumbnail text.
- Turkish localized episode: Turkish adaptation, Turkish voice, localized metadata, and relevant cultural/language adaptation.
- Spanish localized episode: Spanish adaptation, voice, captions, and metadata.

Localization must not be a raw word-for-word translation. Use a localization agent to adapt:
- Idioms and expressions
- Dialogue length and timing
- Pronunciation and names where appropriate
- Humor and cultural references
- Voice and narration style
- Captions and on-screen text
- Titles and descriptions

Preserve canonical character identities, visual appearance, relationships, plot, and core intent across languages unless the owner explicitly configures a localized adaptation.

### Separate channel workflow

The owner must be able to:
1. Add a YouTube channel.
2. Connect it through official YouTube OAuth.
3. Configure its language, locale, keywords, target audience, schedule, and budget.
4. Choose which source series or episodes it receives.
5. Enable assisted or autonomous production/publishing.
6. View that channel's jobs, calendar, errors, and analytics independently.

Never assume one OAuth connection grants access to every channel. Each destination must be explicitly connected and authorized. Do not publish to a channel unless the connected account has the required permissions and the owner selected that channel as a destination.

### Localization workflow

For each selected target language:
1. Generate or adapt the episode script.
2. Review translation quality and child-appropriate wording.
3. Generate language-specific voice audio.
4. Recalculate timing and subtitle alignment.
5. Adapt any on-screen text and thumbnail text.
6. Generate localized title, description, playlist, and metadata.
7. Run safety and quality checks for that language.
8. Route the localized episode to its selected YouTube channel.
9. Publish only when the channel's configured gates pass.

A localization failure must not block other language/channel jobs unless the owner configures all-or-nothing release behavior.

## 21. Multi-channel dashboard and controls

Add a **Channels / Markets** section to the sidebar.

Required screens:
- `/channels`
- `/channels/new`
- `/channels/[id]`
- `/channels/[id]/settings`
- `/channels/[id]/calendar`
- `/channels/[id]/analytics`
- `/localization`
- `/localization/[episodeId]`

Dashboard must support:
- Channel cards with language and connection status
- Separate publishing queues
- Per-channel production and publication status
- Per-channel analytics
- Per-channel budget and usage
- Localization progress across languages
- Bulk planning actions with explicit destination selection
- Filter by channel, language, status, and date

## 22. Multi-channel data model additions

Extend Prisma models to support:
- `Channel` as a first-class destination with language, locale, target markets, metadata defaults, and timezone.
- `Series` as the canonical source story world.
- `Episode` as a canonical source episode.
- `LocalizedEpisode` linked to the source episode and target channel, with localized script, voice, captions, metadata, assets, status, and publication data.
- `ChannelSeries` relation to indicate which series a channel publishes.
- Per-channel `AutomationPolicy`, `BudgetLedger`, `PublishJob`, and `AnalyticsSnapshot`.

Avoid duplicating canonical story content when only localization differs. Keep source and localized content linked for traceability.

## 23. YouTube channel onboarding wizard

Implement an onboarding wizard:

### Step 1 — Connect YouTube
- OAuth authorization
- Read available channel information using supported API scopes
- Owner selects the destination channel
- Confirm access and permissions

### Step 2 — Channel identity
- Channel name
- Language / locale
- Target markets
- Channel description
- Keywords
- Category
- Playlist defaults
- Audience designation

### Step 3 — Content strategy
- Select source series
- Target age range
- Episode format and duration
- Publishing cadence
- Publishing windows and timezone

### Step 4 — Automation and budget
- Manual / Assisted / Autonomous
- Daily, per-episode, and monthly budget caps
- Maximum uploads per week
- Retry limits
- Required quality gates
- Emergency pause behavior

### Step 5 — Preview and confirm
- Show a summary of all channel settings
- Confirm before saving
- Keep autonomous publishing disabled until the owner explicitly enables it

Channel keywords and metadata must be stored as channel-specific configuration. Do not assume keywords guarantee discovery or recommendation placement.

## 24. Additional acceptance criteria for global operation

- Owner can connect and manage multiple YouTube channels from one panel.
- Each channel has independent language, keywords, settings, publishing schedule, budget, and analytics.
- A canonical episode can be localized into multiple languages.
- Localized videos are routed only to explicitly selected, authorized channels.
- Localization and publishing jobs are tracked independently.
- A failure on one channel does not unintentionally publish, duplicate, or block content on another channel.
- The owner can pause automation globally or per channel.
- All autonomous actions are logged and recoverable.


## 25. Long-form videos and YouTube Shorts production

The studio must support both:
- Standard long-form YouTube videos
- YouTube Shorts vertical videos

Treat them as first-class content formats with separate production settings, validation, metadata, scheduling, and analytics. The owner can enable either or both formats per channel.

### Content format configuration

Each channel must have a configurable content strategy:
- Long-form only
- Shorts only
- Long-form + Shorts
- Long-form with Shorts derived from selected episodes

Support format-specific:
- Duration target
- Aspect ratio
- Resolution
- Scene pacing
- Narration/dialogue approach
- Thumbnail/cover treatment
- Metadata
- Publication schedule
- Budget
- Quality gates

Do not hard-code a single duration. Use current YouTube Shorts eligibility rules and the channel's configuration. Validate current YouTube documentation before relying on exact duration limits or upload requirements.

### Long-form production

Create full narrative episodes using the canonical Series Bible:
- Complete story arc
- Multiple scenes
- Character development and family relationships
- Full dialogue/audio
- Appropriate pacing and ending
- Long-form export profile (typically landscape 16:9, with configurable resolution)

### Shorts production

The AI should be able to create Shorts in two ways:

1. **Derived Shorts:** Extract or re-edit a moment from a completed long-form episode, only when it forms a coherent and satisfying short experience.
2. **Original Shorts:** Generate a standalone short story within the same character universe.

Shorts requirements:
- Vertical 9:16 composition
- Suitable resolution and frame rate
- A clear visual/story premise immediately
- Fast but age-appropriate pacing
- Simple, coherent payoff
- Captions or on-screen text when useful
- Correctly mixed audio
- No misleading cut or fake cliffhanger
- No unsafe imitation or overstimulating editing

When deriving a Short from a long-form episode, reframe shots for vertical composition instead of merely cropping the center. Keep characters and important actions visible. Check dialogue and audio synchronization after editing.

### Long-form + Shorts content calendar

The calendar must distinguish:
- Long-form episode
- Original Short
- Derived Short

The planner may schedule a Short before or after a related long-form episode, but it must not assume that publishing Shorts automatically improves long-form recommendations. Use channel analytics to evaluate whether the formats complement each other.

Example configurable cadence:
- 2 long-form episodes per week
- 2–4 Shorts per week

This is only an initial test plan, not a guaranteed optimal cadence. The AI must respect configured budget, production capacity, quality, and policy requirements. It must not increase publishing frequency solely to maximize volume.

### Format-specific publishing

For each channel, allow:
- Separate Shorts and long-form publishing windows
- Independent upload queues
- Independent metadata and descriptions
- Playlist selection
- Per-format budget caps
- Per-format quality review
- YouTube upload status and URL tracking

Use official YouTube APIs and documented upload flows. Check current requirements for Shorts classification and publication. Do not rely on outdated rules or undocumented behavior.

### Format-specific analytics

Track and compare, where available:
- Views
- Watch time
- Average view duration
- Audience retention
- Impressions and click-through rate for applicable surfaces
- Subscribers gained
- Revenue metrics, only when available through authorized analytics access
- Performance by format, language, channel, topic, and publication window

Do not compare raw views alone between Shorts and long-form as if they were equivalent. Explain metrics and limitations. Monetization eligibility and revenue should be presented only from actual YouTube data, not estimates stated as guaranteed earnings.

### Data model additions

Add format-aware fields and models:
- `contentFormat` enum: `LONG_FORM`, `SHORT`
- `sourceEpisodeId` for Shorts derived from a long-form episode
- `aspectRatio`
- `renderProfile`
- `durationSeconds`
- `formatSpecificMetadata`
- `formatSpecificPublishJob`
- format-aware analytics snapshots

Use a separate `Short` model or a unified `ContentItem` model only if the architecture clearly preserves source episode linkage, separate publication, and independent analytics.

### Automation rules

The autonomous planner may:
- Decide whether an episode warrants a derived Short
- Generate original Shorts from the approved Series Bible
- Create a Shorts production queue
- Publish according to channel settings

However:
- Never publish a Short before its required safety/quality checks pass.
- Do not automatically publish duplicate or near-duplicate Shorts.
- Avoid repetitive mass-produced templates.
- Do not use Shorts to mislead viewers about the long-form episode.
- Respect the channel's configured weekly upload limit and budget.
- Pause if format-specific policy or quality checks fail.

## 26. Additional acceptance criteria for Shorts

- Owner can enable both long-form and Shorts per channel.
- AI can produce long-form episode drafts.
- AI can produce original Shorts drafts.
- AI can derive a Short from a selected long-form episode.
- Shorts are rendered and validated in vertical format.
- Long-form and Shorts have separate queues and schedules.
- Each format can have independent metadata, budget, and analytics.
- YouTube publishing state is tracked per content item.
- No Shorts are published automatically unless the owner has explicitly enabled autonomous publishing and all configured gates pass.


---

# 27. Professional production readiness — mandatory project-wide requirements

Treat this project as a **global children’s animation IP studio, channel operations platform, and reliable media-production system**. Do not implement it as a thin AI prompt wrapper that produces files and uploads them.

Before implementing new features, audit the existing code and requirements against this document. Reuse existing architecture where sound; do not duplicate models, queues, provider integrations, or settings. Convert each requirement into a concrete implementation, UI state, test, or documented limitation. Mark anything not yet implemented as a visible backlog item rather than pretending it is complete.

## 27.1 Product operating modes and control plane

Provide clear operating modes:
- **Manual:** AI creates proposals and drafts; owner approves each consequential step.
- **Assisted:** AI runs production tasks, but publishing requires owner approval.
- **Autonomous:** AI can publish only within explicitly enabled channel, format, budget, schedule, policy, and quality boundaries.

Autonomous mode must be opt-in per channel and content format, never enabled by default. It must have:
- A global emergency stop
- Per-channel pause/resume
- Per-provider pause/fallback
- Per-format pause (Long-form / Shorts)
- A kill switch that stops new work and safely cancels or drains queued jobs
- A visible state showing what is running, queued, blocked, failed, or scheduled
- A clear “what will happen next” explanation before automation is enabled
- Audit history for every setting change and consequential AI decision

The AI may not silently loosen safety, quality, budget, publishing, or compliance thresholds to make a job succeed.

## 27.2 Brand identity and channel packaging

Create a **Brand Kit** per series and channel, with:
- Approved series/channel names and short descriptions
- Logo, avatar, channel banner, watermark, typography, palette, and safe-area rules
- Intro/outro policy (optional, short, not forced onto every format)
- Thumbnail style guide, character pose library, and composition rules
- Brand voice, humor, reading level, vocabulary, and tone
- Prohibited visual or verbal motifs
- Brand usage and localization rules

Generate and validate YouTube channel assets at the current official size/aspect requirements. Do not hard-code stale dimensions; validate against current platform documentation. Preview on desktop, mobile, TV, and cropped avatar/banner views. Keep source files and export profiles so assets can be regenerated.

The brand must remain recognizable across languages while allowing culturally appropriate localized variants. Avoid confusingly similar names, unauthorized franchise references, or claims of affiliation.

## 27.3 Editorial strategy and audience definition

Require the owner to configure or approve:
- Target age band and developmental level
- Primary audience and caregiver co-viewing assumptions
- Educational, emotional, entertainment, and values goals
- Episode duration ranges by format
- Content pillars and topic boundaries
- Tone and intensity limits
- Story structure and pacing preferences
- Season/series strategy and release cadence
- Language, region, and cultural adaptation profile

Never treat “children” as a single global audience. The system should support distinct age bands and adjust vocabulary, pacing, concepts, conflict intensity, humor, and learning goals accordingly. Age selection must not override platform or legal requirements.

## 27.4 Originality, variety, and editorial quality

Build an editorial quality system that protects against repetitive, low-value, mass-produced output.

Before production, compare the proposed episode against:
- Prior scripts and episode summaries
- Character combinations and settings
- Story premises, conflict, resolution, jokes, songs, and educational concepts
- Recent thumbnails, titles, and metadata
- Recent videos across the same series and language channels

Use similarity checks as a **review signal**, not as a substitute for editorial judgment. Reject or regenerate near-duplicate work when it lacks meaningful new narrative or educational value. Similarity thresholds must be configurable and tested.

Each episode must have a distinct creative premise, clear narrative progression, meaningful character action, coherent resolution, and an identifiable viewer value. Reuse of the same characters, world, intro/outro, or art direction is allowed; reuse of interchangeable plot templates without meaningful variation is not.

Maintain a creator’s production evidence package:
- Series Bible version
- Script and revisions
- Storyboard/scene plan
- Prompt and generation configuration snapshots
- Asset provenance and provider/model identifiers
- Editing/rendering steps
- Review results and approvals
- Final video and metadata versions

This package supports provenance, debugging, rights review, and evidence of original production. Do not claim that AI output is guaranteed copyrightable or legally exclusive.

## 27.5 Child safety and family-content editorial policy

Implement a configurable, versioned safety rubric aligned with current YouTube Community Guidelines, child safety policies, and kids/family quality principles.

Screen scripts, visuals, audio, thumbnails, titles, descriptions, and metadata for:
- Dangerous or imitable behavior
- Bullying, humiliation, cruelty, or encouragement of dishonesty
- Sexual content, exploitation, or adult themes
- Graphic violence, frightening imagery, distress, or intense peril
- Harmful stereotypes, discriminatory content, or hateful messaging
- Unsafe health, food, hygiene, medicine, or physical activity claims
- Deceptive educational claims or incorrect learning material
- Sensational, misleading, bizarre, or keyword-stuffed content
- Unhealthy emotional manipulation, fear, or pressure to purchase
- Inappropriate use of familiar children’s characters or protected IP
- Confusing, incoherent, or jumbled autogenerated storytelling

Use defense in depth:
1. Script-level checks
2. Storyboard and shot-level checks
3. Audio/transcript checks
4. Rendered-video checks
5. Metadata and thumbnail checks
6. Final publication gate

A safety issue must block publication until corrected and rechecked. High-risk or ambiguous cases must be routed to human review. Do not let the same AI agent both generate content and unilaterally certify every safety-critical check.

For child-directed content, default to conservative privacy and engagement handling. Do not collect child viewer personal data, create child profiles, infer individual child identity, or use comments/DMs as a source of child information. Never use engagement bait, deceptive “educational” claims, or pressure tactics.

## 27.6 Global compliance and localization governance

Create a **Compliance & Policy Registry** with:
- Jurisdiction/market
- Policy or legal topic
- Official source URL
- Last checked date
- Effective date, if known
- Applicability and owner
- Required product/content behavior
- Review status and next review date

Support configurable market profiles and a global baseline. At minimum, design for review of:
- YouTube Terms, Community Guidelines, child safety, Made for Kids designation, monetization and copyright policies
- United States COPPA and applicable advertising/privacy requirements
- EU GDPR, applicable children’s privacy requirements, and relevant Digital Services Act obligations
- UK GDPR and Age Appropriate Design Code considerations
- Other target-market privacy, child protection, advertising, consumer protection, and content rules as markets are added

Do not hard-code legal conclusions or claim global legal compliance. Provide a clear “legal review required” state for uncertain cases and allow qualified counsel to update market requirements. Avoid launching a market profile until required policies and settings have been reviewed.

For Made for Kids classification:
- Require a channel/video audience decision supported by a documented checklist and owner approval.
- Do not infer it only from tags, analytics, or AI classification.
- Keep channel-level defaults and video-level overrides explicit.
- Confirm the chosen designation is set through the official upload/API flow where supported.
- Surface any mismatch between the configured audience and YouTube’s returned status.
- Treat mixed-audience and ambiguous content as requiring careful review rather than automatic classification.

## 27.7 AI disclosure, real-person likeness, and synthetic media

Track AI usage and realistic synthetic-media status for every content item. Distinguish:
- AI used as production assistance (ideas, outlines, scripts, captions, non-realistic animation)
- Realistic synthetic or meaningfully altered content
- AI-generated music or other cases where platform disclosure requirements apply
- Voice/likeness cloning and any required consent

Before upload, determine whether YouTube’s current disclosure field is required and set the corresponding supported API field when applicable. If the API does not expose a required setting or the policy is ambiguous, block autonomous publication and request manual completion in YouTube Studio.

Never clone a real person’s voice or likeness without documented authorization. Keep consent scope, expiry, allowed markets, and permitted use linked to the asset. Never imitate a famous character, celebrity, creator, or franchise as a shortcut.

## 27.8 Copyright, licensing, and asset provenance

Create a rights ledger for all generated and imported assets:
- Image/video/audio asset ID
- Origin (generated, owner-uploaded, licensed, public domain, etc.)
- Provider/model and generation date
- Prompt/configuration snapshot where allowed
- License/terms version and commercial-use eligibility
- Source/creator and proof of permission where relevant
- Restrictions, attribution, territory, term, and expiry
- Content ID/copyright claim status where available
- Whether the asset can be used in monetized content, ads, merchandise, or other derivative works

Before production or publication, check provider terms for commercial use, child-directed use, output ownership, training/data handling, attribution, and restrictions. Terms vary by provider, plan, model, and date; do not assume all generated outputs are cleared.

Do not use copyrighted songs, sound effects, footage, logos, character designs, or other third-party material unless there is a verified permitted basis. Do not rely on “AI-generated” as a copyright clearance. Store music stems and license metadata. Provide a way to replace an asset across future productions if a license expires or a claim arises.

## 27.9 Localization as adaptation, not literal translation

Implement a localization workflow that includes:
- Source language and locale
- Target language, locale, and market
- Script adaptation and dialogue timing
- Character name pronunciation and local suitability
- Voice casting/voice profile per language
- Subtitle/caption generation and review
- Thumbnail/title/description/tag adaptation
- Culture-specific references, idioms, humor, units, and educational concepts
- Reading-level and linguistic quality checks
- Native-speaker review status for priority markets

Do not translate titles, jokes, or dialogue literally when the result is unnatural. Preserve canon and story intent while adapting language and cultural context. Maintain a translation memory and approved glossary, but do not force identical metadata across markets.

## 27.10 Accessibility and inclusive production

Include:
- Captions/subtitles for supported languages
- Caption timing and readability checks
- Dialogue clarity and intelligible audio
- Visual storytelling that does not rely only on audio
- Contrast and text legibility
- Avoidance of rapid flashing and unnecessarily disorienting effects
- Descriptive language where useful
- Configurable audio-description or accessibility tracks when feasible

Do not claim that generated captions are accurate without checking them. Validate caption sync, spelling, speaker attribution, and language.

## 27.11 Thumbnail, metadata, and discovery quality

Create a per-channel/per-market metadata and thumbnail workbench.

For every video:
- Generate several distinct title and thumbnail concepts
- Select one that accurately represents the actual episode
- Check that the thumbnail is readable at small sizes and mobile crop
- Avoid misleading expressions, fake danger, fake educational promises, and deceptive curiosity gaps
- Ensure character designs and branding are consistent
- Validate title/description/tag language against the target market
- Use a concise description, relevant playlist, and useful chapter markers for long-form where appropriate
- Keep keyword/tag use natural and relevant; never keyword-stuff
- Check for trademark, privacy, or rights issues in metadata and artwork

Store metadata versions and track their performance. Only perform changes within the owner-approved policy. Do not automatically change metadata at high frequency or make misleading changes to chase impressions.

## 27.12 Publishing workflow and YouTube API reliability

Use official YouTube APIs and supported OAuth scopes. Maintain a channel connection health state, token refresh, revocation handling, and least-privilege access.

For every upload:
- Validate file, codec, resolution, aspect ratio, duration, audio, and metadata
- Validate configured audience and synthetic-media disclosure
- Upload with a resumable/retry-capable process where supported
- Store upload session and video ID safely
- Poll processing status and handle failure/rejection states
- Verify the final privacy status and scheduled publish time
- Reconcile local state with YouTube after uncertain failures
- Prevent duplicate uploads using idempotency keys and a publication ledger
- Record API quota usage and back off on quota/rate errors
- Respect subscriber-notification settings and avoid unnecessary notification bursts
- Surface API project verification or upload restrictions clearly

Never assume an API call succeeded because the request was sent. Confirm state from the API response and subsequent read-back. Do not retry a non-idempotent upload blindly after a timeout.

## 27.13 Production QC and render validation

Create automated checks for:
- Missing, black, frozen, or corrupted frames
- Unexpected aspect ratio, resolution, frame rate, duration, or codec
- Audio clipping, silence, abrupt cuts, loudness inconsistencies, or sync drift
- Missing dialogue, overlapping voices, pronunciation errors, and caption mismatch
- Character identity/appearance drift across shots
- Scene continuity, camera/character framing, and safe-area violations
- Text spelling, subtitle overflow, and illegible on-screen text
- Unapproved assets or provider watermarking
- Thumbnail/video mismatch
- Render completion and file integrity

Define quality thresholds per format and market. Any critical failure blocks publishing. Save QC reports and allow a failed stage to be rerun without unnecessarily regenerating approved upstream assets.

## 27.14 Observability, operations, and incident handling

Build a production operations dashboard showing:
- Pipeline stages and queue age
- Success/failure/retry rate
- Provider latency, errors, and availability
- Render duration and resource usage
- Cost by provider, channel, format, episode, and market
- Upload and processing status
- Upcoming publications and blocked jobs
- Quality/safety review failures
- Token expiry, quota, and connection health

Provide structured logs, correlation IDs, metrics, traces where appropriate, alerts, and an incident log. Never log OAuth tokens, secret keys, or sensitive child-related data.

Create documented recovery procedures for:
- Provider outage
- Queue backlog
- Failed render
- YouTube API quota exhaustion
- OAuth revocation
- Duplicate/incorrect publication
- Copyright claim or policy strike
- Budget threshold breach
- Data corruption or restore

## 27.15 Data security, privacy, and retention

Security requirements:
- Encrypt secrets and tokens at rest; use a managed secrets system in production
- Encrypt traffic in transit
- Enforce role-based access control and least privilege
- Require strong authentication for administrative actions
- Use secure session management, CSRF protections, rate limits, and input validation
- Protect webhook endpoints and validate signatures where supported
- Maintain audit logs for authentication, settings, publishing, deletion, and provider changes
- Separate development, staging, and production credentials
- Avoid storing personal data unless necessary
- Establish retention and deletion policies for scripts, renders, logs, and assets
- Provide export/delete workflows for owner data
- Keep backups and test restore procedures

The platform is intended to produce children’s media; it must not become a child-facing app or collect data from child viewers. Avoid behavioral profiling of children. Any analytics integration must use authorized, aggregate creator/channel data and comply with applicable platform policies and laws.

## 27.16 Budget, cost forecasting, and financial controls

Create a cost ledger that records actual provider usage and costs, where available, by:
- Channel
- Language/market
- Episode/content item
- Format
- Provider/model
- Production stage
- Retry/fallback
- Storage and rendering

Before a production job starts, estimate cost and show:
- Estimated minimum/maximum
- Required provider credits or subscription capacity
- Expected render/storage cost
- Current period budget
- Whether this job could exceed limits

Support hard daily, weekly, monthly, per-channel, per-format, and per-episode caps. Hard limits must stop new work rather than merely show a warning. Include approval thresholds for expensive retries or provider changes. Never fabricate provider costs; mark unavailable prices as unknown and require configuration.

## 27.17 Analytics and evidence-based improvement

Build a channel analytics layer that imports only authorized metrics and stores dated snapshots.

Analyze separately by:
- Channel and market
- Language
- Long-form / Shorts
- Episode/topic/series arc
- Title/thumbnail version
- Publication time/window
- Traffic source and audience retention where available

Track impressions, click-through rate where applicable, views, watch time, average view duration, retention curves, subscribers gained, returning viewers, and revenue only when the authorized source exposes them.

Use experiments carefully:
- Owner-approved title/thumbnail tests where supported
- Limited, documented changes
- Avoid changing multiple variables without a plan
- Do not use misleading thumbnails or titles
- Do not treat correlation as causation
- Do not compare Shorts and long-form raw view counts as equivalent
- Do not optimize solely for clicks; include satisfaction, retention, quality, safety, and audience trust

AI may recommend changes, but it must explain the evidence, uncertainty, expected tradeoffs, and approval requirements. It must not guarantee virality, rankings, or income.

## 27.18 Channel operations and content catalog

Provide a channel workspace with:
- Channel identity, market, locale, and audience designation
- Connected account and permissions health
- Brand Kit and Series Bible
- Content calendar and production queue
- Published, scheduled, draft, blocked, and failed items
- Playlist and series organization
- Long-form/Shorts relationships
- Copyright/rights alerts
- Policy and compliance review state
- Analytics snapshots and reports
- Channel-specific settings and publishing limits

Provide a searchable content catalog with filters, episode/season/format/language, status, asset provenance, and YouTube URL/video ID. Maintain version history for scripts, audio, renders, thumbnails, and metadata.

## 27.19 Human review and approvals

Human review is required when:
- The content safety checker reports a high-risk or ambiguous issue
- A market’s legal/policy applicability is uncertain
- Rights or licensing evidence is incomplete
- A realistic synthetic-media disclosure decision is ambiguous
- A major canon/brand change is proposed
- A provider’s terms or capabilities have changed materially
- An upload or publication state cannot be verified
- A budget threshold or unusual cost is exceeded
- A new channel or language market is launched
- A critical QC check fails repeatedly

Approval screens must show the actual item, all relevant warnings, the proposed action, and what happens after approval. An approval for one item must not silently approve future items.

## 27.20 Accessibility, maintainability, and test strategy for the web panel

The Next.js application must provide:
- Responsive desktop/tablet/mobile layouts
- Accessible labels, keyboard navigation, focus states, and semantic controls
- Clear loading, empty, success, warning, blocked, and error states
- Search, filters, sorting, pagination, and useful bulk actions
- Confirmation for destructive or consequential actions
- Consistent design system and reusable components
- Localization-ready UI strings and date/time formatting
- Proper timezone handling for channel schedules

Tests must include:
- Unit tests for business rules and validators
- Integration tests for database, queues, provider adapters, and YouTube workflows
- End-to-end tests for onboarding, configuration, review, scheduling, publishing, pausing, and recovery
- Safety/policy regression tests with known test cases
- Permission and authorization tests
- Idempotency and retry tests
- Backup/restore and failure-injection tests
- Accessibility checks and responsive UI tests

## 27.21 Provider abstraction and model selection

Keep text, image, video, voice, music, caption, and rendering providers behind explicit adapter interfaces.

For every provider/model, maintain a capability registry containing:
- Supported task types
- Current availability and health
- Pricing/cost model
- Commercial-use terms and restrictions
- Resolution, duration, aspect ratio, and output constraints
- Character/reference consistency capabilities
- Localization/voice/language capabilities
- Watermark and disclosure behavior
- Rate limits and quota
- Known quality limitations

Select providers based on configured quality, cost, reliability, rights, and output requirements. Do not hard-code a single provider as universally best. Recheck official provider documentation before implementation and when capabilities change. Fallback must not bypass licensing, safety, or quality requirements.

## 27.22 Database, workflow, and scaling requirements

Use a durable state machine for production and publishing. Each job stage must have:
- Explicit state and transition rules
- Input/output references
- Retry count and retry policy
- Timeout
- Idempotency key
- Error category and human-readable message
- Cost record
- Provenance
- Cancellation and resume behavior

Use durable queues, bounded concurrency, backpressure, and per-provider rate limits. Do not rely on a long-lived web request to run a complete production job.

Design database migrations, indexes, and retention policies intentionally. Keep large media in object storage and store references/metadata in the relational database. Use signed, short-lived URLs for private media. Support resumable work after restarts and prevent double-publishing.

## 27.23 Backup, disaster recovery, and lifecycle

Define:
- Automated database backups
- Object-storage lifecycle and versioning
- Recovery point and recovery time objectives appropriate to the project
- Restore drills
- Provider credentials recovery/reconnection
- Job replay policy
- Media archive and deletion policy
- Incident owner and recovery checklist

Do not delete source assets or production evidence merely because a video has been published. Retention must be configurable and rights-aware.

## 27.24 Professional launch checklist

Do not mark the studio “production ready” until all of the following are demonstrated:

- [ ] Series and Brand Kit approved
- [ ] Channel connected through official OAuth
- [ ] Audience designation and market profile reviewed
- [ ] Provider commercial rights and capability checks complete
- [ ] Safety, editorial, continuity, and render QC gates working
- [ ] Long-form and Shorts workflows independently tested
- [ ] Localized script/voice/metadata review completed for launch language
- [ ] Upload, processing, scheduling, and read-back verified
- [ ] Duplicate prevention and retry recovery tested
- [ ] Global and per-channel emergency pause tested
- [ ] Budgets and hard stops tested
- [ ] Monitoring, alerts, logs, and incident procedures configured
- [ ] Backups and restore tested
- [ ] Analytics ingestion and reporting tested
- [ ] Owner can inspect and override every consequential automation action
- [ ] Launch pilot has been reviewed before autonomous publishing is enabled

## 27.25 Implementation priority

Build in stages; do not attempt to ship every advanced capability in one unverified pass.

**P0 — Foundations and safe MVP**
- Authentication, roles, channel onboarding, OAuth, secure settings
- Series Bible, Brand Kit, content calendar, content catalog
- Provider adapters, durable workflow state, budgets
- Long-form and Shorts generation pipeline
- Safety, continuity, rights, QC, and publication gates
- Manual/Assisted modes, approvals, pause/stop
- Official YouTube upload, scheduling, state reconciliation
- Logs, monitoring, backups, and essential tests

**P1 — Professional operations**
- Localization workflow and market profiles
- Metadata/thumbnail workbench
- Analytics snapshots and reporting
- Rights ledger and production evidence package
- Provider health/cost dashboards
- Failure recovery and alerting
- Advanced channel and format management

**P2 — Optimization and scale**
- Carefully governed experiments
- More markets and native-speaker review workflows
- Advanced scene/character consistency checks
- Cost-aware model routing and provider fallback
- More detailed retention/format analytics
- Multi-series and larger channel portfolio operations

The app must show the actual implementation status of these priorities. Never label a feature as complete solely because its UI exists; verify the underlying workflow, API behavior, persistence, authorization, and tests.


## 27.26 Official reference sources and policy freshness

Use official documentation as the source of truth. Recheck these sources during implementation and before a production launch because requirements, API fields, and policy wording can change.

- YouTube channel monetization policies and inauthentic/reused content: https://support.google.com/youtube/answer/1311392
- YouTube Made for Kids audience designation: https://support.google.com/youtube/answer/9528076
- YouTube kids & family content best practices: https://support.google.com/youtube/answer/10774223
- YouTube child safety policy: https://support.google.com/youtube/answer/2801999
- YouTube AI / altered or synthetic content disclosure: https://support.google.com/youtube/answer/14328491
- YouTube Data API video upload (`videos.insert`): https://developers.google.com/youtube/v3/docs/videos/insert
- YouTube Data API video resource and upload status: https://developers.google.com/youtube/v3/docs/videos
- YouTube API Services Developer Policies: https://developers.google.com/youtube/terms/developer-policies
- Google API OAuth 2.0 guidance: https://developers.google.com/identity/protocols/oauth2

At implementation time, document which requirements apply to this project, which API fields support them, and which cases still require YouTube Studio or owner action. Do not assume a Help Center page, API capability, provider feature, or legal requirement is unchanged simply because it was previously reviewed.


---

# 28. Owner video review, revision, and publication approval — mandatory

## 28.1 Core principle

The owner must remain in control of whether a generated video is published. The default workflow is **human review before publication**.

Even when production runs autonomously, the system must not publish a newly generated video until the owner has explicitly approved that exact final video version. Autonomous production does not imply autonomous publication.

The default operating mode for a newly configured channel is:
- AI may plan and produce content
- AI may run automated quality checks
- AI may prepare draft metadata and a proposed publication time
- AI must notify the owner when a review-ready video is available
- AI must wait for explicit owner approval before publishing or scheduling that video

Do not enable auto-publishing by default. Any future auto-publishing mode must be an explicit, separately configured opt-in and must show a clear warning that it bypasses per-video approval. The owner must be able to turn it off immediately. If auto-publishing is disabled, no system process or provider callback may bypass the approval gate.

## 28.2 Review-ready notification

When a video has completed production and all required automated gates pass, create a review task and notify the owner through the dashboard.

Notification wording should be natural and actionable, for example:
- “Yeni videon hazır. İzleyip onaylamak ister misin?”
- “Yeni Shorts videon incelemeye hazır.”
- “Revize ettiğin video yeniden hazır. Tekrar kontrol edebilirsin.”

Notifications must include:
- Content/episode title
- Channel and language/market
- Format (Long-form / Shorts)
- Duration and thumbnail preview
- Production and QC status
- Estimated or configured publication date/time
- A direct action to open the review workspace

Support in-app notifications first. Email or other notification channels may be added only after the owner configures them and grants required permissions. Do not send repeated spam notifications; deduplicate and allow notification preferences.

## 28.3 Review workspace

Build a dedicated review workspace with a video player and relevant production information.

The owner must be able to:
- Play/pause and scrub the complete rendered video
- Watch in a large player/full-screen mode
- View the thumbnail and preview the title/description
- See channel, locale, format, duration, and proposed publish date/time
- Review script, scene list, captions/subtitles, and voice/music details
- See automated QC and safety status, including warnings and failed checks
- Compare the current render with the prior revision
- Open a scene/shot timeline and jump to a scene
- Download the preview/final file where supported
- Approve the exact current version
- Request revisions with written feedback
- Reject/cancel the video
- Save a draft decision and return later

The workspace must make it obvious whether the current video is a draft, in review, revision requested, approved, scheduled, published, or blocked.

## 28.4 Review actions and behavior

Provide clear, distinct actions:

### Approve
- Approves only the exact version currently displayed
- Records the owner, timestamp, video version, and approval scope
- Enables scheduling or publication according to channel settings
- Shows the proposed publication action before it is carried out
- Does not approve future revisions automatically

### Request revision
- Opens a feedback field
- Allows owner feedback at whole-video, scene, shot, audio, script, or metadata level
- Sends the feedback into a revision plan
- Keeps the previous render available for comparison
- Starts a new revision workflow
- Returns the new render to review after production and QC

### Reject
- Stops the current publication workflow
- Marks the item rejected/cancelled with a reason
- Preserves production history and assets according to retention policy
- Does not publish or schedule the rejected version

### Approve and schedule
- Allows the owner to choose or confirm a date, time, and timezone
- Displays the target channel and exact video version
- Requires a final confirmation before committing the schedule
- Verifies the scheduled state against YouTube after the API operation

Never interpret opening, previewing, downloading, or editing a video as approval.

## 28.5 Revision feedback and AI revision planning

The owner should be able to provide natural-language revision instructions, such as:
- “Karakterlerin konuşmaları daha doğal olsun.”
- “Bu sahne çok uzun, kısalt.”
- “Müzik daha sakin olsun.”
- “Karakterin yüzü önceki sahnelerle aynı değil.”
- “Bu espriyi çıkar ve daha eğlenceli bir şey yap.”
- “İngilizce seslendirmeyi daha doğal yap.”
- “Bu sahneyi Shorts için daha dinamik hale getir.”
- “Thumbnail'da ana karakter daha belirgin olsun.”

The AI must:
1. Interpret the owner’s feedback and restate the intended changes.
2. Create a revision plan with affected scenes/assets/stages.
3. Identify which already-approved assets can be safely reused.
4. Estimate cost and time impact when available.
5. Ask for confirmation before expensive or broad regeneration when the change exceeds configured thresholds.
6. Generate the new revision.
7. Run all required QC, safety, rights, and metadata checks again.
8. Return the new version to owner review.

Do not regenerate the entire episode if only one scene, voice line, caption, or thumbnail needs revision. Preserve unchanged approved assets when technically and legally appropriate. However, any change that affects the final video must invalidate the approval of the previous final version.

If the feedback is ambiguous or contradictory, ask a concise clarification rather than guessing. Keep the feedback associated with the revision history.

## 28.6 Versioning and approval integrity

Every reviewable video must have immutable version identifiers, such as:
- Content item ID
- Revision number
- Render ID
- Media checksum/hash
- Metadata version
- Thumbnail version
- QC report version
- Review decision

Approval is bound to the exact final render and associated publication metadata. If the render, audio, thumbnail, title, description, audience designation, disclosure, or other material publication field changes after approval, the system must invalidate the affected approval and request reapproval.

Keep a clear version history:
- Revision 1 — first render
- Revision 2 — owner feedback applied
- Revision 3 — final approved render

Allow comparison of revisions and record who/what initiated each change.

## 28.7 Publication approval gate

Before uploading or scheduling a video, verify:
- Owner approval exists for the current final video version
- The current final video checksum matches the approved version
- Metadata and thumbnail are the approved versions
- Required safety and QC checks passed
- Rights/licensing checks passed
- Audience designation and disclosure fields are complete
- Channel is connected and healthy
- Publication settings, timezone, privacy, and schedule are valid
- Budget and channel limits are not exceeded

If any check fails or state is uncertain, block publication and show the owner the reason. No worker, retry, fallback, or automated scheduler may bypass this gate.

## 28.8 Review queue and status model

Create a review queue with filters for channel, language, format, series, status, and creation date.

Minimum statuses:
- `production_queued`
- `producing`
- `qc_pending`
- `review_ready`
- `revision_requested`
- `revising`
- `approved`
- `scheduled`
- `publishing`
- `published`
- `rejected`
- `blocked`
- `failed`
- `cancelled`

Define allowed transitions explicitly and enforce them in the backend. Use durable workflow state and audit events; do not rely only on frontend button visibility.

Show review queue counts and the next required owner action on the dashboard. Support stale-review reminders with configurable timing, but do not automatically publish a video merely because the owner has not responded.

## 28.9 Audit and accountability

Record:
- Who reviewed and approved/rejected the video
- Which exact version was reviewed
- Owner feedback and revision instructions
- QC/safety reports for each revision
- Publication target, schedule, and final YouTube video ID
- Every approval invalidation and reason
- Relevant setting changes that affected the workflow

The owner must be able to inspect this history. Do not expose secrets or sensitive provider data in the audit log.

## 28.10 Acceptance criteria

This feature is not complete until tests demonstrate:
- A production-ready video appears in the review queue and triggers a notification
- The owner can watch it and approve it
- The owner can request a revision in natural language
- The AI applies changes and creates a new version
- The new version returns to review
- Approval of the old version does not approve the new one
- Rejected videos cannot be published
- Unapproved videos cannot be scheduled or uploaded
- A changed render or material metadata invalidates approval
- API retries and worker restarts cannot bypass approval
- The owner can pause the queue or cancel publication
- The publication ledger confirms the final YouTube state


## 29. Character Design, Appearance Controls, and Approval Workflow

### 29.1 Core Requirement
The owner must have full creative control over the appearance and visual identity of every character. AI-generated character designs are proposals, not final decisions. The owner can accept, edit, regenerate, compare, or reject any design before it becomes an approved character reference.

### 29.2 Character Design Studio
Implement a dedicated Character Design Studio in the panel. For each character, provide editable fields and visual controls, including:
- Character name, role, age range, personality, and relationship to other characters.
- Species/type and body shape/proportions.
- Face shape, eyes, eyebrows, nose, mouth, ears, fur/hair, colors, markings, and distinctive features.
- Clothing, accessories, footwear, and signature items.
- Height/build and relative scale compared with other characters.
- Animation style, rendering style, color palette, and visual tone.
- Voice profile and language variants, managed separately from visual appearance.
- Character backstory and continuity notes.

Use visual controls where practical (color pickers, dropdowns, sliders, toggles) alongside natural-language instructions. Do not require the owner to edit prompts or code to make basic character changes.

### 29.3 Character Reference Sheet
For every newly created character, generate a reviewable reference sheet before the character is used in a production episode. Include, where supported:
- Front, side, and three-quarter views.
- Full-body and close-up views.
- A range of facial expressions.
- A small set of standard poses.
- Outfit/accessory details and palette.
- A concise character description and locked visual attributes.

The owner can approve the reference sheet, request changes, or reject it. Unapproved character designs must not be treated as final production references.

### 29.4 New Character Detection in Every Script
When a script is created or edited, the system must identify every character who appears or is mentioned as participating in a scene. It must:
1. Match each character against the approved character library.
2. Detect characters that do not yet exist in the library.
3. Create a proposed character profile and reference sheet for each new character.
4. Present those proposals to the owner for review.
5. Use new characters in production only after the required approval.

The script workflow must show a character roster per episode, including returning characters and newly proposed characters. Do not silently invent a new visual identity during scene generation.

### 29.5 Owner Feedback and Iterative Revision
The owner must be able to provide natural-language feedback such as:
- “Gözlerini biraz büyüt.”
- “Tüy rengini daha açık yap.”
- “Bu karakter daha sevimli ve küçük görünsün.”
- “Kıyafetini değiştir ama yüzünü aynı tut.”
- “Önceki tasarıma geri dön.”

The system must translate feedback into a proposed design change, show a preview, and allow the owner to compare versions before approval. The system must not overwrite an approved character design without explicit owner confirmation.

### 29.6 Versioning and Visual Locks
Maintain versioned character designs with:
- Character ID and immutable design version ID.
- Approved reference images and source-generation metadata where available.
- Editable design attributes and prompt/reference configuration.
- Creation and approval timestamps and owner identity.
- Change history and ability to restore a previous version.

Approved visual attributes must be locked as references for subsequent scenes and episodes. If the owner changes an approved design, create a new version. Preserve prior versions and their associated episode/render references.

### 29.7 Consistency Across Scenes and Episodes
Every scene generation request must reference the relevant approved character design version. Use reference images, character IDs, supported identity/consistency controls, and explicit visual constraints provided by the selected generation provider.

The pipeline must:
- Keep faces, proportions, colors, markings, outfits, and signature accessories consistent.
- Distinguish intentional costume changes from accidental appearance drift.
- Detect and flag notable visual deviations during quality control where technically possible.
- Avoid claiming perfect character consistency; provider limitations must be surfaced.
- Allow the owner to mark a scene as an intentional exception.

### 29.8 Scene-Level Character Review
In the episode review workspace, allow the owner to select a scene and inspect its characters. If a character looks wrong, the owner can:
- Request a targeted scene regeneration.
- Provide a specific correction while preserving other approved attributes.
- Regenerate only the affected shot/scene where supported, rather than the entire episode.
- Compare before/after versions and approve the correction.

Any revised render must return through the applicable quality checks and owner review. A change to a scene or final video invalidates the prior approval of that render.

### 29.9 Character Library and Settings
Provide a searchable Character Library with filters such as approved, draft, needs revision, archived, and recently used. Character settings must be accessible from:
- A dedicated Character Library / Character Design Studio.
- The script's detected character roster.
- The episode/scene review workspace.

When editing a character from a script or scene, clearly indicate whether the change affects only that scene or creates a new character design version that can be used in future productions. Require confirmation before applying a global character change.

### 29.10 Acceptance Criteria
- The owner can create, edit, regenerate, approve, reject, and restore character design versions without changing code.
- Every newly detected character in a script receives a proposed profile and reference sheet before production use.
- Production cannot silently use an unapproved new character design.
- A character design change does not overwrite the previous approved version.
- Scenes use the selected approved character reference version.
- The owner can request targeted corrections to a scene and review the revised output.
- Character appearance changes are recorded in the audit/change history.


## 30. Child Development-Informed Storytelling, Slow Pacing, Curiosity, and Series Continuity

### 30.1 Editorial Objective
The studio must create age-appropriate stories that children can understand, emotionally connect with, remember, discuss, and look forward to revisiting. The objective is meaningful, enjoyable storytelling—not maximizing screen time, compulsive viewing, or exploiting children's developmental vulnerabilities.

Story design should be informed by child-development and narrative research, while avoiding claims that any formula guarantees attention, attachment, learning, or channel growth. The owner must define the intended age range for the channel and each series before generating scripts.

### 30.2 Slow, Gradual Story Progression
The main story universe must develop gradually across episodes. Do not rush major events, relationships, character transformations, discoveries, conflicts, or resolutions merely to fit them into one episode.

The AI must:
- Develop characters and relationships through small, understandable moments.
- Allow children time to understand what happened and why.
- Avoid introducing too many new characters, locations, rules, or plotlines in a single episode.
- Avoid resolving major mysteries or long-running goals too early.
- Maintain a series bible containing the current state of the world, relationships, character goals, known facts, unresolved questions, and planned gradual developments.
- Use a season/series arc plan to distribute major milestones across a reasonable number of episodes.
- Ensure each episode advances the story in a meaningful but measured way.

The system must not artificially stretch a story with repetitive filler. Slow progression means meaningful development at a child-friendly pace, not delaying every answer or making episodes feel incomplete.

### 30.3 Hybrid Episodic and Serial Structure
Use a hybrid structure:
- **Episode-level story:** Each episode contains a clear, age-appropriate situation or mini-adventure with a beginning, development, and satisfying resolution.
- **Series-level story:** Each episode also contributes a small step toward a broader relationship, goal, mystery, place, or character-development arc.
- **Season/arc milestones:** Larger changes happen gradually and are spaced across multiple episodes.
- **Continuity:** Previous events matter. Characters remember what happened, relationships evolve, and established facts remain consistent.

Children should be able to enjoy an episode even if they have not seen every previous installment, while returning viewers receive extra enjoyment from recognizing ongoing developments.

### 30.4 Curiosity and Wonder
Build curiosity through story-world questions that are understandable, meaningful, and safe for the target age:
- Introduce a small, intriguing question, unusual object, new place, unexplained but non-threatening event, or character goal.
- Give children enough information to form their own guesses.
- Let clues emerge naturally through scenes and character actions.
- Allow characters to wonder aloud, make predictions, and explore possibilities.
- Resolve questions at a thoughtful pace; do not keep every question unanswered.
- Mix immediate answers with a few longer-running, gentle mysteries.

Curiosity must come from wonder, discovery, empathy, problem-solving, humor, and anticipation—not fear, distress, threats, or deceptive promises.

### 30.5 Character Identification and Emotional Connection
Characters should have recognizable traits, strengths, flaws, preferences, hopes, and age-appropriate feelings. They should not be reduced to generic plot devices.

The AI should:
- Give characters consistent motivations and distinctive ways of responding.
- Show feelings through dialogue, behavior, facial expressions, and choices.
- Let characters learn gradually rather than become perfect after one lesson.
- Create relatable everyday experiences such as friendship, cooperation, jealousy, disappointment, trying again, sharing, curiosity, and asking for help.
- Show supportive relationships with caregivers and trusted adults where appropriate to the story.
- Preserve each character's voice and behavior across episodes and languages.

The story may encourage empathy and perspective-taking, but must not claim to diagnose, treat, or guarantee psychological outcomes.

### 30.6 Gentle Suspense and Episode Endings
Use age-appropriate anticipation with a balanced ending:
- Resolve the main emotional or practical problem of the episode.
- End with a warm, funny, surprising, thoughtful, or hopeful moment.
- Optionally introduce one small question or invitation that naturally leads to the next episode.
- Make it clear that the characters are safe when the story includes uncertainty.
- Do not use frightening cliffhangers, threats to a beloved character, distressing separation, shame, or high-pressure “watch now or miss out” language.
- Do not repeatedly withhold essential resolution solely to compel another viewing.
- Do not promise a specific next episode unless it is planned and feasible.

A cliffhanger is optional, not mandatory. The ending must feel emotionally satisfying even when a gentle ongoing question remains.

### 30.7 Age-Appropriate Pacing and Complexity
The owner must configure the target age band and desired episode duration. The AI should adapt:
- Sentence length, vocabulary, dialogue density, and explanation.
- Number of characters and plot threads.
- Scene duration and visual change frequency.
- Emotional intensity, conflict complexity, and how quickly information is revealed.
- Amount of repetition and recap.
- Degree of independence expected from viewers to remember previous events.

Do not assume all children of the same age have identical comprehension, attention, or emotional needs. Use age bands as production guidance, not as a diagnosis or rigid developmental claim.

### 30.8 Repetition, Familiarity, and Meaningful Variation
Use recurring phrases, routines, locations, character behaviors, motifs, songs, or visual cues when they support recognition and participation. Repetition should reinforce familiarity or meaning, not pad runtime.

Vary the adventure, emotional situation, problem-solving approach, humor, and discoveries so episodes do not become formulaic. Maintain recognizable patterns while offering meaningful novelty.

### 30.9 Story Bible and Continuity Memory
Maintain a structured, versioned series bible containing:
- Canonical character profiles and approved visual/voice references.
- Relationships and how they have evolved.
- Timeline and episode summaries.
- World rules, locations, objects, and recurring motifs.
- Resolved story questions and open questions.
- Character knowledge: what each character has and has not learned.
- Planned future milestones and forbidden contradictions.
- Emotional or thematic lessons already explored, to avoid repetitive moralizing.

Before generating a new script, retrieve relevant continuity and validate the draft against it. Flag contradictions for owner review rather than silently rewriting canon.

### 30.10 Owner-Controlled Arc Planning
Provide a Story Arc Planner in the panel where the owner can:
- Define the central premise and long-term goal or mystery.
- Set an approximate arc/season length without forcing a premature ending.
- View episode-by-episode milestones and character development.
- Decide which questions are answered now, later, or intentionally left open.
- Move, edit, approve, or remove planned milestones.
- Preview whether a proposed episode progresses the story too quickly, repeats previous material, or leaves the episode without a satisfying resolution.

AI suggestions must remain editable and require owner approval before becoming canonical.

### 30.11 Responsible Engagement and Child Wellbeing
The system must not optimize content for compulsive viewing or exploit children's susceptibility. Specifically:
- No manipulative urgency, guilt, fear of missing out, or direct pressure on children to watch another episode.
- No deceptive “secret” or reward promises that are not fulfilled.
- No distressing cliffhanger designed to leave children anxious.
- No engagement tactics that encourage ignoring sleep, school, family, or offline activities.
- Do not use analytics to infer sensitive psychological traits about individual children.
- Do not use comments, personal data, or behavioral profiling of child viewers to generate personalized pressure tactics.

Optimize for story quality, age appropriateness, positive audience feedback, comprehension, and responsible channel performance—not watch time at any cost.

### 30.12 Story Quality Review Checklist
Before a script is approved, the system should review:
- Is the story understandable for the selected age range?
- Does the episode have a clear beginning, development, and satisfying resolution?
- Does it make a meaningful but gradual contribution to the larger arc?
- Is the pace too fast, too slow, or padded?
- Is there a clear, child-appropriate source of curiosity or wonder?
- Do the characters act consistently and have understandable motivations?
- Is the emotional intensity appropriate and does the episode restore a sense of safety?
- Does it preserve continuity and avoid contradictions?
- Does it avoid manipulative engagement techniques?
- Does it offer meaningful novelty rather than repeating prior episodes?

The AI should provide concise explanations and flag concerns; the owner remains the final editorial approver.

### 30.13 Research-Informed, Not Research-Guaranteed
Narrative transportation, character identification, curiosity, suspense, and serial storytelling are useful concepts for informing creative design. Research findings must be described with appropriate limits. Do not assert that a particular pacing formula, cliffhanger, character, or episode structure will necessarily make children attached, return to the channel, or improve psychological outcomes.

The studio should use responsible qualitative feedback and aggregate channel analytics to improve storytelling without profiling individual children or compromising their wellbeing.


## 31. Child Development, Educational Storytelling, Physical and Cognitive Wellbeing, and Responsible CTAs

### 31.1 Development-Supportive Editorial Mission
The channel should combine entertainment with age-appropriate opportunities for learning, curiosity, emotional understanding, social skills, and healthy everyday habits. Stories may support children's cognitive, language, emotional, social, and physical development through character actions and narrative experiences.

This is an educational and creative objective, not a clinical or therapeutic service. Do not claim that watching the videos will diagnose, treat, prevent, or guarantee improvements in a child's development, health, intelligence, behavior, or school performance. Do not present the channel as a substitute for caregivers, educators, clinicians, or professional guidance.

### 31.2 Define Audience Age Bands and Learning Intent
Before generating a series, the owner must select an intended age range and define:
- Primary audience age band and expected language complexity.
- Main entertainment premise and educational themes.
- Intended developmental opportunities, chosen from an owner-editable taxonomy.
- Topics to avoid or require expert review.
- Episode length and pacing guidance appropriate to the selected audience.

Do not treat children of the same age as identical. Use age bands as broad creative guidance, not as a developmental assessment or diagnosis.

### 31.3 Developmental Domains
The editorial planner may include age-appropriate opportunities in the following areas:

**Cognitive and thinking skills**
- Observation, noticing similarities and differences, simple classification, sequencing, cause and effect, memory, flexible thinking, planning, and age-appropriate problem-solving.
- Encourage characters to ask questions, make guesses, test ideas safely, and explain what they noticed.
- Avoid presenting guesses as facts or making every problem have only one rigid solution.

**Language and communication**
- Natural dialogue, vocabulary introduced in context, storytelling, listening, turn-taking, describing feelings and observations, and age-appropriate multilingual exposure.
- Preserve meaning and cultural context during localization rather than translating every educational phrase literally.

**Social and emotional understanding**
- Recognizing and naming feelings, empathy, cooperation, perspective-taking, friendship, conflict resolution, asking for help, handling disappointment, patience, and trying again.
- Show characters making mistakes and repairing them without shame or humiliation.
- Do not imply that all emotions must be positive or that a child is wrong for feeling upset.

**Creativity and imagination**
- Pretend play, music, art, storytelling, building, inventing, exploring multiple ideas, and open-ended questions.
- Invite imaginative responses without suggesting that fantasy events are real-world facts.

**Physical wellbeing and movement**
- Include joyful, accessible movement opportunities such as stretching, dancing, balancing, walking, simple coordination games, or outdoor exploration when appropriate.
- Show healthy everyday routines such as rest, hydration, handwashing, safe play, and balanced meals in a non-shaming and culturally adaptable way.
- Do not prescribe exercise, diet, treatment, or health advice. Avoid body shaming, weight-focused messages, dangerous imitation, unsafe challenges, or competitive pressure.
- Make clear through context when an activity requires adult supervision or is not safe to imitate.

### 31.4 Learning Through Story, Not Constant Lecturing
The preferred format is **story first, learning naturally embedded**:
1. A character encounters a relatable situation, question, or challenge.
2. The character observes, wonders, and tries an age-appropriate approach.
3. The story shows the process and consequences in a concrete way.
4. Characters reflect briefly, share what they learned, or recognize that they may need help.
5. The episode ends with an emotionally satisfying resolution.

Avoid turning every episode into a lecture, worksheet, or moral speech. Keep learning moments concise, relevant to the plot, and enjoyable. Do not force an explicit lesson into every scene or every episode.

### 31.5 Character-as-Teacher Moments
Characters may occasionally guide the audience in a warm, playful, teacher-like way:
- Explain a simple concept using an example from the story.
- Ask the viewer a question and allow a brief pause.
- Invite the viewer to notice a clue, count objects, predict what might happen, name an emotion, or try a safe movement.
- Demonstrate a simple skill and show its use in the story.
- Use a recurring “let's discover together” moment, without making the character sound like an authority on health or psychology.

Characters must not shame, scold, test, or imply that viewers are less smart or less good if they do not know an answer. Do not pressure children to respond, share personal information, or prove that they watched.

### 31.6 Parent and Caregiver Trust
Provide a parent-facing episode information panel, distinct from child-facing video content. It may include:
- Episode synopsis and intended age band.
- Themes and skills naturally represented.
- Any movement/activity shown and relevant safety context.
- Sensitive topics or emotionally intense moments.
- Brief discussion or offline activity suggestions, where useful.
- Sources or expert review notes for factual health, safety, or developmental claims.

Do not imply that every episode is professionally certified or clinically validated. Clearly label any expert-reviewed content and identify the scope of review. Seek qualified professional review for specialized developmental, medical, mental health, nutrition, or safety topics.

### 31.7 Accuracy, Safety, and Expert Review
- Distinguish fictional story elements from real-world educational claims.
- Use reputable, current sources for factual educational or health content.
- Flag content that makes developmental, medical, nutrition, physical activity, mental health, or safety claims for human review.
- Do not generate individualized advice or infer a viewer's developmental status.
- Do not use fictional characters to endorse products, supplements, treatments, diets, or unverified claims.
- Include appropriate caregiver context for activities that could be unsafe if imitated.
- If the system cannot verify a claim, it must soften, remove, or flag it rather than inventing certainty.

### 31.8 Balanced Educational Content Strategy
Maintain a series-level content plan that balances:
- Pure entertainment and imaginative adventure.
- Cognitive curiosity and problem-solving.
- Language and communication.
- Social-emotional themes.
- Creative expression.
- Physical movement and everyday wellbeing.

Do not make every episode educational in the same way. Avoid repetitive moral lessons. The owner must be able to adjust theme frequency and approve the planned content balance.

### 31.9 Responsible Like and Subscribe Call to Action
Include a brief, consistent like/subscribe invitation in every video, preferably near the end after the main story has reached a satisfying conclusion. The CTA must:
- Be gentle, friendly, and clearly optional.
- Avoid guilt, threats, fear, urgency, shame, or promises of rewards.
- Never imply that a character will be sad, lonely, hurt, or disappointed if the viewer does not subscribe or like.
- Never ask children to pressure parents, spend money, reveal personal information, or interact in unsafe ways.
- Avoid interrupting important story or learning moments.
- Be appropriate to the platform's current child-directed content rules and features.

Suggested example:
“Bu macera hoşuna gittiyse videoyu beğenebilir ve yeni hikâyeler için kanalımıza abone olabilirsin. Bir sonraki macerada görüşürüz!”

The CTA can be delivered by a character in a warm tone, with a brief visual cue. It must not be the emotional climax or a condition for the story's resolution. The owner can configure wording, timing, character, language, and visual style; the default should be a short end-card CTA.

### 31.10 CTA and Child-Directed Platform Compliance
The system must check the current platform policies and the channel's audience designation before publishing. Do not assume that every engagement feature is available on child-directed videos. Do not create scripts that encourage children to use unavailable comments, notifications, external links, or other restricted features.

If the platform's current rules or the selected audience setting prohibit or restrict a feature, the CTA must be adapted or omitted as needed. The owner must be informed of any limitation. A generic request to subscribe or like must not be framed as a guarantee of reach, growth, or monetization.

### 31.11 Development and Educational Quality Review
Before the owner approves a script, provide an editable review summary:
- Intended age band and educational/entertainment balance.
- Developmental domains represented, if any.
- Whether the learning moment is organically integrated into the story.
- Whether dialogue, complexity, and pacing are age-appropriate.
- Any factual claim requiring source verification or expert review.
- Any physical activity or imitation safety concern.
- Whether the episode avoids shame, stereotypes, coercion, and manipulative engagement.
- Whether the like/subscribe CTA is present, brief, optional, and compliant with current platform rules.

The system should flag concerns and explain them plainly. The owner retains final editorial approval.

### 31.12 Acceptance Criteria
- The owner can define age band and developmental/educational themes for each series.
- Scripts can include natural, story-based learning opportunities without mandatory lecture segments.
- Characters can demonstrate simple thinking, emotional, social, language, creative, or physical-wellbeing skills.
- Factual or sensitive claims can be sourced, flagged, revised, or routed for qualified review.
- A parent-facing episode summary is available in the panel.
- Every video draft includes a configurable, responsible like/subscribe CTA by default, subject to current platform rules and the channel's audience settings.
- The CTA never uses guilt, fear, pressure, rewards, or emotional manipulation.
- The final video is reviewed and approved by the owner before publication, as defined in the human review workflow.


## Section 33 — Mandatory production capabilities: storyboard, continuity memory, targeted revision, cost control, and production queue

The following five capabilities are mandatory, not optional enhancements. They must be represented in the product architecture, user interface, data model, workflows, acceptance criteria, and implementation plan.

### 33.1 Storyboard preview before animation
- Before full animation rendering, generate a reviewable storyboard/animatic preview for the episode.
- Each scene should show its planned framing, characters, setting, action, dialogue/audio cue, and approximate duration.
- The owner must be able to approve, reject, or request changes to individual storyboard panels/scenes and to the overall sequence.
- Do not start expensive full animation rendering until the required storyboard approval gate has passed, unless the owner explicitly changes this setting.
- A storyboard revision must propagate to affected downstream scene/render jobs and invalidate approvals that no longer match the revised version.
- Acceptance criteria: owner can review the storyboard before animation, revise a specific scene, approve the exact version, and see which downstream jobs are affected.

### 33.2 Episode and story continuity memory
- Maintain a structured, versioned series bible and episode continuity record.
- Track established world rules, character traits, relationships, goals, knowledge, emotional development, prior events, unresolved story threads, and relevant visual/audio constraints.
- When creating a new episode, retrieve and use relevant canon and prior episode facts; avoid contradictions, unexplained character knowledge, reset character development, or accidental changes to established rules.
- Distinguish approved canon from draft proposals and owner overrides.
- Provide a continuity review that flags likely contradictions and shows the relevant earlier episode or approved fact.
- Allow the owner to correct, accept, or explicitly override a continuity warning.
- Do not claim perfect memory or guarantee that every contradiction will be detected.
- Acceptance criteria: a new episode can use approved prior continuity, show detected conflicts before approval, and preserve owner-approved corrections.

### 33.3 Scene-level targeted revisions
- Support revisions scoped to a specific scene, shot, dialogue line, character, voice segment, or audio element wherever provider capabilities allow.
- The owner should be able to give natural-language feedback, such as “make this expression warmer,” “change the background,” or “shorten this dialogue,” and preview the proposed change.
- Reuse unaffected approved assets and completed stages; do not regenerate the entire episode by default.
- Show what will be regenerated, estimated time/cost when available, and which approvals will be invalidated before starting.
- Maintain immutable versions and a change history so the owner can compare revisions and restore a prior approved version.
- If a provider cannot support a narrow edit, clearly disclose the limitation and offer the closest supported workflow.
- Acceptance criteria: a localized change produces a new version of the affected scope, preserves unaffected work where feasible, and requires re-approval of changed output.

### 33.4 Cost estimates, budget limits, and usage tracking
- Show an estimated production cost before starting a job or episode, with a breakdown by relevant stages/providers (script, image, voice, animation, rendering, storage, and other applicable services).
- Clearly label estimates as estimates; show actual usage/cost after completion where provider data is available.
- Allow owner-configured budget limits per episode, project, time period, or provider, where technically supported.
- Warn before starting a job that may exceed the configured budget; require explicit confirmation to proceed beyond a hard limit.
- Track retries, failed jobs, provider usage, and avoidable regeneration so costs are transparent.
- Provide a cost dashboard and episode-level cost history; do not fabricate pricing or claim exact costs where provider billing data is unavailable.
- Acceptance criteria: owner can inspect an estimate before production, configure a limit, receive an over-budget warning, and compare estimated versus actual cost after production.

### 33.5 Production queue and resumable workflows
- Provide a persistent production queue for episodes, scenes, and jobs, including queued, running, waiting for approval, failed, canceled, and completed states.
- Show job progress, current stage, dependencies, retry status, estimated remaining time when available, and actionable error details.
- Support safe pause, resume, cancel, retry, and prioritization where provider capabilities permit.
- Persist workflow state so a server restart, provider timeout, or transient failure does not require restarting the entire episode.
- Use idempotent job handling, retry policies, and dependency tracking to prevent duplicate charges or duplicate publication.
- Allow preparation of later episodes while earlier episodes are rendering, subject to budget and concurrency limits.
- Keep publication as a separately gated action requiring owner approval of the exact final render and metadata.
- Acceptance criteria: jobs survive interruption, resume from the last valid completed stage where possible, expose errors and retry controls, and never publish without the required approval.

### 33.6 Integration requirements
These five capabilities must be connected rather than implemented as isolated screens:
- Storyboard approval gates full animation rendering.
- Continuity memory informs script and storyboard creation and is checked before owner approval.
- Targeted revisions update only affected workflow stages where possible and invalidate relevant downstream approvals.
- Cost estimates and budget limits apply to queue jobs before execution and to retries/regeneration.
- Queue state reflects dependencies, review gates, failures, revisions, and final publication state.
- Every approval must be tied to an immutable version identifier; edits to that version invalidate the corresponding approval.
- All actions and state transitions must be recorded in an audit trail.

### 33.7 End-to-end acceptance scenario
The implementation is not complete until the owner can:
1. Create a new episode using the approved series bible and continuity memory.
2. Review and revise the script and storyboard before full animation.
3. See an estimated cost and confirm that it fits the configured budget.
4. Start production and monitor the persistent queue.
5. Request a change to one scene without unnecessarily regenerating the entire episode.
6. Review the revised scene, see which approvals were invalidated, and approve the exact final version.
7. Publish only after the final owner approval, with the publishing action and result recorded.


## Section 34 — Owner decisions: YouTube audience analysis, configurable age targeting, all-language support, and integration into an existing project

These owner decisions are confirmed requirements and must be reflected in the product design and implementation plan.

### 34.1 YouTube channel and audience analysis
- Provide a YouTube analysis area that can inspect the connected channel's available analytics and content catalog, subject to YouTube API/OAuth permissions and data availability.
- Analyze published videos and available audience signals, including views, watch time, audience retention, traffic sources, geography, language, age-range information where YouTube exposes it, and other supported metrics.
- Clearly distinguish channel-specific first-party analytics from public competitor/video research. Do not imply that private analytics for other channels are available.
- Use analysis to recommend age ranges, topics, formats, episode lengths, languages, publishing cadence, and potential content improvements.
- Present evidence, date ranges, confidence/limitations, and rationale for recommendations. Do not promise views, virality, growth, or monetization.
- Recommendations must be owner-configurable and require owner review before changing the channel strategy or producing/publishing content.
- Provide refreshable reports and trend comparisons over available periods; respect YouTube API quotas, privacy, and policy restrictions.

### 34.2 Owner-configurable target age group
- The owner must be able to choose and change the intended audience age range from the panel at any time.
- Provide sensible age-range presets and a custom range/configuration where appropriate, without assuming that one setting fits every episode or channel.
- Use the selected age range to inform script complexity, vocabulary, pacing, story themes, emotional intensity, visual design, episode length recommendations, and parent-facing episode information.
- Allow an episode or series to override the channel default, with clear visibility of the selected target age range.
- The system may recommend an age range based on YouTube/channel analysis, but the owner remains in control and must confirm changes.
- Include safety and age-appropriateness checks against the selected target group; age targeting must not bypass child-safety or platform requirements.
- Acceptance criteria: owner can configure a default age group, override it for a series/episode, see how it affects production, and review the relevant checks before approval.

### 34.3 All-language support
- The product must be designed for multilingual operation across all languages supported by the selected AI providers and YouTube publishing/localization capabilities; do not hard-code a short list of languages as the product's limit.
- Support language selection for scripts, dialogue, voice generation, subtitles/captions, translated metadata, and localized episode descriptions where provider/platform support exists.
- Support one primary language and multiple additional language versions for a video, including alternate audio tracks and subtitles when supported by YouTube.
- Preserve character names, story canon, tone, age-appropriateness, and meaning during translation/localization.
- Show capability/quality availability by language and voice provider. Clearly disclose languages or features that are unsupported, unavailable, or lower-confidence.
- Do not promise native-quality voices or full YouTube localization support for every language; provider and platform capabilities must be verified at runtime/configuration.
- Acceptance criteria: owner can select any available supported language, generate localized assets and metadata, review them, and publish the supported language tracks/localizations without creating a separate channel by default.

### 34.4 Video duration default
- Set the default target duration for standard long-form episodes to 5–8 minutes.
- Allow the owner to adjust episode duration per series or episode.
- Story pacing and narrative completeness take priority over padding or forcing every episode to an exact duration.
- Shorts remain a separately configured output format and must not inherit the 5–8 minute default.
- Display planned and final duration in the script/storyboard/production/review flow.

### 34.5 Single-owner usage and existing-project integration
- The initial panel is for a single owner/user; team collaboration and role-based access are not required for the first release, but the architecture should not make later expansion unnecessarily difficult.
- This is not a standalone application that replaces the user's existing project. It must be added as a new panel/page/feature area inside the existing project.
- Before implementation, inspect the existing repository structure, framework, authentication, navigation/sidebar, design system, database conventions, API patterns, environment configuration, and deployment workflow.
- Add the new animation-studio panel page using the existing project's established architecture and visual conventions.
- Reuse existing authentication and layout; do not create a second login system or duplicate global navigation unless the repository clearly requires it.
- Keep new routes, components, services, database changes, and environment variables scoped and documented.
- Do not overwrite or refactor unrelated existing project functionality. Preserve current behavior and provide migration/rollback instructions for any database or configuration changes.
- Cursor must first map the existing project and propose an integration plan, then implement the new panel within that project.
- Acceptance criteria: the new panel appears in the existing application's navigation, is accessible through the existing authentication flow, and does not break existing pages or functionality.

### 34.6 Confirmed initial product defaults
- Initial usage: one owner.
- Initial channel architecture: one YouTube channel, extensible later.
- Standard long-form episode target: 5–8 minutes, adjustable.
- Languages: all languages supported by configured providers and YouTube localization features, with capability checks.
- Target age group: owner-configurable, informed by analysis and recommendations.
- YouTube analysis: required feature, using available authorized channel analytics and clearly labeled public research.
- Delivery: a new panel/page integrated into an existing project, not a separate standalone application.
