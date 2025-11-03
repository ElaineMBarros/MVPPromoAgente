export interface ChatMessage {
  id: string;
  role: "user" | "agent";
  content: string;
  timestamp: string;
}

export interface ChatResponse {
  response: string;
  session_id: string;
  timestamp: string;
}

export interface SystemStatus {
  system_ready: boolean;
  openai: boolean;
  openai_version: string | null;
  openai_model: string;
  agno_framework: boolean;
  agno_version: string | null;
  agno_status_error: string | null;
  orchestrator: boolean;
  extractor: boolean;
  validator: boolean;
  summarizer: boolean;
  memory_manager: boolean;
  sqlite_db: boolean;
  messages_stored: number;
  promotions_count: number;
  python_version: string;
  environment: string;
}

export interface PromotionRecord {
  id: string;
  promo_id: string;
  session_id: string;
  titulo?: string;
  mecanica?: string;
  descricao?: string;
  segmentacao?: string;
  periodo_inicio?: string;
  periodo_fim?: string;
  condicoes?: string;
  recompensas?: string;
  status?: string;
  created_at: string;
  sent_at?: string;
}
