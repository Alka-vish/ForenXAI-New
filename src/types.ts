export interface ImageInformation {
  filename: string;
  width: number;
  height: number;
  color_mode: string;
  format: string;
  file_size_bytes: number;
}

export interface ForensicEvidenceItem {
  evidence_id: string;
  category: string;
  title: string;
  observation: string;
  measurement: Record<string, any>;
  source_module: string;
  coordinates: {
    grid_position: [number, number];
    region_id: string;
  } | null;
  alternative_explanations: string[];
  limitations: string[];
  strength: string;
}

export interface DebateMessage {
  agent: 'prosecutor' | 'defence';
  turn: number;
  argument: string;
  supporting_evidence_ids: string[];
  uncertainties: string[];
  alternative_explanations: string[];
}

export interface HallucinationFlag {
  turn: number;
  agent: string;
  evidence_id: string;
  type: string;
  details: string;
}

export interface VerifiedClaim {
  turn: number;
  agent: string;
  evidence_ids: string[];
  verified: boolean;
  notes?: string;
}

export interface ContradictionItem {
  point?: string;
  prosecutor_claim?: string;
  defence_claim?: string;
  status?: string;
  expert_resolution?: string;
  [key: string]: any;
}

export interface ExpertReport {
  status: 'verified' | 'verification_failed' | string;
  evidence_sufficient: boolean;
  recommendation: 'proceed_to_judge' | 'stop' | string;
  checked_evidence_ids: string[];
  hallucination_flags: HallucinationFlag[];
  contradictions: (string | ContradictionItem)[];
  missing_information: string[];
  verified_claims: VerifiedClaim[];
  unsupported_claims?: any[];
  reliability_concerns?: string[];
  explanation?: string;
  technical_notes?: string[];
}

export interface JudgeResult {
  status: 'completed' | 'skipped' | string;
  assessment: 'REAL' | 'FAKE' | 'UNCERTAIN';
  reasoning: string;
  supporting_evidence_ids: string[];
  contradictory_evidence_ids: string[];
  limitations: string[];
  expert_verification_summary: string;
}

export interface DebateGraphState {
  image_id: string;
  status: 'completed' | 'insufficient_evidence' | 'stopped' | string;
  can_proceed: boolean;
  debate_completed: boolean;
  completed_iterations: number;
  total_messages: number;
  debate_messages: DebateMessage[];
  prosecutor_turns?: DebateMessage[];
  defence_turns?: DebateMessage[];
  evidence_sufficiency?: {
    can_proceed: boolean;
    reason?: string;
    total_evidence_items?: number;
    sufficient_categories?: number;
    [key: string]: any;
  };
  stopping_reason: string | null;
  message?: string;
  expert_report: ExpertReport | null;
  judge_result: JudgeResult | null;
  processing_errors: string[];
}

export interface DebateApiResponse {
  image_information: ImageInformation;
  features?: {
    spatial_features?: Record<string, any>;
    noise_analysis?: Record<string, any>;
    frequency_analysis?: Record<string, any>;
    srm_analysis?: Record<string, any>;
    wavelet_analysis?: Record<string, any>;
    compression_analysis?: Record<string, any>;
    recompression_ela_analysis?: Record<string, any>;
    ai_detection?: Record<string, any>;
  };
  evidence: ForensicEvidenceItem[];
  evidence_summary: {
    total_evidence_items: number;
    evidence_categories: string[];
  };
  debate: DebateGraphState;
  analysis?: Record<string, any>;
}

export interface InvestigationRecord {
  id: string;
  timestamp: string;
  imageName: string;
  imageSize: number;
  imagePreview?: string;
  response: DebateApiResponse;
}
