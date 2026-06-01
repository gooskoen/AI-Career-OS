export type PipelineStatus =
  | "drafted"
  | "applied"
  | "recruiter_replied"
  | "interview_scheduled"
  | "interview_completed"
  | "offer_received"
  | "hired"
  | "rejected"
  | "withdrawn";

export const PIPELINE_STATUSES: PipelineStatus[] = [
  "drafted",
  "applied",
  "recruiter_replied",
  "interview_scheduled",
  "interview_completed",
  "offer_received",
  "hired",
  "rejected",
  "withdrawn"
];

export interface UserProfile {
  id: string;
  email: string;
  display_name: string;
}

export interface AuthResponse {
  access_token: string;
  refresh_token: string;
  user: UserProfile;
}

export interface DashboardReport {
  active_applications: number;
  interviews_scheduled: number;
  offers_received: number;
  hires: number;
  rejections: number;
  pipeline_totals: Record<PipelineStatus, number>;
}

export interface FunnelReport {
  applications: number;
  recruiter_replies: number;
  interviews: number;
  offers: number;
  hires: number;
  application_to_reply_rate: number;
  reply_to_interview_rate: number;
  interview_to_offer_rate: number;
  offer_to_hire_rate: number;
}

export interface OutcomeReport {
  rejection_rate: number;
  offer_rate: number;
  hire_rate: number;
  outcome_trends: Record<string, Record<string, number>>;
}

export interface SkillReport {
  strongest_performing_skills: string[];
  weakest_performing_skills: string[];
  most_successful_skills: string[];
  rejection_linked_skills: string[];
}

export interface RecommendationReport {
  recommendations_followed: Record<string, number>;
  recommendations_ignored: Record<string, number>;
  recommendation_usage_rates: Record<string, number>;
}

export interface CandidateProfile {
  id?: string;
  display_name?: string;
  name?: string;
  headline?: string;
  location?: string;
  summary?: string;
  target_roles?: string[];
  skills?: string[];
  experience_highlights?: string[];
}

export interface ApplicationRecord {
  id: string;
  candidate_id?: string;
  job_id?: string;
  status: PipelineStatus;
  source?: string | null;
  next_action?: string | null;
  next_action_due?: string | null;
  created_at?: string;
}

export type ApplicationBoard = Record<PipelineStatus, ApplicationRecord[]>;

export interface ApplicationSummary {
  application: ApplicationRecord;
  current_status: PipelineStatus;
  next_action?: string | null;
  next_action_due?: string | null;
  latest_notes: Array<{ id?: string; note: string; created_at?: string }>;
  artifact_readiness: {
    match_ready: boolean;
    package_ready: boolean;
    intelligence_ready: boolean;
  };
  latest_outcome?: { outcome: string; notes?: string; created_at?: string } | null;
  status_history: Array<{
    previous_status?: string | null;
    new_status: PipelineStatus;
    created_at?: string;
  }>;
}
