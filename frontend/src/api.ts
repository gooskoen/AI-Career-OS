import type {
  ApplicationBoard,
  ApplicationSummary,
  AuthResponse,
  CandidateProfile,
  DashboardReport,
  FunnelReport,
  OutcomeReport,
  PipelineStatus,
  RecommendationReport,
  SkillReport
} from "./types";

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "";
const ACCESS_TOKEN_KEY = "ai-career-os.access-token";
const REFRESH_TOKEN_KEY = "ai-career-os.refresh-token";
const USER_KEY = "ai-career-os.user";

export function saveSession(session: AuthResponse): void {
  sessionStorage.setItem(ACCESS_TOKEN_KEY, session.access_token);
  sessionStorage.setItem(REFRESH_TOKEN_KEY, session.refresh_token);
  sessionStorage.setItem(USER_KEY, JSON.stringify(session.user));
}

export function clearSession(): void {
  sessionStorage.removeItem(ACCESS_TOKEN_KEY);
  sessionStorage.removeItem(REFRESH_TOKEN_KEY);
  sessionStorage.removeItem(USER_KEY);
}

export function getStoredUser() {
  const raw = sessionStorage.getItem(USER_KEY);
  return raw ? JSON.parse(raw) : null;
}

export function isAuthenticated(): boolean {
  return Boolean(sessionStorage.getItem(ACCESS_TOKEN_KEY));
}

async function request<T>(
  path: string,
  options: RequestInit = {},
  retry = true
): Promise<T> {
  const headers = new Headers(options.headers);
  headers.set("Content-Type", "application/json");
  const token = sessionStorage.getItem(ACCESS_TOKEN_KEY);
  if (token) {
    headers.set("Authorization", `Bearer ${token}`);
  }

  const response = await fetch(`${API_BASE}${path}`, { ...options, headers });
  if (response.status === 401 && retry && sessionStorage.getItem(REFRESH_TOKEN_KEY)) {
    await refreshSession();
    return request<T>(path, options, false);
  }
  if (!response.ok) {
    throw new Error(await errorMessage(response));
  }
  return response.json() as Promise<T>;
}

async function errorMessage(response: Response): Promise<string> {
  try {
    const body = await response.json();
    return body?.error?.message ?? "Request failed";
  } catch {
    return "Request failed";
  }
}

export const api = {
  async register(email: string, displayName: string, password: string) {
    const session = await request<AuthResponse>("/auth/register", {
      method: "POST",
      body: JSON.stringify({
        email,
        display_name: displayName,
        password
      })
    });
    saveSession(session);
    return session;
  },

  async login(email: string, password: string) {
    const session = await request<AuthResponse>("/auth/login", {
      method: "POST",
      body: JSON.stringify({ email, password })
    });
    saveSession(session);
    return session;
  },

  async refresh() {
    return refreshSession();
  },

  logout() {
    clearSession();
  },

  dashboard() {
    return request<DashboardReport>("/reporting/dashboard");
  },

  funnel() {
    return request<FunnelReport>("/reporting/funnel");
  },

  outcomes() {
    return request<OutcomeReport>("/reporting/outcomes");
  },

  skills() {
    return request<SkillReport>("/reporting/skills");
  },

  recommendations() {
    return request<RecommendationReport>("/reporting/recommendations");
  },

  board() {
    return request<ApplicationBoard>("/applications/board");
  },

  transitionApplication(id: string, status: PipelineStatus) {
    return request(`/applications/${id}/transition`, {
      method: "POST",
      body: JSON.stringify({ status })
    });
  },

  applicationSummary(id: string) {
    return request<ApplicationSummary>(`/applications/${id}/summary`);
  },

  candidates() {
    return request<CandidateProfile[]>("/candidates");
  },

  createCandidate(candidate: CandidateProfile) {
    return request<CandidateProfile & { id: string }>("/candidates", {
      method: "POST",
      body: JSON.stringify({
        name: candidate.name ?? candidate.display_name ?? "Demo Candidate",
        headline: candidate.headline ?? "AI operations candidate",
        location: candidate.location ?? "Remote",
        summary: candidate.summary ?? "Private beta candidate profile.",
        target_roles: candidate.target_roles ?? ["AI Operations"],
        skills: candidate.skills ?? ["Python", "workflow automation"],
        experience_highlights: candidate.experience_highlights ?? [
          "Built workflow automation and reporting."
        ],
        portfolio_links: []
      })
    });
  },

  importJob(rawText: string, candidateId?: string) {
    return request<{
      job: {
        id: string;
        title: string;
        company: string;
        location?: string;
        description: string;
        required_skills: string[];
        nice_to_have_skills: string[];
      };
      duplicate: boolean;
      match?: { id: string } | null;
    }>("/jobs/import-text", {
      method: "POST",
      body: JSON.stringify({
        raw_text: rawText,
        match_candidate_id: candidateId
      })
    });
  },

  createMatch(candidateId: string, jobId: string) {
    return request<{ id: string; score?: number; strengths?: string[]; gaps?: unknown[] }>(
      "/matches/persist",
      {
        method: "POST",
        body: JSON.stringify({
          candidate_profile_id: candidateId,
          job_description_id: jobId
        })
      }
    );
  },

  generatePackage(candidate: CandidateProfile, job: unknown, matchResult: unknown) {
    return request("/applications/package", {
      method: "POST",
      body: JSON.stringify({
        candidate: {
          name: candidate.name ?? candidate.display_name ?? "Demo Candidate",
          headline: candidate.headline ?? "AI operations candidate",
          location: candidate.location ?? "Remote",
          summary: candidate.summary ?? "Private beta candidate profile.",
          target_roles: candidate.target_roles ?? ["AI Operations"],
          skills: candidate.skills ?? ["Python", "workflow automation"],
          experience_highlights: candidate.experience_highlights ?? [
            "Built workflow automation and reporting."
          ],
          portfolio_links: []
        },
        job,
        match_result: matchResult
      })
    });
  },

  createApplication(candidateId: string, jobId: string, matchResultId?: string) {
    return request<{ id: string; status: PipelineStatus }>("/applications", {
      method: "POST",
      body: JSON.stringify({
        candidate_id: candidateId,
        job_id: jobId,
        status: "drafted",
        source: "private_beta_ui",
        match_result_id: matchResultId
      })
    });
  },

  recordOutcome(candidateId: string, jobId: string, applicationId: string) {
    return request("/outcomes", {
      method: "POST",
      body: JSON.stringify({
        candidate_id: candidateId,
        job_id: jobId,
        application_id: applicationId,
        outcome: "applied",
        notes: "Recorded through Sprint 13 beta workflow.",
        cv_edits_applied: true,
        cover_letter_used: true,
        interview_prep_used: false,
        skills: ["workflow automation", "reporting"],
        job_family: "AI Operations"
      })
    });
  }
};

async function refreshSession(): Promise<AuthResponse> {
  const refreshToken = sessionStorage.getItem(REFRESH_TOKEN_KEY);
  if (!refreshToken) {
    throw new Error("No refresh token available");
  }
  const session = await request<AuthResponse>(
    "/auth/refresh",
    {
      method: "POST",
      body: JSON.stringify({ refresh_token: refreshToken })
    },
    false
  );
  saveSession(session);
  return session;
}
