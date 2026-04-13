function getApiBaseUrl() {
  if (typeof window !== "undefined") {
    return process.env.NEXT_PUBLIC_API_BASE_URL ?? "";
  }

  return (
    process.env.INTERNAL_API_BASE_URL ??
    process.env.INTERNAL_WEB_BASE_URL ??
    process.env.NEXT_PUBLIC_SITE_URL ??
    process.env.NEXT_PUBLIC_API_BASE_URL ??
    "http://127.0.0.1:3000"
  );
}

const API_BASE_URL = getApiBaseUrl();

/** Must match API `ALLOWED_CONNECTOR_SLUGS` (apps/api/app/services/source_registry.py). */
export const KNOWN_CONNECTOR_SLUGS = [
  "arsat",
  "boletin-oficial",
  "comprar",
  "contratar",
  "inta",
  "licitaciones-catamarca",
  "licitaciones-chaco",
  "licitaciones-cordoba",
  "licitaciones-corrientes",
  "licitaciones-mendoza",
  "licitaciones-rio-negro",
  "licitaciones-salta",
  "licitaciones-san-luis",
  "licitaciones-santa-fe",
  "licitaciones-tucuman",
  "pami",
  "pbac",
] as const;

export function formatFastApiDetail(payload: unknown): string {
  if (payload == null) {
    return "Error desconocido";
  }
  if (typeof payload === "string") {
    return payload;
  }
  if (typeof payload === "object" && payload !== null && "detail" in payload) {
    const detail = (payload as { detail: unknown }).detail;
    if (typeof detail === "string") {
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((item) => {
          if (item && typeof item === "object" && "msg" in item) {
            return String((item as { msg: unknown }).msg);
          }
          return JSON.stringify(item);
        })
        .join(" ");
    }
  }
  return JSON.stringify(payload);
}

export type Tender = {
  id: number;
  source_id: number;
  external_id: string | null;
  title: string;
  description_raw: string | null;
  organization: string | null;
  jurisdiction: string | null;
  procedure_type: string | null;
  publication_date: string | null;
  deadline_date: string | null;
  opening_date: string | null;
  estimated_amount: string | null;
  currency: string | null;
  status_raw: string | null;
  source_url: string;
  source: {
    id: number;
    name: string;
    slug: string;
    source_type: string;
    base_url: string;
    is_active: boolean;
  };
  matches: {
    id: number;
    company_profile_id: number;
    score: string;
    score_band: string;
    reasons_json: {
      summary?: string[];
      components?: Record<string, { points?: number }>;
    } | null;
    matched_at: string;
  }[];
  states: {
    id: number;
    user_id: number;
    state: string;
    notes: string | null;
    alert_overrides_json: {
      inherit_company_defaults?: boolean;
      receive_deadlines?: boolean;
      deadline_offsets_hours?: number[];
    } | null;
    updated_at: string;
  }[];
};

export type DocumentText = {
  id: number;
  extraction_method: string;
  extraction_status: string;
  extracted_text: string | null;
  text_length: number;
  confidence_score: string | null;
};

export type TenderDocument = {
  id: number;
  document_type: string;
  filename: string;
  file_path: string | null;
  source_url: string;
  download_status: string;
  downloaded_at: string | null;
  texts: DocumentText[];
};

export type TenderDetail = Tender & {
  detail_html_path: string | null;
  detail_cached_at: string | null;
  documents: TenderDocument[];
  enrichments: {
    id: number;
    llm_model: string | null;
    summary_short: string | null;
    summary_structured_json: {
      summary_short?: string;
      procurement_object?: string;
      key_dates?: Record<string, string | null>;
      key_requirements?: string[];
      risk_flags?: string[];
      evidence_snippets?: string[];
    } | null;
    key_requirements: string[] | null;
    risk_flags: string[] | null;
    extracted_deadlines: Record<string, string | null> | null;
    enrichment_status: string;
    created_at: string;
  }[];
  alerts: {
    id: number;
    user_id: number;
    alert_type: string;
    scheduled_for: string;
    sent_at: string | null;
    delivery_channel: string;
    delivery_status: string;
    payload_snapshot: Record<string, string> | null;
  }[];
};

export type TenderResponse = {
  items: Tender[];
  total: number;
};

export type Source = {
  id: number;
  name: string;
  slug: string;
  source_type: string;
  scraping_mode: string;
  connector_slug?: string | null;
  base_url: string;
  config_json?: Record<string, unknown> | null;
  is_active: boolean;
  last_run_at?: string | null;
  connector_available?: boolean;
};

export type SourceRun = {
  id: number;
  source_id: number;
  status: string;
  started_at: string;
  finished_at: string | null;
  items_found: number;
  items_new: number;
  error_message: string | null;
};

export type Alert = {
  id: number;
  tender_id: number;
  user_id: number;
  alert_type: string;
  scheduled_for: string;
  sent_at: string | null;
  delivery_channel: string;
  delivery_status: string;
  delivery_attempts: number;
  last_error_message: string | null;
  provider_message_id: string | null;
  payload_snapshot: Record<string, string> | null;
};

export type AdminAuditEvent = {
  id: number;
  actor_user_id: number | null;
  action: string;
  detail_json: Record<string, unknown> | null;
  created_at: string;
};

export type WhatsappOutboxMessage = {
  id: string;
  provider: string;
  to: string;
  body: string;
  created_at: string;
};

export type User = {
  id: number;
  company_profile_id: number | null;
  cuit: string | null;
  email: string;
  full_name: string;
  company_name: string | null;
  role: string;
  is_active: boolean;
  whatsapp_number: string | null;
  whatsapp_opt_in: boolean;
  whatsapp_verified_at: string | null;
  telegram_chat_id: string | null;
  telegram_opt_in: boolean;
  telegram_verified_at: string | null;
  alert_preferences_json: {
    min_score?: number;
    channels?: string[];
    receive_relevant?: boolean;
    receive_deadlines?: boolean;
  } | null;
};

export type MeUpdateInput = {
  full_name?: string;
  company_name?: string;
  cuit?: string;
  whatsapp_number?: string;
  whatsapp_opt_in?: boolean;
  telegram_chat_id?: string;
  telegram_opt_in?: boolean;
  email_opt_in?: boolean;
  telegram_opt_in_alerts?: boolean;
  alert_priority?: "alta" | "media" | "todas";
  receive_deadlines?: boolean;
  receive_relevant?: boolean;
};

export type CompanyProfile = {
  id: number;
  cuit: string | null;
  company_name: string;
  legal_name: string | null;
  company_description: string;
  sectors: string[] | null;
  include_keywords: string[] | null;
  exclude_keywords: string[] | null;
  jurisdictions: string[] | null;
  preferred_buyers: string[] | null;
  min_amount: string | null;
  max_amount: string | null;
  alert_preferences_json: {
    min_score?: number;
    receive_relevant?: boolean;
    receive_deadlines?: boolean;
    deadline_only_for_saved?: boolean;
    deadline_offsets_hours?: number[];
  } | null;
  tax_status_json: Record<string, unknown> | null;
  company_data_source: string | null;
  company_data_updated_at: string | null;
  source_scope_mode: "all_active" | "custom";
};

export type SourceAccess = {
  profile_id: number;
  company_name: string;
  source_scope_mode: "all_active" | "custom";
  selected_source_ids: number[];
  effective_source_ids: number[];
  sources: Source[];
};

export type AutomationSettings = {
  id: number;
  is_enabled: boolean;
  ingestion_interval_hours: number;
  openai_api_key_configured: boolean;
  resend_api_key_configured: boolean;
  email_delivery_enabled: boolean;
  whatsapp_enabled: boolean;
  whatsapp_provider: string | null;
  whatsapp_api_version: string | null;
  whatsapp_meta_token_configured: boolean;
  whatsapp_meta_phone_number_id: string | null;
  telegram_enabled: boolean;
  telegram_bot_token_configured: boolean;
  openai_model: string | null;
  llm_master_prompt: string | null;
  contact_email: string | null;
  contact_whatsapp_number: string | null;
  contact_telegram_handle: string | null;
  demo_booking_url: string | null;
  resend_from_email: string | null;
  last_run_started_at: string | null;
  last_run_finished_at: string | null;
  last_success_at: string | null;
  last_error_message: string | null;
  last_cycle_summary: Record<string, unknown> | null;
};

export type PublicPlatformSettings = {
  contact_email: string | null;
  contact_whatsapp_number: string | null;
  contact_telegram_handle: string | null;
  demo_booking_url: string | null;
};

export type SourceCreateInput = {
  name: string;
  slug: string;
  source_type: string;
  scraping_mode: string;
  connector_slug?: string | null;
  base_url: string;
  config_json?: Record<string, unknown> | null;
  is_active: boolean;
};

export type SourceUpdateInput = {
  name?: string;
  slug?: string;
  source_type?: string;
  scraping_mode?: string;
  connector_slug?: string | null;
  base_url?: string;
  config_json?: Record<string, unknown> | null;
  is_active?: boolean;
};

export type CompanyLookup = {
  cuit: string;
  company_name: string;
  legal_name: string;
  tax_status_json: Record<string, unknown> | null;
  company_data_source: string;
  company_data_updated_at: string;
  jurisdictions: string[] | null;
  sectors: string[] | null;
};

export async function fetchTenders(searchParams?: {
  source?: string;
  jurisdiction?: string;
  min_score?: string;
}) {
  const params = new URLSearchParams();
  if (searchParams?.source) params.set("source", searchParams.source);
  if (searchParams?.jurisdiction) {
    params.set("jurisdiction", searchParams.jurisdiction);
  }
  if (searchParams?.min_score) params.set("min_score", searchParams.min_score);

  const response = await fetch(
    `${API_BASE_URL}/api/v1/tenders${params.toString() ? `?${params}` : ""}`,
    { cache: "no-store" },
  );

  if (!response.ok) {
    throw new Error("Failed to fetch tenders");
  }

  return (await response.json()) as TenderResponse;
}

export async function fetchSources() {
  const response = await fetch(`${API_BASE_URL}/api/v1/sources`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error("Failed to fetch sources");
  }

  return (await response.json()) as Source[];
}

export async function fetchTenderDetail(id: string, cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/tenders/${id}`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });

  if (!response.ok) {
    throw new Error("Failed to fetch tender detail");
  }

  return (await response.json()) as TenderDetail;
}

export async function fetchSavedTenders(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/saved-tenders`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Failed to fetch saved tenders");
  }
  return (await response.json()) as TenderResponse;
}

function withCookieHeader(cookieHeader?: string) {
  return cookieHeader ? { cookie: cookieHeader } : undefined;
}

export async function fetchSourceRuns(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/source-runs`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch source runs");
  }
  return (await response.json()) as SourceRun[];
}

export async function fetchAlerts(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/alerts`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (response.status === 401 || response.status === 403) {
    return [];
  }
  if (!response.ok) {
    throw new Error("Failed to fetch alerts");
  }
  return (await response.json()) as Alert[];
}

export async function fetchUsers(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/users`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch users");
  }
  return (await response.json()) as User[];
}

export async function fetchAdminSources(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/sources`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch admin sources");
  }
  return (await response.json()) as Source[];
}

export async function fetchAdminCompanyProfiles(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/company-profiles`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch company profiles");
  }
  return (await response.json()) as CompanyProfile[];
}

export async function fetchAutomationSettings(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/automation`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch automation settings");
  }
  return (await response.json()) as AutomationSettings;
}

export async function fetchPublicPlatformSettings() {
  const response = await fetch(`${API_BASE_URL}/api/v1/public/platform-settings`, {
    cache: "no-store",
  });
  if (!response.ok) {
    throw new Error("Failed to fetch public platform settings");
  }
  return (await response.json()) as PublicPlatformSettings;
}

export async function fetchWhatsappOutbox(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/alerts/outbox`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch WhatsApp outbox");
  }
  return (await response.json()) as WhatsappOutboxMessage[];
}

export async function fetchAdminAuditEvents(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/audit-events`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch admin audit events");
  }
  return (await response.json()) as AdminAuditEvent[];
}

export async function fetchCurrentUser(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/me`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Failed to fetch current user");
  }
  return (await response.json()) as User;
}

export async function fetchMyCompanyProfile(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/me/company-profile`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (response.status === 401) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Failed to fetch company profile");
  }
  return (await response.json()) as CompanyProfile;
}

export async function fetchMySourceAccess(cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/me/source-access`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (response.status === 401 || response.status === 403) {
    return null;
  }
  if (!response.ok) {
    throw new Error("Failed to fetch company source access");
  }
  return (await response.json()) as SourceAccess;
}

export async function fetchAdminCompanySourceAccess(profileId: number, cookieHeader?: string) {
  const response = await fetch(`${API_BASE_URL}/api/v1/admin/company-profiles/${profileId}/source-access`, {
    cache: "no-store",
    headers: withCookieHeader(cookieHeader),
  });
  if (!response.ok) {
    throw new Error("Failed to fetch admin company source access");
  }
  return (await response.json()) as SourceAccess;
}
