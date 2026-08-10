# Requirements Document

## Introduction

Smart Suite is a GEO (Generative Engine Optimization) platform that helps cross-border e-commerce sellers produce, optimize, and distribute content for AI search engines. The current UI is built with Streamlit and serves 7 functional pages (智库、智测、智造、智优、智布、智析、智中枢). This document defines requirements for migrating the frontend to Next.js (App Router) with a Protozoa-style design system, consuming the existing FastAPI backend via REST endpoints. The migration follows an incremental approach where the Streamlit version continues operating in parallel until the Next.js version achieves feature parity.

## Glossary

- **Frontend**: The Next.js 14+ application using App Router, deployed as the new user-facing interface
- **Backend**: The existing FastAPI server (`api/main.py`) that wraps `engine.py` into REST endpoints
- **Zhiku_Page**: The Knowledge Base page (智库) — manages AI search phrase expansion, selection, and curation
- **Zhice_Page**: The AI Search Journey Simulation page (智测) — tests phrases against AI platforms and displays coverage results
- **Zhixi_Page**: The Analytics Dashboard page (智析) — visualizes GEO metrics, citation tracking, and trend charts
- **Zhizao_Page**: The Content Production page (智造) — generates draft articles from selected phrases
- **Zhiyou_Page**: The Content Optimization page (智优) — scores and rewrites content for GEO compliance
- **Zhibu_Page**: The Content Distribution page (智布) — formats and exports content as structured JSON
- **Zhongshu_Page**: The Hub page (智中枢) — provides pipeline overview, batch management, and system status
- **Auth_System**: The user authentication and role-based permission system
- **Agent_Chat**: The conversational Agent interface for operating Smart Suite via natural language
- **API_Client**: The typed HTTP client layer in the Frontend that communicates with the Backend
- **Region_Config**: JSON-based configuration files defining per-region AI platforms, languages, and knowledge bases
- **Batch**: A named unit of work (e.g., batch_001) containing outputs from each pipeline step
- **Protozoa_Design**: The visual design language featuring glassmorphism, dark gradient backgrounds, accent glow effects, and compact data-dense layouts

## Requirements

### Requirement 1: Project Scaffolding and Architecture

**User Story:** As a developer, I want a well-structured Next.js project with shared components and API integration, so that each page module can be developed and deployed incrementally.

#### Acceptance Criteria

1. THE Frontend SHALL use Next.js 14 or later with App Router and TypeScript strict mode enabled
2. THE Frontend SHALL organize pages using the directory structure `/app/(dashboard)/zhiku`, `/app/(dashboard)/zhice`, `/app/(dashboard)/zhixi`, `/app/(dashboard)/zhizao`, `/app/(dashboard)/zhiyou`, `/app/(dashboard)/zhibu`, `/app/(dashboard)/zhongshu`
3. THE Frontend SHALL include a shared layout with sidebar navigation matching the pipeline flow order: 智库 → 智测 → 智造 → 智优 → 智布 → 智析 → 智中枢
4. THE API_Client SHALL use a typed HTTP client (fetch or axios) with base URL configurable via environment variable `NEXT_PUBLIC_API_URL`
5. IF the `NEXT_PUBLIC_API_URL` environment variable is not set, THEN THE API_Client SHALL default to `http://localhost:8000` and log a warning indicating the fallback
6. THE Frontend SHALL support concurrent operation with the existing Streamlit UI by connecting to the same Backend instance without data conflicts, using read-only access patterns for shared resources and batch-scoped writes
7. THE Frontend SHALL implement the Protozoa_Design system with dark gradient backgrounds (`#0a0a1a` to `#1a1a2e`), glassmorphism cards (backdrop-filter: blur(10px), semi-transparent borders), accent color `#00d4aa`, and responsive layouts adapting from 768px to 1920px viewport width
8. IF the API_Client receives no response from the Backend within 15 seconds, THEN THE API_Client SHALL abort the request, return a timeout error to the calling component, and allow retry

### Requirement 2: Knowledge Base Page (智库)

**User Story:** As a content operator, I want to expand seed words into AI search phrases and manage phrase selection, so that I can curate a high-quality phrase library for content production.

#### Acceptance Criteria

1. WHEN a user enters a seed word and clicks expand, THE Zhiku_Page SHALL call `POST /api/zhiku/expand` with the seed word, count (default 15, range 1–50), language, market, and batch_id parameters and display the returned phrases in a table sortable by any column header
2. THE Zhiku_Page SHALL display phrase data in a table with columns: ai_query, intent_type, priority_score, estimated_volume, category, is_selected, and created_at
3. WHEN a user selects or deselects phrases via checkbox, THE Zhiku_Page SHALL call `POST /api/zhiku/select` with the affected indices and immediately reflect the new selection state in the UI; IF the API call fails, THEN THE Zhiku_Page SHALL revert the checkbox to its previous state and display an error message indicating the selection could not be saved
4. THE Zhiku_Page SHALL support filtering phrases by category (dropdown of distinct values), intent_type (dropdown of distinct values), and priority_score (minimum threshold numeric input)
5. THE Zhiku_Page SHALL display a batch selector allowing users to switch between different batch contexts
6. WHEN phrases are loaded via `GET /api/zhiku/phrases`, THE Zhiku_Page SHALL pass the current user and batch_id as query parameters to enable region-based filtering
7. IF the `POST /api/zhiku/expand` call fails or returns an error, THEN THE Zhiku_Page SHALL display an error message indicating the expansion could not be completed and retain the seed word input so the user can retry
8. IF the loaded phrase list is empty (total equals 0), THEN THE Zhiku_Page SHALL display a placeholder message indicating no phrases exist for the current batch and prompting the user to expand a seed word

### Requirement 3: AI Search Journey Simulation Page (智测)

**User Story:** As a GEO strategist, I want to test search phrases against multiple AI platforms and see coverage results, so that I can identify content gaps and optimization opportunities.

#### Acceptance Criteria

1. THE Zhice_Page SHALL provide an input area for selecting a topic (free-text field), choosing one or more test platforms from the list (qianwen, deepseek, kimi, doubao, chatgpt, gemini), and specifying the number of phrases to generate via a bounded control with a minimum of 3 and a maximum of 30
2. WHEN a user initiates a test, THE Zhice_Page SHALL call `POST /api/zhice/verify` with the phrases and selected platforms and display a progress indicator showing the completion percentage of queries processed out of total queries
3. THE Zhice_Page SHALL display test results in a table showing: query, platform, has_official_link status (true if the AI answer text contains an Amazon domain reference), has_brand_mention status (true if the AI answer text contains "亚马逊" or "amazon"), and answer preview truncated to the first 30 characters
4. THE Zhice_Page SHALL compute and display gap analysis including: total queries tested, coverage rate (percentage of query-platform pairs where has_official_link is true divided by total query-platform pairs), and a list of uncovered queries (where has_official_link is false) marked as opportunities
5. THE Zhice_Page SHALL support a multi-step workflow with navigation across five sequential steps: execute test → opportunity analysis → execute opportunities → status display → closed-loop dashboard
6. WHEN test results contain gaps (queries where has_official_link is false), THE Zhice_Page SHALL allow users to confirm gaps as opportunities and proceed to the execution step
7. IF all query-platform pairs return has_official_link as true (zero gaps), THEN THE Zhice_Page SHALL display a success message indicating full coverage with no action required
8. IF an API call to a selected platform fails during test execution, THEN THE Zhice_Page SHALL record the failure for that query-platform pair, continue processing remaining pairs, and display the failed pair with an error indicator in the results table

### Requirement 4: Analytics Dashboard Page (智析)

**User Story:** As a team lead, I want to visualize GEO performance metrics including weekly trends, monthly comparisons, and citation tracking, so that I can report on output and identify growth areas.

#### Acceptance Criteria

1. THE Zhixi_Page SHALL display weekly trend data by calling `GET /api/zhixi/monthly` and rendering line charts showing Reg Start values over time for CN GEO, WW GEO, and WW Direct channels, with each channel as a distinct line series
2. THE Zhixi_Page SHALL display metric summary cards showing: YTD totals, YoY growth percentages, and WoW change percentages with color-coded indicators — green for values greater than zero, red for values less than zero, and neutral (grey) for values equal to zero
3. THE Zhixi_Page SHALL display citation tracking data by calling `GET /api/zhixi/citations` and rendering a table with columns sortable by clicking column headers, where the table displays gap verification results including phrase, platform, citation status, and verification date
4. WHEN the `GET /api/zhixi/monthly`, `GET /api/zhixi/citations`, or `GET /api/zhixi/summary` endpoint returns an empty data array, THE Zhixi_Page SHALL display an empty-state message indicating no data is available for that section instead of rendering an empty chart or table
5. WHEN the summary endpoint `GET /api/zhixi/summary` returns data, THE Zhixi_Page SHALL display GEO input activity metrics including: total phrase count, total content count, and number of AI platforms with at least one verified citation (platform coverage count)
6. IF any `GET /api/zhixi/*` endpoint returns an error or fails to respond within 10 seconds, THEN THE Zhixi_Page SHALL display an error indicator in the affected section and retain any previously loaded data for that section

### Requirement 5: Content Production and Optimization Pages (智造 + 智优)

**User Story:** As a content producer, I want to generate draft content from selected phrases and then score and optimize that content, so that articles are GEO-compliant and likely to be cited by AI engines.

#### Acceptance Criteria

1. WHEN a user clicks generate on the Zhizao_Page, THE Zhizao_Page SHALL call `POST /api/zhizao/generate` with batch_id, content_limit, content_language, and template_id, and display a progress indicator that remains visible until the response is received or a 120-second timeout elapses
2. WHEN generation completes successfully, THE Zhizao_Page SHALL display generated drafts in an expandable list showing: ai_query, title, word_count, and a preview of content_draft truncated to the first 200 characters
3. WHEN a user triggers scoring on the Zhiyou_Page, THE Zhiyou_Page SHALL call `POST /api/zhiyou/score` and display a scorecard with per-article scores across five dimensions (intent_match, ai_readability, authority, actionability, differentiation) each on a 1–5 scale, an overall weighted score, and a compliance status of PASS (overall_score ≥ 4.5 and intent_match ≥ 4 and authority ≥ 4) or FAIL
4. WHEN a user triggers optimization on the Zhiyou_Page, THE Zhiyou_Page SHALL call `POST /api/zhiyou/optimize` with batch_id and content_language, and display a before/after content comparison showing original score, optimized score, and a list of specific changes applied
5. THE Zhizao_Page SHALL support template selection from available templates: auto, registration, fees, logistics, advertising, listing
6. WHEN optimization completes, THE Zhiyou_Page SHALL display optimization results showing: original overall score, optimized overall score, a list of changes applied (each as a brief description), and compliance check status (PASS or FAIL with the failing dimension identified)
7. IF the `POST /api/zhizao/generate`, `POST /api/zhiyou/score`, or `POST /api/zhiyou/optimize` call fails or times out after 120 seconds, THEN THE respective page SHALL dismiss the progress indicator, display an error message indicating the operation that failed, and retain any previously displayed content unchanged
8. IF scoring returns a FAIL compliance status for one or more articles, THEN THE Zhiyou_Page SHALL visually distinguish failed articles from passed articles and enable the optimization action only for articles with FAIL status

### Requirement 6: Content Distribution and Hub Pages (智布 + 智中枢)

**User Story:** As a content manager, I want to format optimized content for distribution and monitor the overall pipeline status, so that I can track batch progress and export publish-ready content.

#### Acceptance Criteria

1. THE Zhibu_Page SHALL display formatted content output by loading the batch's `04_zhibu/zhibu_output.json` via a Backend endpoint, showing each item with its `meta.title`, the first 200 characters of the `body` field as content preview, and metadata including `compliance.status`, `ai_friendly.overall_score`, and `quality_metrics.word_count`
2. THE Zhibu_Page SHALL provide an export function that downloads the complete `zhibu_output.json` file (containing all items for the selected batch) for external publishing systems
3. IF the batch's `04_zhibu/zhibu_output.json` does not exist or contains zero items, THEN THE Zhibu_Page SHALL display an empty-state message indicating that no distribution content is available for the selected batch
4. THE Zhongshu_Page SHALL display pipeline status for each batch showing completion status of each step (智库, 智造, 智优, 智布), where a step is considered complete when its folder contains at least one output file (`.csv` or `.json`)
5. THE Zhongshu_Page SHALL display a batch selector listing all available batches and show file counts per step with a progress indicator displaying the number of completed steps out of 4 total steps
6. THE Zhongshu_Page SHALL show a pipeline flow visualization as a horizontal sequence of the 4 pipeline steps with the currently active step visually highlighted using a distinct border and background color

### Requirement 7: User Authentication and Permissions

**User Story:** As a system administrator, I want to control user access with login-based authentication and region-based permissions, so that each user sees data appropriate to their role and region.

#### Acceptance Criteria

1. WHEN a user accesses the Frontend without an active session, THE Auth_System SHALL display a login prompt requiring a user identifier before granting access to any dashboard page
2. WHEN a user submits their identifier, THE Auth_System SHALL call `GET /api/auth/check` with the user identifier and receive a JSON response containing allowed status (boolean), region (string), sub_region (string), and is_admin flag (boolean)
3. WHILE a user is authenticated, THE Auth_System SHALL store the session information (user, region, sub_region, is_admin) in a client-side state management solution and include the user identifier in subsequent API calls
4. IF the auth check returns allowed=false, THEN THE Auth_System SHALL display an access denied message and prevent navigation to dashboard pages
5. IF the auth check API endpoint is unreachable or returns no response within 10 seconds, THEN THE Auth_System SHALL display a connection error message and prevent access to dashboard pages until a successful auth check is completed
6. WHILE a user has is_admin=false, THE Auth_System SHALL hide all administrative functions, specifically: user management, batch deletion, and the admin approval panel
7. WHEN a user is successfully authenticated, THE Auth_System SHALL load Region_Config for the authenticated user's region to determine available AI platforms, content languages, and default seeds
8. IF no user interaction occurs for 8 hours, THEN THE Auth_System SHALL expire the session and require re-authentication on the next user action

### Requirement 8: Internationalization Support

**User Story:** As a user in different language regions, I want the UI to display in my preferred language, so that I can operate the system comfortably in Chinese, English, Korean, or Vietnamese.

#### Acceptance Criteria

1. THE Frontend SHALL support UI languages: en, zh-CN, zh-TW, ko, vi, ensuring that every visible UI element (labels, buttons, navigation items, tooltips, placeholder text, and system messages) has a translation string defined for each of the five language codes
2. THE Frontend SHALL load translation strings from a single JSON file following the existing `i18n_strings.json` key-per-string structure, where each top-level key maps to an object containing one value per supported language code (en, zh-CN, zh-TW, ko, vi)
3. WHEN a user's region is determined via Auth_System, THE Frontend SHALL set the default UI language based on Region_Config's `ui_language` field and apply it immediately without requiring a page reload
4. THE Frontend SHALL provide a language switcher component in the sidebar listing all five supported UI languages (English, 简体中文, 繁體中文, 한국어, Tiếng Việt), allowing manual language override that takes effect immediately upon selection
5. WHEN a user selects a language via the language switcher, THE Frontend SHALL persist the selection in the user's profile (users.json `user_lang` field) so the preference is retained across sessions and used on subsequent logins instead of the Region_Config default
6. IF a translation key has no value defined for the active UI language, THEN THE Frontend SHALL fall back to the English (en) value for that key and render it without error
7. IF the Region_Config's `ui_language` field is missing, empty, or contains a language code not in the supported set (en, zh-CN, zh-TW, ko, vi), THEN THE Frontend SHALL default to English (en) and log a warning indicating the invalid value and region code

### Requirement 9: Agent Chat Mode

**User Story:** As a power user, I want to interact with Smart Suite through natural language conversation, so that I can execute pipeline operations without navigating individual pages.

#### Acceptance Criteria

1. THE Agent_Chat SHALL provide a chat interface accessible from a collapsible side panel (visible on all pages) or a dedicated route within the Frontend, retaining visibility during navigation between pages
2. WHEN a user sends a message of up to 2000 characters, THE Agent_Chat SHALL forward the message to a Backend chat endpoint and stream the response with the first token appearing within 3 seconds of submission
3. WHEN a user's message expresses intent to invoke a pipeline action (expanding phrases via 智库, running tests via 智测, generating content via 智造, or scoring content via 智优), THE Agent_Chat SHALL identify the target action, execute it against the active batch, and display a confirmation indicating which action was triggered and its completion status
4. WHEN the Backend returns structured data (containing tabular rows, chart datasets, or key-value status fields), THE Agent_Chat SHALL render the corresponding structured output (table, chart, or status card) inline within the chat conversation
5. IF the Backend chat endpoint is unreachable or the streaming connection is interrupted, THEN THE Agent_Chat SHALL display an error message indicating the failure reason, preserve the user's unsent or in-progress message in the input field, and allow retry without re-typing
6. THE Agent_Chat SHALL maintain a conversation history of at least the 50 most recent message pairs (user + assistant) within the current session to provide context for multi-turn interactions

### Requirement 10: Real-Time Data and Responsive Design

**User Story:** As a user working across desktop and tablet devices, I want the interface to be responsive and show live data updates, so that I can monitor pipeline progress without manual refreshes.

#### Acceptance Criteria

1. THE Frontend SHALL implement responsive layouts that adapt to viewport widths from 768px (tablet) to 1920px (desktop) without horizontal scrolling, and SHALL scale content proportionally at intermediate widths between these bounds
2. WHILE a backend operation has been running for more than 2 seconds without a response, THE Frontend SHALL display a visible progress indicator and poll the Backend for status updates at intervals no greater than 5 seconds until the operation completes or fails
3. THE Frontend SHALL use client-side state management (React Context or Zustand) to maintain pipeline state across page navigations, re-fetching from the Backend only when the local state is absent or explicitly invalidated by a user action
4. IF a network request to the Backend fails or exceeds a 15-second timeout, THEN THE Frontend SHALL display an error message indicating the nature of the failure, provide a retry option allowing up to 3 retry attempts, and preserve all form field values the user has entered prior to the failure
5. IF all retry attempts for a failed network request are exhausted, THEN THE Frontend SHALL disable the retry option and display a message directing the user to check connectivity or try again later
