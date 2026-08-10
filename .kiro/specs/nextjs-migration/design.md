# Technical Design Document

## Overview

This document describes the technical architecture for migrating Smart Suite's frontend from Streamlit to Next.js 14 (App Router). The new frontend is a standalone SPA that consumes the existing FastAPI backend (`api/main.py`) via REST. It runs in parallel with Streamlit until feature parity is achieved.

## Architecture

### System Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Browser                            │
│  ┌───────────────────────────────────────────────────────┐  │
│  │             Next.js Frontend (App Router)              │  │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐             │  │
│  │  │ Auth     │ │ i18n     │ │ Theme    │  Global      │  │
│  │  │ Context  │ │ Provider │ │ Provider │  Providers   │  │
│  │  └──────────┘ └──────────┘ └──────────┘             │  │
│  │  ┌─────────────────────────────────────────────────┐ │  │
│  │  │            (dashboard) Layout                    │ │  │
│  │  │  ┌──────┐ ┌──────────────────────────────────┐ │ │  │
│  │  │  │Sidebar│ │        Page Content              │ │ │  │
│  │  │  │ Nav   │ │  zhiku|zhice|zhizao|zhiyou|...  │ │ │  │
│  │  │  └──────┘ └──────────────────────────────────┘ │ │  │
│  │  │  ┌──────────────────────────────────────────┐   │ │  │
│  │  │  │        Agent Chat Panel (collapsible)    │   │ │  │
│  │  │  └──────────────────────────────────────────┘   │ │  │
│  │  └─────────────────────────────────────────────────┘ │  │
│  └───────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                            │ HTTP (REST)
                            ▼
┌─────────────────────────────────────────────────────────────┐
│              FastAPI Backend (api/main.py)                    │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────────┐  │
│  │ /api/auth│ │/api/zhiku│ │/api/zhice│ │/api/zhizao   │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────────┘  │
│  ┌──────────┐ ┌──────────┐ ┌──────────────────────────┐   │
│  │/api/zhiyou│ │/api/zhixi│ │      engine.py           │   │
│  └──────────┘ └──────────┘ └──────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                   File System (output/)                       │
│  output/batch_001/01_zhiku/ | 02_zhizao/ | 03_zhiyou/ | ... │
│  output/metrics/ | output/users.json | config/regions/*.json │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack

| Layer | Choice | Rationale |
|-------|--------|-----------|
| Framework | Next.js 14+ (App Router) | Server components, file-based routing, TypeScript-first |
| Language | TypeScript (strict) | Type safety for API contracts |
| Styling | Tailwind CSS + CSS Variables | Utility-first, easy theming for Protozoa design |
| State | Zustand | Lightweight, works with RSC, no boilerplate |
| HTTP Client | Native fetch + typed wrapper | No extra dependency, supports streaming |
| Charts | Recharts | React-native, declarative, good TypeScript support |
| UI Components | Custom (Protozoa) + Radix primitives | Accessibility-compliant, unstyled base |
| i18n | Custom hook + JSON strings | Match existing `i18n_strings.json` format |
| Package Manager | pnpm | Fast, disk-efficient |

### Directory Structure

```
frontend/
├── app/
│   ├── layout.tsx                   # Root layout (html, body, providers)
│   ├── page.tsx                     # Redirect to /zhiku or login
│   ├── login/
│   │   └── page.tsx                 # Login page
│   ├── (dashboard)/
│   │   ├── layout.tsx               # Dashboard shell (sidebar + main + chat panel)
│   │   ├── zhiku/page.tsx           # 智库 - Knowledge Base
│   │   ├── zhice/page.tsx           # 智测 - AI Search Verification
│   │   ├── zhizao/page.tsx          # 智造 - Content Production
│   │   ├── zhiyou/page.tsx          # 智优 - Content Optimization
│   │   ├── zhibu/page.tsx           # 智布 - Content Distribution
│   │   ├── zhixi/page.tsx           # 智析 - Analytics Dashboard
│   │   └── zhongshu/page.tsx        # 智中枢 - Pipeline Hub
├── components/
│   ├── layout/
│   │   ├── Sidebar.tsx
│   │   ├── PipelineFlow.tsx
│   │   └── ChatPanel.tsx
│   ├── ui/
│   │   ├── GlassCard.tsx
│   │   ├── DataTable.tsx
│   │   ├── MetricCard.tsx
│   │   ├── ProgressBar.tsx
│   │   ├── BatchSelector.tsx
│   │   ├── Button.tsx
│   │   ├── Input.tsx
│   │   ├── Select.tsx
│   │   ├── Modal.tsx
│   │   └── Toast.tsx
│   └── charts/
│       ├── TrendLineChart.tsx
│       └── CoverageChart.tsx
├── lib/
│   ├── api-client.ts
│   ├── types.ts
│   ├── constants.ts
│   └── utils.ts
├── stores/
│   ├── auth-store.ts
│   ├── batch-store.ts
│   ├── pipeline-store.ts
│   └── i18n-store.ts
├── hooks/
│   ├── useAuth.ts
│   ├── useApiCall.ts
│   ├── useI18n.ts
│   └── usePolling.ts
├── i18n/
│   └── strings.json
├── styles/
│   └── globals.css
├── next.config.js
├── tailwind.config.ts
├── tsconfig.json
├── package.json
└── .env.local
```

## Components and Interfaces

### API Client Interface

```typescript
// lib/api-client.ts
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface ApiOptions {
  timeout?: number;      // default 15000ms
  retries?: number;      // default 3
}

interface ApiError {
  status: number;
  message: string;
  isTimeout: boolean;
  retriesExhausted: boolean;
}

async function apiGet<T>(path: string, params?: Record<string, string>, opts?: ApiOptions): Promise<T>;
async function apiPost<T>(path: string, body: unknown, opts?: ApiOptions): Promise<T>;
async function apiStream(path: string, body: unknown): AsyncGenerator<string>;
```

### Core UI Component Interfaces

```typescript
// GlassCard
interface GlassCardProps {
  children: React.ReactNode;
  className?: string;
  glow?: boolean;
  padding?: 'sm' | 'md' | 'lg';
}

// DataTable
interface ColumnDef<T> {
  key: keyof T;
  header: string;
  sortable?: boolean;
  render?: (value: T[keyof T], row: T) => React.ReactNode;
}

interface DataTableProps<T> {
  data: T[];
  columns: ColumnDef<T>[];
  sortable?: boolean;
  filterable?: boolean;
  selectable?: boolean;
  onSelectionChange?: (indices: number[]) => void;
  emptyMessage?: string;
  loading?: boolean;
}

// MetricCard
interface MetricCardProps {
  label: string;
  value: string | number;
  change?: number;
  changeLabel?: string;
  trend?: 'up' | 'down' | 'flat';
}

// BatchSelector
interface BatchSelectorProps {
  batches: string[];
  active: string;
  onChange: (batchId: string) => void;
}

// PipelineFlow
interface PipelineStep {
  id: string;
  label: string;
  status: 'complete' | 'active' | 'pending';
  fileCount?: number;
}

interface PipelineFlowProps {
  steps: PipelineStep[];
  activeStep?: string;
}
```

### Zustand Store Interfaces

```typescript
// auth-store.ts
interface AuthState {
  user: string | null;
  region: string;
  subRegion: string;
  isAdmin: boolean;
  isAuthenticated: boolean;
  lastActivity: number;
  login: (user: string) => Promise<void>;
  logout: () => void;
  touch: () => void;  // update lastActivity
}

// batch-store.ts
interface BatchState {
  activeBatch: string;
  batches: string[];
  setActiveBatch: (id: string) => void;
  fetchBatches: () => Promise<void>;
}

// pipeline-store.ts
interface PipelineState {
  status: Record<string, PipelineStep[]>;
  fetchStatus: (batchId: string) => Promise<void>;
  invalidate: (batchId: string) => void;
}

// i18n-store.ts
interface I18nState {
  locale: string;
  strings: Record<string, Record<string, string>>;
  setLocale: (locale: string) => void;
  t: (key: string) => string;
  loadStrings: () => Promise<void>;
}
```

### Hook Interfaces

```typescript
// useApiCall.ts
interface UseApiCallReturn<T> {
  data: T | null;
  loading: boolean;
  error: ApiError | null;
  execute: (...args: unknown[]) => Promise<T>;
  retry: () => Promise<T>;
  canRetry: boolean;
}

// usePolling.ts
interface UsePollingOptions {
  url: string;
  interval?: number;    // default 5000ms
  enabled: boolean;
  onData: (data: unknown) => void;
  onComplete: () => void;
}
```

## Data Models

### API Request/Response Types

```typescript
// Auth
interface AuthResponse {
  allowed: boolean;
  user: string;
  region?: string;
  sub_region?: string;
  is_admin?: boolean;
}

// Zhiku
interface SeedExpansionRequest {
  seed_word: string;
  count: number;         // 1–50, default 15
  language: string;      // "zh-CN" | "en"
  market: string;        // "CN" | "NA" | "EU" | "JP" | "ROA"
  batch_id: string;
}

interface PhraseData {
  ai_query: string;
  intent_type: string;
  priority_score: number;
  estimated_volume: number;
  category: string;
  is_selected: string;    // "TRUE" | "FALSE"
  created_at: string;
}

interface PhraseListResponse {
  phrases: PhraseData[];
  total: number;
}

// Zhice
interface ZhiceRequest {
  phrases: string[];
  platforms: string[];
  user: string;
}

interface ZhiceResult {
  query: string;
  platform: string;
  has_official_link: boolean;
  has_brand_mention: boolean;
  answer_preview: string;
  error?: string;
}

// Zhizao
interface ZhizaoRequest {
  batch_id: string;
  content_limit: number;
  content_language: string;
  template_id: string;   // "auto" | "registration" | "fees" | "logistics" | "advertising" | "listing"
}

interface DraftContent {
  ai_query: string;
  title: string;
  word_count: number;
  content_draft: string;
}

// Zhiyou
interface ZhiyouRequest {
  batch_id: string;
  content_language: string;
}

interface ScoreResult {
  ai_query: string;
  intent_match: number;       // 1–5
  ai_readability: number;     // 1–5
  authority: number;          // 1–5
  actionability: number;      // 1–5
  differentiation: number;    // 1–5
  overall_score: number;
  compliance_status: 'PASS' | 'FAIL';
}

// Zhixi
interface MonthlyMetric {
  month: string;
  cn_geo: number;
  ww_geo: number;
  ww_direct: number;
}

interface CitationRecord {
  phrase: string;
  platform: string;
  citation_status: string;
  verification_date: string;
}

// Region Config
interface RegionConfig {
  region_code: string;
  display_name: string;
  ui_language: string;
  ai_platforms: {
    default_selected: string[];
    available: string[];
  };
  official_links: string[];
  knowledge_base_paths: string[];
  default_seeds: string[];
  verification_platforms: string[];
  content_languages: { code: string; name: string }[];
}
```

## Error Handling

| Scenario | HTTP Status | Frontend Behavior |
|----------|-------------|-------------------|
| API timeout | N/A (aborted) | Show error toast "Request timed out", enable retry button |
| Server error | 500 | Show error toast with `detail` message from response |
| Not found | 404 | Show empty state ("No data for this batch") |
| Auth rejected | 200 (allowed=false) | Show "Access Denied", stay on login |
| Auth endpoint down | Network error | Show "Cannot connect to server", prevent dashboard access |
| Long op timeout (120s) | N/A (aborted) | Show "Generation timed out", retain form, enable retry |
| Network offline | Network error | Show persistent banner "No connection", auto-retry when online |
| Session expired (8h) | Client-side check | Clear auth store, redirect to `/login`, preserve URL |

Retry policy: up to 3 attempts with exponential backoff (1s, 2s, 4s). After exhaustion, disable retry and show connectivity guidance.

## Correctness Properties

### Property 1: Optimistic UI Consistency
When a phrase selection checkbox is toggled, the UI updates immediately. If the backend call fails, the checkbox reverts to its previous state within 1 second, ensuring the displayed state always reflects the actual persisted state.
**Validates: Requirements 2.3**

### Property 2: Data Isolation
Each page loads data scoped to the active batch in `batch-store`. Switching batches invalidates stale data and triggers fresh fetches, ensuring no cross-batch data leakage.
**Validates: Requirements 1.6**

### Property 3: Auth Boundary
No dashboard page renders content before `auth-store.isAuthenticated` is confirmed true. The dashboard layout acts as a synchronous gate — unauthenticated requests redirect before any child route renders.
**Validates: Requirements 7.1**

### Property 4: i18n Completeness
The `t(key)` function always returns a string (never undefined). If a key is missing for the current locale, it falls back to English. If missing in English too, it returns the raw key string to prevent UI breakage.
**Validates: Requirements 8.6**

### Property 5: Concurrent Safety
The Next.js frontend performs only batch-scoped writes (phrase selection within a batch). It does not modify shared output files outside the active batch context, preventing conflicts with the parallel Streamlit instance.
**Validates: Requirements 1.5**

### Property 6: Progress Indicator Truthfulness
A progress indicator is shown if and only if an operation is in-flight. It is dismissed on success, failure, or timeout — never left spinning indefinitely.
**Validates: Requirements 10.2**

## Testing Strategy

| Level | Tool | Coverage |
|-------|------|----------|
| Unit | Vitest | Zustand stores, utility functions, API client (mocked fetch) |
| Component | Vitest + React Testing Library | UI components render correctly, handle props |
| Integration | Playwright | Full page flows: login → expand → select → generate |
| Visual | Manual | Protozoa design compliance at all breakpoints |
| E2E | Playwright | Complete pipeline flow against running FastAPI backend |

Key test scenarios:
- Auth flow: valid user → dashboard, invalid user → denied, timeout → error
- Zhiku: expand → table renders, select → optimistic update, select fail → revert
- Zhice: run test → progress → results, handle partial failures
- Responsive: all pages at 768px, 1024px, 1920px without overflow
- i18n: switch languages, verify all strings update, verify fallback
