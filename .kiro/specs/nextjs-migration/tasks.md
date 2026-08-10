# Implementation Plan:

## Overview

This plan covers the full Next.js migration for Smart Suite, organized into 17 tasks across 7 phases. Tasks are ordered by dependency — foundational infrastructure first, then pages by priority (智库 → 智测 → 智析 → 智造/智优 → 智布/智中枢 → Agent Chat → Polish).

## Task Dependency Graph

```json
{
  "waves": [
    [1],
    [2],
    [3],
    [4, 16],
    [5],
    [6, 7],
    [8, 9, 10, 11, 12, 13, 14, 15],
    [17]
  ]
}
```

## Tasks

- [ ] 1. Initialize Next.js project with App Router, TypeScript strict, Tailwind CSS, pnpm. Configure `tailwind.config.ts` with Protozoa theme (accent `#00d4aa`, dark gradients, glow shadows). Create `styles/globals.css` with CSS variables. Create `.env.local` with `NEXT_PUBLIC_API_URL`. Install deps: zustand, recharts, @radix-ui/react-dialog, @radix-ui/react-dropdown-menu, @radix-ui/react-checkbox. Verify builds and runs on localhost:3000. [Requirement 1: AC 1, 7]
- [ ] 2. Create `lib/types.ts` with all API request/response TypeScript interfaces. Create `lib/api-client.ts` with typed fetch wrapper (configurable base URL, 15s timeout, 3 retries, X-User header). Create `lib/constants.ts` and `lib/utils.ts`. Implement fallback to localhost:8000 with console warning. [Requirement 1: AC 4, 5, 8; Requirement 10: AC 4, 5]
- [ ] 3. Create Zustand stores: `auth-store.ts` (user, region, isAdmin, login/logout, 8h timeout), `batch-store.ts` (activeBatch, batches, fetch), `pipeline-store.ts` (per-batch status), `i18n-store.ts` (locale, strings, t() with English fallback). [Requirement 7: AC 3, 8; Requirement 8: AC 6; Requirement 10: AC 3]
- [ ] 4. Create shared UI components: GlassCard, Button (primary/secondary/danger), Input, Select (Radix), Modal (Radix Dialog), Toast, ProgressBar, MetricCard (green/red/grey trend), DataTable (sortable, filterable, selectable with optimistic updates, loading skeleton, empty state), BatchSelector. [Requirement 1: AC 7; Requirement 10: AC 1, 2]
- [ ] 5. Create `app/(dashboard)/layout.tsx` with auth guard redirect. Create `Sidebar.tsx` with nav items in order (智库→智测→智造→智优→智布→智析→智中枢), active highlighting, language switcher, logout. Create `PipelineFlow.tsx` horizontal step indicator. Implement responsive collapse (240px desktop, 64px tablet). [Requirement 1: AC 2, 3; Requirement 10: AC 1]
- [ ] 6. Create `app/login/page.tsx` with identifier input. On submit call `GET /api/auth/check`. Handle success (store session, load region config, redirect to /zhiku), failure (show denied), timeout (show connection error). Implement 8h inactivity expiry. Create `useAuth.ts` hook. Hide admin UI when is_admin=false. [Requirement 7: AC 1–8]
- [ ] 7. Create `i18n/strings.json` with keys for all UI elements across 5 languages (en, zh-CN, zh-TW, ko, vi). Create `useI18n.ts` hook. Set default locale from region config on auth. Build language switcher (5 options). Persist preference. Fallback to English for missing keys. Handle invalid ui_language with English default + warning. [Requirement 8: AC 1–7]
- [ ] 8. Build 智库 page: SeedExpander (input, count 1–50, language, market, expand button → POST /api/zhiku/expand). PhraseTable (DataTable with ai_query, intent_type, priority_score, estimated_volume, category, is_selected, created_at). Column sorting, filter controls (category/intent dropdowns, priority threshold). Checkbox selection → POST /api/zhiku/select with optimistic UI + revert on failure. Load via GET /api/zhiku/phrases. Empty state and error handling. [Requirement 2: AC 1–8]
- [ ] 9. Build 智测 page: TestConfig (topic input, platform multi-select from 6 options, phrase count 3–30). WorkflowStepper (5 sequential steps). POST /api/zhice/verify with progress bar. ResultsTable (query, platform, has_official_link, has_brand_mention, answer preview 30 chars). Gap analysis (total tested, coverage rate %, opportunity list). Handle zero gaps (success message) and per-platform failures (error indicator, continue others). [Requirement 3: AC 1–8]
- [ ] 10. Build 智析 page: TrendLineChart (Recharts, GET /api/zhixi/monthly, CN GEO + WW GEO + WW Direct lines). MetricCards row (YTD, YoY%, WoW% with green/red/grey). CitationTable (GET /api/zhixi/citations, sortable columns). InputSummary (GET /api/zhixi/summary, phrase count, content count, platform coverage). Empty state per section. Error handling retains previous data. [Requirement 4: AC 1–6]
- [ ] 11. Build 智造 page: GenerateForm (batch, content_limit, language, template dropdown: auto/registration/fees/logistics/advertising/listing). POST /api/zhizao/generate with 120s timeout + progress indicator. DraftList (expandable items: ai_query, title, word_count, preview 200 chars). Handle timeout and error (dismiss progress, show error, retain form). [Requirement 5: AC 1, 2, 5, 7]
- [ ] 12. Build 智优 page: Scoring (POST /api/zhiyou/score → scorecard with 5 dimensions 1–5, overall score, PASS/FAIL). Visual distinction PASS (green) vs FAIL (red). Enable optimize only for FAIL articles. Optimization (POST /api/zhiyou/optimize → before/after comparison, score change, changes list). Handle timeout/error. [Requirement 5: AC 3, 4, 6, 7, 8]
- [ ] 13. Build 智布 page: Load zhibu_output.json via backend. Display items (meta.title, body preview 200 chars, compliance.status, overall_score, word_count). Export button (download JSON). Empty state for missing/empty data. [Requirement 6: AC 1, 2, 3]
- [ ] 14. Build 智中枢 page: Batch selector listing all batches. Pipeline flow visualization (4 horizontal steps: 智库→智造→智优→智布, active step highlighted). Per-step file counts and completion status (≥1 .csv/.json = complete). Progress indicator (X/4 steps). Batch grid/list with progress. [Requirement 6: AC 4, 5, 6]
- [ ] 15. Build Agent Chat panel: Collapsible right panel (400px) with toggle button on all pages. Message list (user/assistant bubbles). Input area (2000 char limit). Streaming response via ReadableStream. Pipeline action detection → execute against active batch → confirmation. Structured data rendering inline (tables, cards). Error handling (preserve input, allow retry). Maintain 50 message pairs in session. [Requirement 9: AC 1–6]
- [ ] 16. Create `usePolling.ts` hook (poll URL every 5s while enabled). Create `useApiCall.ts` hook (loading, error, execute, retry, canRetry). Show progress after 2s of no response. Retry up to 3 attempts then disable with connectivity message. Integrate with zhizao and zhice pages. [Requirement 10: AC 2, 4, 5]
- [ ] 17. Responsive QA: Test all pages at 768px, 1024px, 1440px, 1920px. Verify sidebar collapse. Verify no horizontal scroll. Verify charts/tables scale. Verify ChatPanel layout. Verify all strings translated (5 languages). Full flow test (login → expand → verify → generate → score → optimize → distribute). Verify concurrent Streamlit+Next.js operation. Verify error states with backend disconnected. [Requirement 1: AC 6; Requirement 8: AC 1; Requirement 10: AC 1]

## Notes

- Tasks 8–14 (page implementations) can be developed in parallel once Tasks 1–6 are complete
- Task 15 (Agent Chat) requires a backend streaming endpoint that may need to be added to `api/main.py`
- Task 16 (Polling) can be developed alongside page tasks as utility infrastructure
- The Streamlit version remains operational throughout — no downtime during migration
