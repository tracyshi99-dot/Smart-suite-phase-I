// ============ Auth ============
export interface AuthResponse {
  allowed: boolean;
  user: string;
  region?: string;
  sub_region?: string;
  is_admin?: boolean;
}

// ============ Zhiku ============
export interface SeedExpansionRequest {
  seed_word: string;
  count: number;
  language: string;
  market: string;
  batch_id: string;
}

export interface PersonaExpansionRequest {
  identity: string;
  company_type: string;
  marketplace: string[];
  content_focus: string[];
  count: number;
  language: string;
  batch_id: string;
}

export interface UploadPhrasesRequest {
  phrases: string[];
  source: string;
  batch_id: string;
}

export interface PhraseData {
  ai_query: string;
  intent_type: string;
  priority_score: number;
  estimated_volume: number;
  category: string;
  is_selected: string | boolean; // "TRUE" | "FALSE" | true | false
  created_at: string;
  source?: string;
}

export interface PhraseListResponse {
  phrases: PhraseData[];
  total: number;
}

export interface SelectRequest {
  batch_id: string;
  indices: number[];
  selected: boolean;
}

// ============ Zhice ============
export interface ZhiceRequest {
  phrases: string[];
  platforms: string[];
  user: string;
}

export interface ZhiceResult {
  query: string;
  platform: string;
  has_official_link: boolean;
  has_brand_mention: boolean;
  sentiment?: string;
  competitors?: string;
  answer_preview: string;
  error?: string;
}

export interface ZhiceResponse {
  status: string;
  message: string;
  phrases: number;
  platforms: string[];
  results?: ZhiceResult[];
}

// ============ Zhizao ============
export interface ZhizaoRequest {
  batch_id: string;
  content_limit: number;
  content_language: string;
  template_id: string;
}

export interface DraftContent {
  ai_query: string;
  title: string;
  word_count: number;
  content_draft: string;
}

export interface ZhizaoResponse {
  success: boolean;
  drafts?: DraftContent[];
  count?: number;
  message?: string;
}

// ============ Zhiyou ============
export interface ZhiyouRequest {
  batch_id: string;
  content_language: string;
}

export interface ScoreResult {
  ai_query: string;
  title?: string;
  intent_match: number;
  ai_readability: number;
  authority: number;
  actionability: number;
  differentiation: number;
  overall_score: number;
  compliance_status: "PASS" | "FAIL";
}

export interface ZhiyouScoreResponse {
  success: boolean;
  scores?: ScoreResult[];
  message?: string;
}

export interface OptimizeResult {
  ai_query: string;
  original_score: number;
  optimized_score: number;
  changes: string[];
  compliance_status: "PASS" | "FAIL";
}

export interface ZhiyouOptimizeResponse {
  success: boolean;
  results?: OptimizeResult[];
  message?: string;
}

// ============ Zhixi ============
export interface MonthlyMetric {
  month: string;
  cn_geo: number;
  ww_geo: number;
  ww_direct: number;
  [key: string]: string | number;
}

export interface CitationRecord {
  phrase: string;
  platform: string;
  citation_status: string;
  verification_date: string;
  [key: string]: string;
}

export interface MetricsResponse {
  data: Record<string, unknown>[];
  columns?: string[];
  total?: number;
}

// ============ Region Config ============
export interface RegionConfig {
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

// ============ Pipeline ============
export interface PipelineStep {
  id: string;
  label: string;
  status: "complete" | "active" | "pending";
  fileCount?: number;
}

export interface BatchStatus {
  batch_id: string;
  steps: PipelineStep[];
  total_files: number;
}

// ============ Chat ============
export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
  structured_data?: unknown;
  timestamp: number;
}

// ============ API Error ============
export interface ApiError {
  status: number;
  message: string;
  isTimeout: boolean;
  retriesExhausted: boolean;
}
