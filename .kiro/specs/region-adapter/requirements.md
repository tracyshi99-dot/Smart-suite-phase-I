# Requirements Document

## Introduction

Region Adapter 是 Smart Suite 的区域配置适配层，实现基于用户 `user_region`（ROA / CN / NA / EU）自动加载差异化配置的能力。每个 region 拥有独立的配置文件，定义该区域的 AI 检索平台、官方链接标准、知识库文件、Ahrefs report_id、默认种子短语（seeds）和验证平台。用户登录后系统自动匹配其 admin 分配的 region 配置（支持手动切换），Admin 审批界面增加 region 筛选维度。

**Region 体系说明：**
- **CN**：中国大陆用户，使用国内+国际 AI 平台，中文界面
- **ROA** (Rest of Asia)：原 TW / KR / VN 用户统一归入，英文界面，WW AI 平台。ROA 内部保留 sub_region 字段（TW/KR/VN）供后续细分，用户可自行选择 sub_region
- **NA**：北美用户（如 quadaisy），英文界面，WW AI 平台
- **EU**：欧洲用户（如 mbudhira），英文界面，WW AI 平台

所有非 CN 用户（ROA/NA/EU）看到的界面逻辑一致：英文、ChatGPT/Gemini/Perplexity/Grok 平台、对应 region 的官方链接和种子短语。

## Glossary

- **Region_Adapter**: 区域配置适配模块，负责加载、解析和提供区域差异化配置
- **Region_Config**: 单个区域的 JSON 配置文件，包含该区域所有差异化参数
- **User_Region**: 用户所属区域标识，存储在 users.json 的 user_region 字段中，取值为 ROA / CN / NA / EU
- **Sub_Region**: ROA 用户的细分区域标识（TW / KR / VN），存储在 users.json 的 user_sub_region 字段中，用于 official_links 和 seeds 的进一步差异化
- **Active_Region**: 用户当前生效的区域，默认为 admin 分配的 User_Region，但用户可手动切换到其他 region
- **Smart_Suite**: 整体系统，包含 FastAPI 后端、Streamlit UI 和内容生产流水线
- **Admin_Panel**: Streamlit UI 中的管理员审批界面
- **Zhice_Module**: 智测模块，AI 搜索旅程模拟引擎
- **Zhiku_Module**: 智库模块，检索短语生成引擎
- **AI_Platform_List**: 某区域对应的 AI 检索平台集合（CN 同时使用国内平台 DeepSeek/Doubao/Kimi/Yuanbao/Qianwen 和国际平台 ChatGPT/Gemini/Perplexity/Grok；ROA/NA/EU 统一使用 ChatGPT/Gemini/Perplexity/Grok）
- **Official_Links**: 各区域的亚马逊官方卖家门户链接列表（如 TW 为 sell.amazon.tw），用于内容检测中验证是否正确引用了对应国家官网链接
- **Default_Seeds**: 各区域的默认种子检索短语列表
- **Content_Languages**: 各区域支持的内容输出语言列表（如 ROA 支持繁體中文/韩语/越南语/英语），决定检索短语和文章的生成语言
- **Verification_Platforms**: 各区域用于智测验证的 AI 平台集合

## Requirements

### Requirement 1: Region Configuration File Structure

**User Story:** As a system administrator, I want each region to have a standardized configuration file, so that all region-specific parameters are centrally managed and easily maintainable.

#### Acceptance Criteria

1. THE Region_Adapter SHALL store each region configuration as a separate JSON file at the path `config/regions/{region_code}.json`
2. WHEN a Region_Config file is loaded, THE Region_Adapter SHALL validate that it contains all required fields with correct types: ai_platforms (non-empty array of strings), official_links (non-empty array of strings), knowledge_base_paths (array of strings), ahrefs_report_id (string or null), default_seeds (array of at least 5 strings), verification_platforms (non-empty array of strings), and content_languages (non-empty array of objects each containing "code" and "name" string fields)
3. IF a Region_Config file is missing a required field or a field has an incorrect type, THEN THE Region_Adapter SHALL raise a validation error indicating the field name, the expected type, and the region code
4. IF a Region_Config file does not exist for a given region code, THEN THE Region_Adapter SHALL fall back to a default configuration file at `config/regions/_default.json`
5. THE Region_Adapter SHALL support the four defined region codes: ROA, CN, NA, EU
6. THE Region_Adapter SHALL support sub_region values within ROA: TW, KR, VN — stored in users.json as user_sub_region, used to load sub-region-specific overrides (official_links, default_seeds) from `config/regions/ROA_{sub_region}.json` if available
7. IF a Region_Config file contains malformed JSON that cannot be parsed, THEN THE Region_Adapter SHALL raise a parse error indicating the region code and refuse to load the configuration
8. IF both the requested Region_Config file and the `_default.json` fallback file are unavailable, THEN THE Region_Adapter SHALL raise a fatal configuration error and prevent the system from operating with that region code
9. IF a region code is requested that is not one of the four supported values (ROA, CN, NA, EU), THEN THE Region_Adapter SHALL raise a validation error indicating the unsupported region code

### Requirement 2: Auto-Load Region Configuration on Login with Manual Override

**User Story:** As a logged-in user, I want the system to automatically load my admin-assigned region's configuration by default, and I want the ability to manually switch to another region, so that I can flexibly view content for different regions.

#### Acceptance Criteria

1. WHEN a user logs in, THE Smart_Suite SHALL look up the user's default region from the user_region field in users.json
2. WHEN the user's default region is determined, THE Region_Adapter SHALL load the corresponding Region_Config and inject it into the session state as the Active_Region
3. IF a user has no user_region mapping in users.json, THEN THE Region_Adapter SHALL assign the default configuration from `_default.json` and log a warning including the username
4. THE Region_Adapter SHALL complete configuration loading within 500ms of login
5. WHILE a user session is active, THE Region_Adapter SHALL retain the loaded Region_Config in session state without re-reading from disk on each page navigation
6. THE Smart_Suite SHALL display a region selector in the UI sidebar allowing the user to switch Active_Region to any of the four supported regions (ROA, CN, NA, EU), with the currently active region visually indicated
7. WHEN a user selects a different region via the selector, THE Region_Adapter SHALL reload the corresponding Region_Config and update the session state within 500ms
8. WHEN a user switches regions manually, THE Smart_Suite SHALL preserve the switch for the duration of the session but revert to the admin-assigned default on next login
9. IF the Region_Adapter fails to load the requested Region_Config during a manual switch (due to missing or malformed file), THEN THE Smart_Suite SHALL display an error message and retain the previously active Region_Config
10. THE Smart_Suite SHALL display the active region code as a label in the sidebar region selector so the user always knows which region is currently loaded
11. FOR ROA users, THE Smart_Suite SHALL additionally display a sub_region selector (TW / KR / VN) in the sidebar below the region selector, allowing them to choose or change their sub_region; the selection SHALL persist to users.json so it remembers on next login
12. WHEN an ROA user has not yet set a sub_region (first login or admin left it unset), THE Smart_Suite SHALL display a one-time onboarding prompt asking the user to select their sub_region (TW / KR / VN) before proceeding to any module; this selection also auto-sets the default content language (TW→zh-TW, KR→ko, VN→vi)

### Requirement 3: Region-Specific AI Platforms for Zhice

**User Story:** As a content operator, I want the Zhice module to use my region's AI platforms, so that search journey simulations reflect the actual platforms my target audience uses.

#### Acceptance Criteria

1. WHEN a Zhice simulation is initiated, THE Zhice_Module SHALL read the ai_platforms list from the active Region_Config and execute queries against every platform in that list
2. THE Region_Config for CN SHALL include both domestic and international platforms: deepseek, doubao, kimi, yuanbao, qianwen, chatgpt, gemini, perplexity, grok
3. THE Region_Config for ROA SHALL include the platforms: chatgpt, gemini, perplexity, grok
4. THE Region_Config for NA SHALL include the platforms: chatgpt, gemini, perplexity, grok
5. THE Region_Config for EU SHALL include the platforms: chatgpt, gemini, perplexity, grok
6. WHEN a user overrides the platform selection in the UI, THE Zhice_Module SHALL present all platforms from the full supported set (deepseek, doubao, kimi, yuanbao, qianwen, chatgpt, gemini, perplexity, grok) with the user's region platforms pre-selected, and use the user's final selection instead of the Region_Config default
7. IF a user override results in fewer than 1 platform selected, THEN THE Zhice_Module SHALL prevent simulation execution and display an error message indicating that at least one platform must be selected
8. IF the ai_platforms list in the active Region_Config is empty or contains a platform identifier not in the supported set, THEN THE Zhice_Module SHALL raise a validation error indicating the invalid platform entry and region code, and SHALL not proceed with the simulation

### Requirement 4: Region-Specific Official Link Standards

**User Story:** As a content operator, I want detection rules to use my region's official link standards, so that brand mention verification and content quality checks can detect whether generated content correctly references the target region's Amazon seller portal URLs.

#### Acceptance Criteria

1. THE Region_Config SHALL include an official_links field containing a list of one or more authorized Amazon seller portal URLs for that region
2. THE Region_Config for ROA SHALL include official_links covering all sub_regions: ["sell.amazon.tw", "sell.amazon.co.kr", "sell.amazon.vn"]; when a sub_region is set, THE Region_Adapter SHALL filter to only the sub_region's official link(s)
3. THE Region_Config for CN SHALL include official_links: ["sell.amazon.com.cn"]
4. THE Region_Config for NA SHALL include official_links: ["sell.amazon.com"]
5. THE Region_Config for EU SHALL include official_links: ["sell.amazon.co.uk", "sell.amazon.de", "sell.amazon.fr", "sell.amazon.it", "sell.amazon.es", "sell.amazon.nl", "sell.amazon.pl", "sell.amazon.se", "sell.amazon.com.be"]
8. WHEN content detection rules evaluate official link presence, THE Smart_Suite SHALL perform a domain-level match by checking whether the content contains at least one URL whose domain matches an entry in the official_links list of the active Region_Config, regardless of protocol prefix (http/https), "www" subdomain, or trailing path segments
9. WHEN generated content contains an official link whose domain matches an entry in a different region's official_links list but not the active region, THE Smart_Suite SHALL flag it as a region mismatch warning displayed as an inline annotation in the Zhiyou compliance check results
10. THE Smart_Suite SHALL use the official_links list to perform link extraction and verification during the Zhiyou compliance check step, reporting a pass when at least one active-region official link is found and a fail when no official link from any region is detected in the content
11. IF generated content contains no URL matching any official_links entry from any region, THEN THE Smart_Suite SHALL report a "missing official link" compliance failure in the Zhiyou compliance check results

### Requirement 5: Region-Specific Knowledge Base

**User Story:** As a content operator, I want Zhiku and Zhizao to reference my region's knowledge base, so that generated content is relevant to my region's sellers.

#### Acceptance Criteria

1. THE Region_Config SHALL specify a knowledge_base_paths field containing a list of at least 1 and at most 50 relative file paths pointing to region-specific knowledge files under `input/knowledge/`
2. WHEN the Zhiku_Module generates queries, THE Zhiku_Module SHALL load and reference as context only the knowledge files listed in the active Region_Config, excluding all knowledge files not in that list
3. WHEN the Zhizao module generates content, THE Smart_Suite SHALL inject only the knowledge files listed in the active Region_Config as context, excluding all knowledge files not in that list
4. IF a knowledge_base_path listed in Region_Config does not exist on disk, THEN THE Region_Adapter SHALL log a warning including the missing path and the region code, and skip that path without failing
5. IF all knowledge_base_paths in the active Region_Config are invalid or missing on disk, THEN THE Region_Adapter SHALL raise an error indicating that no knowledge files are available for that region and prevent content generation from proceeding

### Requirement 6: Region-Specific Ahrefs Integration

**User Story:** As a TW content operator, I want Ahrefs Brand Radar to use my region's report_id, so that brand mention data reflects my regional campaign.

#### Acceptance Criteria

1. THE Region_Config SHALL include an ahrefs_report_id field of type string (maximum 128 characters) or null
2. WHEN the Ahrefs integration is invoked, THE Smart_Suite SHALL pass the ahrefs_report_id from the active Region_Config as the report identifier in the Ahrefs Brand Radar API request
3. IF ahrefs_report_id is null or empty string in the active Region_Config, THEN THE Smart_Suite SHALL hide all Ahrefs-related UI components (Brand Radar panel and Ahrefs data widgets) and not issue any Ahrefs API calls for that session
4. IF the Ahrefs API returns an error or is unreachable when invoked, THEN THE Smart_Suite SHALL display an error message indicating the Ahrefs data is temporarily unavailable and retain the last successfully retrieved data if present
5. WHEN an admin views the Ahrefs data panel, THE Smart_Suite SHALL display a region dropdown listing all six supported regions, and WHEN the admin selects a region, THE Smart_Suite SHALL reload the Ahrefs data using that region's ahrefs_report_id
6. IF an admin selects a region whose ahrefs_report_id is null or empty, THEN THE Smart_Suite SHALL display a message indicating no Ahrefs report is configured for that region

### Requirement 7: Region-Specific Default Seeds

**User Story:** As a content operator, I want to see default seed phrases relevant to my region when I open Zhiku, so that I can start generating queries without manual seed entry.

#### Acceptance Criteria

1. THE Region_Config SHALL include a default_seeds list containing seed phrases written in the primary language of the region and relevant to that region's seller audience topics
2. WHEN the Zhiku UI loads, THE Zhiku_Module SHALL pre-populate the seed input with the default_seeds from the active Region_Config
3. THE default_seeds for each region SHALL contain at least 5 and no more than 30 seed phrases, each between 2 and 100 characters in length
4. WHEN a user adds or removes seeds, THE Zhiku_Module SHALL persist the changes to the user's session without modifying the Region_Config file, up to a maximum of 50 seeds per session
5. IF a user attempts to add a seed phrase that already exists in the current seed list (case-insensitive match), THEN THE Zhiku_Module SHALL reject the duplicate and display an error message indicating the phrase already exists
6. IF the active Region_Config contains a default_seeds list with fewer than 5 entries or the field is empty, THEN THE Zhiku_Module SHALL load the default_seeds from `_default.json` and log a warning identifying the affected region code

### Requirement 8: Region-Specific Verification Platforms

**User Story:** As a content operator, I want Zhice verification to run against my region's relevant AI platforms, so that coverage reports reflect my actual competitive landscape.

#### Acceptance Criteria

1. THE Region_Config SHALL include a verification_platforms list defining which platforms to use for automated verification runs
2. WHEN a batch verification is triggered, THE Zhice_Module SHALL execute queries against all platforms in the verification_platforms list from the active Region_Config
3. THE verification_platforms for CN SHALL include at least: deepseek, doubao, kimi, chatgpt, perplexity, grok
4. THE verification_platforms for ROA, NA, EU SHALL include at least: chatgpt, perplexity, grok
5. IF a platform in verification_platforms fails to respond within 30 seconds during a batch verification run, THEN THE Zhice_Module SHALL mark that platform's result as "timeout" in the report, continue with remaining platforms, and include the timeout count in the batch summary
6. WHEN a user overrides verification platforms in the UI, THE Zhice_Module SHALL use the user's selection instead of the Region_Config default, following the same validation rules as Requirement 3 criterion 9

### Requirement 9: Admin Panel Region Filtering

**User Story:** As an admin, I want to filter pending approvals and user lists by region, so that I can manage regional teams efficiently.

#### Acceptance Criteria

1. WHEN an admin opens the approval panel, THE Admin_Panel SHALL display a region filter dropdown with options: All, ROA, CN, NA, EU, with "All" selected by default
2. WHEN a region filter is selected, THE Admin_Panel SHALL display only pending approvals and user list entries whose user_region matches the selected value
3. WHEN "All" is selected in the region filter, THE Admin_Panel SHALL display all users regardless of region
4. THE Admin_Panel SHALL display the user's region (and sub_region for ROA users) as visible columns in the user list table
5. WHEN a new user is pending approval, THE Admin_Panel SHALL allow the admin to assign a user_region value from a fixed set of four options: ROA, CN, NA, EU
6. IF an admin attempts to approve a new user without selecting a region, THEN THE Admin_Panel SHALL keep the approve action disabled and display an inline indication that region assignment is required before approval can proceed
7. IF a user has no user_region assigned, THEN THE Admin_Panel SHALL display the region column as "Unassigned" and include that user only when the "All" filter is selected
8. FOR ROA users, THE Admin_Panel SHALL optionally allow the admin to assign a sub_region (TW / KR / VN) at approval time or leave it unset for the user to self-select later

### Requirement 10: Region Configuration API Endpoint

**User Story:** As a developer integrating with Smart Suite, I want an API endpoint to retrieve region configuration, so that external tools can adapt to region-specific settings.

#### Acceptance Criteria

1. THE Smart_Suite SHALL expose a GET endpoint at `/api/region/config` that returns the active Region_Config for the authenticated user as a JSON object containing all fields defined in Requirement 1 (ai_platforms, official_links, knowledge_base_paths, ahrefs_report_id, default_seeds, verification_platforms, content_languages)
2. THE Smart_Suite SHALL expose a GET endpoint at `/api/region/list` that returns a JSON array of all four supported region codes (ROA, CN, NA, EU) with their display names
3. WHEN an unauthenticated request is received at any `/api/region/*` endpoint, THE Smart_Suite SHALL return HTTP 401 with a JSON body containing an error field indicating authentication is required
4. WHEN an authenticated admin request to `/api/region/config` includes a query parameter `region_code`, THE Smart_Suite SHALL return the Region_Config for the specified region code
5. IF a non-admin user sends a request with the `region_code` query parameter, THEN THE Smart_Suite SHALL return HTTP 403 with a JSON body containing an error field indicating insufficient permissions
6. IF a request specifies a `region_code` value that does not match one of the four supported region codes (ROA, CN, NA, EU), THEN THE Smart_Suite SHALL return HTTP 404 with a JSON body containing an error field indicating the region code is not found
7. THE Smart_Suite SHALL return API responses from `/api/region/*` endpoints within 1000ms under normal operating conditions

### Requirement 11: Content Language Selection for Query and Article Generation

**User Story:** As an ROA content operator, I want to select a content language (Vietnamese, Traditional Chinese, Korean, or English) for my queries and articles, so that the generated search phrases and content are produced in the language of my target audience.

#### Acceptance Criteria

1. THE Region_Config SHALL include a content_languages field containing a list of supported content output languages for that region, each with a language code and display name
2. THE Region_Config for ROA SHALL include content_languages: [{"code": "zh-TW", "name": "繁體中文"}, {"code": "ko", "name": "한국어"}, {"code": "vi", "name": "Tiếng Việt"}, {"code": "en", "name": "English"}]
3. THE Region_Config for CN SHALL include content_languages: [{"code": "zh-CN", "name": "简体中文"}, {"code": "en", "name": "English"}]
4. THE Region_Config for NA SHALL include content_languages: [{"code": "en", "name": "English"}]
5. THE Region_Config for EU SHALL include content_languages: [{"code": "en", "name": "English"}]
6. WHEN the Zhiku UI loads, THE Zhiku_Module SHALL display a content language selector in the sidebar (below sub_region selector for ROA users), populated with the content_languages from the active Region_Config, with the first entry as the default selection
7. FOR ROA users with a sub_region set, THE Zhiku_Module SHALL pre-select the language matching their sub_region: TW → zh-TW, KR → ko, VN → vi; the user can override this at any time via the sidebar language selector
8. WHEN a user selects a content language and generates search phrases (seeds → AI queries), THE Zhiku_Module SHALL instruct the LLM to produce queries in the selected language, allowing natural mixing with English terms (e.g., "亚马逊 FBA 怎么发货", "아마존 PPC 광고 방법") since real users search with mixed-language phrases
9. WHEN the Zhizao module generates article content from queries, THE Smart_Suite SHALL produce the full article (title, body, meta description) entirely in the selected content language — no language mixing allowed in article output. If the source query contains English terms (e.g., "FBA", "PPC"), the article SHALL either translate them or keep them as universally recognized proper nouns, but all prose SHALL be in the target language
10. WHEN the Zhiyou module optimizes or rewrites content, THE Smart_Suite SHALL maintain the same language purity as the original article — the optimized output SHALL remain entirely in the original content_language without introducing mixed-language prose
11. THE Smart_Suite SHALL store the content_language code as a column in zhiku_ai_queries.csv and zhizao_draft_content.csv to track which language each item was produced in
12. WHEN a user switches content language mid-session, THE Smart_Suite SHALL apply the new language only to subsequently generated items without modifying previously generated content
13. THE Smart_Suite SHALL validate that article and optimized content output matches the requested language by checking the script of the generated text (e.g., CJK characters for zh-TW, Hangul for ko, Vietnamese diacritics for vi) and flag mismatches as warnings
14. IF the Zhiyou compliance check detects that an article contains more than 10% of characters from a script inconsistent with the declared content_language (excluding universally recognized brand names and acronyms), THEN THE Smart_Suite SHALL flag it as a "language consistency violation" and recommend rewrite
