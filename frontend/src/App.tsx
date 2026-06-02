import type React from "react";
import { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  BriefcaseBusiness,
  LayoutDashboard,
  LogOut,
  UserRound
} from "lucide-react";
import { api, getStoredUser, isAuthenticated } from "./api";
import type {
  ApplicationBoard,
  ApplicationPackage,
  ApplicationRecord,
  ApplicationSummary,
  CandidateProfile,
  DashboardReport,
  FunnelReport,
  JobRecord,
  MatchResult,
  OutcomeReport,
  PipelineStatus,
  RecommendationReport,
  SkillReport
} from "./types";
import { PIPELINE_STATUSES } from "./types";

type Page = "dashboard" | "applications" | "insights" | "profile";
type AuthMode = "login" | "register";
type WorkflowStep = {
  label: string;
  status: "todo" | "done";
};
type JobIntakeMode = "text" | "url";
type IntakeWizardState = {
  candidateForm: CandidateFormState;
  jobMode: JobIntakeMode;
  jobText: string;
  jobUrl: string;
  candidate: CandidateProfile | null;
  job: JobRecord | null;
  matchResult: MatchResult | null;
  applicationPackage: ApplicationPackage | null;
  application: ApplicationRecord | null;
};
type CandidateFormState = {
  name: string;
  headline: string;
  location: string;
  summary: string;
  skills: string;
  targetRoles: string;
  experienceHighlights: string;
};

const statusLabels: Record<PipelineStatus, string> = {
  drafted: "Drafted",
  applied: "Applied",
  recruiter_replied: "Recruiter Replied",
  interview_scheduled: "Interview Scheduled",
  interview_completed: "Interview Completed",
  offer_received: "Offer Received",
  hired: "Hired",
  rejected: "Rejected",
  withdrawn: "Withdrawn"
};

const INTAKE_WIZARD_STORAGE_KEY = "ai-career-os.intake-wizard";
const defaultCandidateForm: CandidateFormState = {
  name: "",
  headline: "",
  location: "",
  summary: "",
  skills: "",
  targetRoles: "",
  experienceHighlights: ""
};
const defaultJobText = [
  "Paste a job description here.",
  "Include title, company, location, responsibilities, required skills, and nice-to-have skills."
].join("\n");

export function App() {
  const [authed, setAuthed] = useState(isAuthenticated());
  const [page, setPage] = useState<Page>("dashboard");

  if (!authed) {
    return <AuthScreen onAuthenticated={() => setAuthed(true)} />;
  }

  return (
    <Shell
      page={page}
      onPageChange={setPage}
      onLogout={() => {
        api.logout();
        setAuthed(false);
      }}
    />
  );
}

function AuthScreen({ onAuthenticated }: { onAuthenticated: () => void }) {
  const [mode, setMode] = useState<AuthMode>("login");
  const [email, setEmail] = useState("demo@example.com");
  const [displayName, setDisplayName] = useState("Demo User");
  const [password, setPassword] = useState("use-a-long-demo-password");
  const [error, setError] = useState("");

  async function submit(event: React.FormEvent) {
    event.preventDefault();
    setError("");
    try {
      if (mode === "login") {
        await api.login(email, password);
      } else {
        await api.register(email, displayName, password);
      }
      onAuthenticated();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Authentication failed");
    }
  }

  return (
    <main className="auth-shell">
      <form className="auth-panel" onSubmit={submit}>
        <div>
          <p className="eyebrow">Private beta</p>
          <h1>AI-Career-OS</h1>
        </div>
        <div className="segmented" role="tablist" aria-label="Authentication mode">
          <button
            type="button"
            className={mode === "login" ? "active" : ""}
            onClick={() => setMode("login")}
          >
            Login
          </button>
          <button
            type="button"
            className={mode === "register" ? "active" : ""}
            onClick={() => setMode("register")}
          >
            Register
          </button>
        </div>
        <label>
          Email
          <input value={email} onChange={(event) => setEmail(event.target.value)} />
        </label>
        {mode === "register" && (
          <label>
            Display name
            <input
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
            />
          </label>
        )}
        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
          />
        </label>
        {error && <p className="error">{error}</p>}
        <button className="primary" type="submit">
          {mode === "login" ? "Login" : "Create account"}
        </button>
      </form>
    </main>
  );
}

function Shell({
  page,
  onPageChange,
  onLogout
}: {
  page: Page;
  onPageChange: (page: Page) => void;
  onLogout: () => void;
}) {
  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div>
          <p className="eyebrow">AI-Career-OS</p>
          <h2>Career cockpit</h2>
        </div>
        <nav>
          <NavButton icon={<LayoutDashboard />} active={page === "dashboard"} onClick={() => onPageChange("dashboard")}>
            Dashboard
          </NavButton>
          <NavButton icon={<BriefcaseBusiness />} active={page === "applications"} onClick={() => onPageChange("applications")}>
            Applications
          </NavButton>
          <NavButton icon={<BarChart3 />} active={page === "insights"} onClick={() => onPageChange("insights")}>
            Insights
          </NavButton>
          <NavButton icon={<UserRound />} active={page === "profile"} onClick={() => onPageChange("profile")}>
            Profile
          </NavButton>
        </nav>
        <button className="logout" onClick={onLogout}>
          <LogOut size={18} />
          Logout
        </button>
      </aside>
      <main className="content">
        {page === "dashboard" && <DashboardPage onOpenApplications={() => onPageChange("applications")} />}
        {page === "applications" && <ApplicationsPage />}
        {page === "insights" && <InsightsPage />}
        {page === "profile" && <ProfilePage />}
      </main>
    </div>
  );
}

function NavButton({
  active,
  icon,
  children,
  onClick
}: {
  active: boolean;
  icon: React.ReactNode;
  children: React.ReactNode;
  onClick: () => void;
}) {
  return (
    <button className={active ? "nav active" : "nav"} onClick={onClick}>
      {icon}
      {children}
    </button>
  );
}

function DashboardPage({ onOpenApplications }: { onOpenApplications: () => void }) {
  const { data: dashboard, error } = useResource(api.dashboard);
  const { data: funnel } = useResource(api.funnel);

  return (
    <section>
      <PageHeader title="Dashboard" subtitle="Pipeline health and current outcomes" />
      {error && <Notice message={error} />}
      <div className="metric-grid">
        <Metric label="Active Applications" value={dashboard?.active_applications} />
        <Metric label="Interviews Scheduled" value={dashboard?.interviews_scheduled} />
        <Metric label="Offers Received" value={dashboard?.offers_received} />
        <Metric label="Hires" value={dashboard?.hires} />
        <Metric label="Rejections" value={dashboard?.rejections} />
      </div>
      <Panel title="Funnel Summary">
        <FunnelSummary funnel={funnel} />
      </Panel>
      <Panel title="Pipeline Totals">
        <div className="status-grid">
          {PIPELINE_STATUSES.map((status) => (
            <span key={status}>
              <strong>{statusLabels[status]}</strong>
              {dashboard?.pipeline_totals?.[status] ?? 0}
            </span>
          ))}
        </div>
      </Panel>
      <IntakeWizard onOpenApplications={onOpenApplications} />
    </section>
  );
}

function IntakeWizard({ onOpenApplications }: { onOpenApplications: () => void }) {
  const saved = loadIntakeWizardState();
  const [candidateForm, setCandidateForm] = useState<CandidateFormState>(
    saved?.candidateForm ?? defaultCandidateForm
  );
  const [jobMode, setJobMode] = useState<JobIntakeMode>(saved?.jobMode ?? "text");
  const [jobText, setJobText] = useState(saved?.jobText ?? defaultJobText);
  const [jobUrl, setJobUrl] = useState(saved?.jobUrl ?? "");
  const [candidate, setCandidate] = useState<CandidateProfile | null>(saved?.candidate ?? null);
  const [job, setJob] = useState<JobRecord | null>(saved?.job ?? null);
  const [matchResult, setMatchResult] = useState<MatchResult | null>(saved?.matchResult ?? null);
  const [applicationPackage, setApplicationPackage] =
    useState<ApplicationPackage | null>(saved?.applicationPackage ?? null);
  const [application, setApplication] = useState<ApplicationRecord | null>(
    saved?.application ?? null
  );
  const [loading, setLoading] = useState("");
  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  const candidateId = candidate?.id;
  const jobId = job?.id ?? "";
  const matchId = matchResult?.id ?? "";

  const steps: WorkflowStep[] = [
    { label: "Candidate", status: candidate ? "done" : "todo" },
    { label: "Job", status: job ? "done" : "todo" },
    { label: "Match", status: matchResult ? "done" : "todo" },
    { label: "Package", status: applicationPackage ? "done" : "todo" },
    { label: "Application", status: application ? "done" : "todo" }
  ];

  useEffect(() => {
    sessionStorage.setItem(
      INTAKE_WIZARD_STORAGE_KEY,
      JSON.stringify({
        candidateForm,
        jobMode,
        jobText,
        jobUrl,
        candidate,
        job,
        matchResult,
        applicationPackage,
        application
      })
    );
  }, [
    candidateForm,
    jobMode,
    jobText,
    jobUrl,
    candidate,
    job,
    matchResult,
    applicationPackage,
    application
  ]);

  async function runWizardAction(action: string, operation: () => Promise<void>) {
    setMessage("");
    setError("");
    setLoading(action);
    try {
      await operation();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Wizard action failed");
    } finally {
      setLoading("");
    }
  }

  function updateCandidateField(field: keyof CandidateFormState, value: string) {
    setCandidateForm((current) => ({ ...current, [field]: value }));
  }

  function resetDownstream(from: "candidate" | "job" | "match" | "package") {
    if (from === "candidate") {
      setJob(null);
    }
    if (from === "candidate" || from === "job") {
      setMatchResult(null);
    }
    if (from === "candidate" || from === "job" || from === "match") {
      setApplicationPackage(null);
    }
    if (from !== "package") {
      setApplication(null);
    }
  }

  function candidateFromForm(): CandidateProfile {
    return {
      name: required(candidateForm.name, "Full Name"),
      headline: required(candidateForm.headline, "Headline"),
      location: required(candidateForm.location, "Location"),
      summary: required(candidateForm.summary, "Summary"),
      skills: requiredList(candidateForm.skills, "Skills"),
      target_roles: requiredList(candidateForm.targetRoles, "Target Roles"),
      experience_highlights: requiredList(
        candidateForm.experienceHighlights,
        "Experience Highlights"
      ),
      portfolio_links: []
    };
  }

  async function saveCandidate() {
    await runWizardAction("candidate", async () => {
      const created = await api.createCandidate(candidateFromForm());
      setCandidate(created);
      resetDownstream("candidate");
      setMessage("candidate saved");
    });
  }

  async function importJob() {
    await runWizardAction("job", async () => {
      if (!candidateId) {
        throw new Error("Save candidate before importing a job.");
      }
      const imported =
        jobMode === "text"
          ? await api.importJobText(required(jobText, "Job Description"), candidateId)
          : await api.importJobUrl(required(jobUrl, "Job URL"), candidateId);
      setJob(imported.job);
      setMatchResult(null);
      setApplicationPackage(null);
      setApplication(null);
      setMessage(imported.duplicate ? "existing job loaded" : "job imported");
    });
  }

  async function generateMatch() {
    await runWizardAction("match", async () => {
      if (!candidate || !candidateId || !job || !jobId) {
        throw new Error("Save candidate and import a job before generating a match.");
      }
      const preview = await api.previewMatch(candidate, job);
      const persisted = await api.createMatch(candidateId, jobId);
      setMatchResult({ ...preview, id: persisted.id });
      setApplicationPackage(null);
      setApplication(null);
      setMessage("match generated");
    });
  }

  async function generatePackage() {
    await runWizardAction("package", async () => {
      if (!candidate || !job || !matchResult) {
        throw new Error("Generate a match before creating an application package.");
      }
      const generated = await api.generatePackage(candidate, job, matchResult);
      setApplicationPackage(generated);
      setApplication(null);
      setMessage("package generated");
    });
  }

  async function createApplication() {
    await runWizardAction("application", async () => {
      if (!candidateId || !jobId || !matchId) {
        throw new Error("Generate a persisted match before creating an application.");
      }
      const created = await api.createApplication(candidateId, jobId, matchId);
      setApplication(created);
      setMessage("application created");
    });
  }

  return (
    <Panel title="User Intake Wizard">
      <p className="muted">
        Create a real candidate profile, import a real vacancy, review the match,
        generate an application package, and create an application using existing APIs.
      </p>
      <div className="workflow-steps">
        {steps.map((step) => (
          <span className={step.status === "done" ? "done" : "todo"} key={step.label}>
            {step.label}
          </span>
        ))}
      </div>

      <div className="wizard-grid">
        <section className="wizard-section">
          <h3>Candidate</h3>
          <div className="form-grid">
            <label>
              Full Name
              <input
                value={candidateForm.name}
                onChange={(event) => updateCandidateField("name", event.target.value)}
              />
            </label>
            <label>
              Headline
              <input
                value={candidateForm.headline}
                onChange={(event) => updateCandidateField("headline", event.target.value)}
              />
            </label>
            <label>
              Location
              <input
                value={candidateForm.location}
                onChange={(event) => updateCandidateField("location", event.target.value)}
              />
            </label>
          </div>
          <label>
            Summary
            <textarea
              value={candidateForm.summary}
              onChange={(event) => updateCandidateField("summary", event.target.value)}
            />
          </label>
          <div className="form-grid">
            <label>
              Skills
              <textarea
                value={candidateForm.skills}
                onChange={(event) => updateCandidateField("skills", event.target.value)}
              />
            </label>
            <label>
              Target Roles
              <textarea
                value={candidateForm.targetRoles}
                onChange={(event) => updateCandidateField("targetRoles", event.target.value)}
              />
            </label>
            <label>
              Experience Highlights
              <textarea
                value={candidateForm.experienceHighlights}
                onChange={(event) =>
                  updateCandidateField("experienceHighlights", event.target.value)
                }
              />
            </label>
          </div>
          <button className="primary inline" disabled={loading === "candidate"} onClick={saveCandidate}>
            {loading === "candidate" ? "Saving..." : "Save Candidate"}
          </button>
          {candidate && <p className="notice success">Candidate ready: {candidate.name ?? candidate.display_name}</p>}
        </section>

        <section className="wizard-section">
          <h3>Job</h3>
          <div className="segmented compact" role="tablist" aria-label="Job intake mode">
            <button
              type="button"
              className={jobMode === "text" ? "active" : ""}
              onClick={() => setJobMode("text")}
            >
              Paste Description
            </button>
            <button
              type="button"
              className={jobMode === "url" ? "active" : ""}
              onClick={() => setJobMode("url")}
            >
              Paste URL
            </button>
          </div>
          {jobMode === "text" ? (
            <label>
              Job Description
              <textarea
                className="large-textarea"
                value={jobText}
                onChange={(event) => setJobText(event.target.value)}
              />
            </label>
          ) : (
            <label>
              Job URL
              <input value={jobUrl} onChange={(event) => setJobUrl(event.target.value)} />
            </label>
          )}
          <button className="primary inline" disabled={!candidateId || loading === "job"} onClick={importJob}>
            {loading === "job" ? "Importing..." : "Import Job"}
          </button>
          {job && (
            <div className="result-box">
              <strong>{job.title}</strong>
              <span>{job.company}</span>
              <span>{job.location ?? "Location not specified"}</span>
            </div>
          )}
        </section>

        <section className="wizard-section">
          <h3>Match</h3>
          <button className="primary inline" disabled={!candidateId || !jobId || loading === "match"} onClick={generateMatch}>
            {loading === "match" ? "Generating..." : "Generate Match"}
          </button>
          {matchResult && <MatchSummary match={matchResult} />}
        </section>

        <section className="wizard-section">
          <h3>Application Package</h3>
          <button
            className="primary inline"
            disabled={!matchResult || loading === "package"}
            onClick={generatePackage}
          >
            {loading === "package" ? "Generating..." : "Generate Package"}
          </button>
          {applicationPackage && <PackageSummary applicationPackage={applicationPackage} />}
        </section>

        <section className="wizard-section">
          <h3>Application</h3>
          <button
            className="primary inline"
            disabled={!applicationPackage || !matchId || loading === "application"}
            onClick={createApplication}
          >
            {loading === "application" ? "Creating..." : "Create Application"}
          </button>
          {application && (
            <div className="result-box">
              <strong>Status: {statusLabels[application.status]}</strong>
              <span>Next action: continue through the application pipeline.</span>
              <button onClick={onOpenApplications}>Open Pipeline</button>
            </div>
          )}
        </section>
      </div>

      {message && <p className="notice success">{message}</p>}
      {error && <Notice message={error} />}
    </Panel>
  );
}

function MatchSummary({ match }: { match: MatchResult }) {
  const gaps = [
    ...(match.gaps?.critical ?? []),
    ...(match.gaps?.moderate ?? []),
    ...(match.gaps?.optional ?? [])
  ];
  return (
    <div className="summary-stack">
      <div className="score-badge">{match.score}% match</div>
      <Timeline
        title="Strengths"
        items={(match.strengths ?? []).map((strength) => strength.skill)}
      />
      <Timeline title="Gaps" items={gaps} />
      <Timeline title="Recommended Actions" items={match.recommended_actions ?? []} />
      {match.recommendation && <p className="muted">{match.recommendation}</p>}
    </div>
  );
}

function PackageSummary({
  applicationPackage
}: {
  applicationPackage: ApplicationPackage;
}) {
  return (
    <div className="summary-stack">
      <p>{applicationPackage.tailored_summary}</p>
      <Timeline title="Key Strengths" items={applicationPackage.key_strengths} />
      <Timeline title="Risk Gaps" items={applicationPackage.risk_gaps} />
      <Timeline title="Recommended CV Edits" items={applicationPackage.recommended_cv_edits} />
    </div>
  );
}

function loadIntakeWizardState(): IntakeWizardState | null {
  try {
    const raw = sessionStorage.getItem(INTAKE_WIZARD_STORAGE_KEY);
    return raw ? (JSON.parse(raw) as IntakeWizardState) : null;
  } catch {
    return null;
  }
}

function required(value: string, label: string): string {
  const trimmed = value.trim();
  if (!trimmed) {
    throw new Error(`${label} is required.`);
  }
  return trimmed;
}

function requiredList(value: string, label: string): string[] {
  const items = value
    .split(/[\n,]/)
    .map((item) => item.trim())
    .filter(Boolean);
  if (!items.length) {
    throw new Error(`${label} is required.`);
  }
  return items;
}

function ApplicationsPage() {
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [dragged, setDragged] = useState<ApplicationRecord | null>(null);
  const { data: board, error, reload } = useResource(api.board);

  const selected = useMemo<ApplicationRecord | undefined>(
    () => Object.values(board ?? {}).flat().find((item) => item.id === selectedId),
    [board, selectedId]
  );

  async function transition(application: ApplicationRecord, status: PipelineStatus) {
    await api.transitionApplication(application.id, status);
    await reload();
    setSelectedId(application.id);
  }

  return (
    <section>
      <PageHeader title="Applications" subtitle="Kanban-ready application pipeline" />
      {error && <Notice message={error} />}
      <div className="board" data-testid="kanban-board">
        {PIPELINE_STATUSES.map((status) => (
          <div
            className="lane"
            key={status}
            onDragOver={(event) => event.preventDefault()}
            onDrop={() => dragged && transition(dragged, status)}
          >
            <h3>{statusLabels[status]}</h3>
            {(board?.[status] ?? []).map((application) => (
              <button
                draggable
                className="application-card"
                key={application.id}
                onClick={() => setSelectedId(application.id)}
                onDragStart={() => setDragged(application)}
              >
                <span>{application.source ?? "manual"}</span>
                <strong>{application.id.slice(0, 8)}</strong>
                {application.next_action && <small>{application.next_action}</small>}
              </button>
            ))}
          </div>
        ))}
      </div>
      {selected && <ApplicationDetail applicationId={selected.id} />}
    </section>
  );
}

function ApplicationDetail({ applicationId }: { applicationId: string }) {
  const { data: summary, error } = useResource(() => api.applicationSummary(applicationId), [applicationId]);

  return (
    <Panel title="Application Detail">
      {error && <Notice message={error} />}
      {summary && (
        <div className="detail-grid" data-testid="application-detail">
          <Detail label="Application" value={summary.application.id} />
          <Detail label="Status" value={statusLabels[summary.current_status]} />
          <Detail label="Next Action" value={summary.next_action ?? "None"} />
          <Detail label="Due" value={summary.next_action_due ?? "None"} />
          <Readiness summary={summary} />
          <Timeline title="Status History" items={summary.status_history.map((item) => item.new_status)} />
          <Timeline title="Notes" items={summary.latest_notes.map((item) => item.note)} />
          <Timeline title="Latest Outcome" items={[summary.latest_outcome?.outcome ?? "None"]} />
        </div>
      )}
    </Panel>
  );
}

function InsightsPage() {
  const { data: funnel } = useResource(api.funnel);
  const { data: outcomes } = useResource(api.outcomes);
  const { data: skills } = useResource(api.skills);
  const { data: recommendations } = useResource(api.recommendations);

  return (
    <section>
      <PageHeader title="Insights" subtitle="Deterministic reporting from your outcomes" />
      <Panel title="Funnel Metrics">
        <FunnelSummary funnel={funnel} />
      </Panel>
      <div className="two-column">
        <Panel title="Outcome Analytics">
          <Detail label="Rejection Rate" value={formatRate(outcomes?.rejection_rate)} />
          <Detail label="Offer Rate" value={formatRate(outcomes?.offer_rate)} />
          <Detail label="Hire Rate" value={formatRate(outcomes?.hire_rate)} />
        </Panel>
        <Panel title="Skill Analytics">
          <Timeline title="Strongest Skills" items={skills?.strongest_performing_skills ?? []} />
          <Timeline title="Rejection Linked" items={skills?.rejection_linked_skills ?? []} />
        </Panel>
      </div>
      <Panel title="Recommendation Analytics">
        <div className="status-grid">
          {Object.entries(recommendations?.recommendation_usage_rates ?? {}).map(([key, value]) => (
            <span key={key}>
              <strong>{labelize(key)}</strong>
              {formatRate(value)}
            </span>
          ))}
        </div>
      </Panel>
    </section>
  );
}

function ProfilePage() {
  const user = getStoredUser();
  const { data: candidates } = useResource(api.candidates);
  const candidate = candidates?.[0];

  return (
    <section>
      <PageHeader title="Profile" subtitle="Account and candidate snapshot" />
      <div className="two-column">
        <Panel title="User Profile">
          <Detail label="Name" value={user?.display_name ?? "Unknown"} />
          <Detail label="Email" value={user?.email ?? "Unknown"} />
        </Panel>
        <Panel title="Candidate Profile">
          <Detail label="Name" value={candidate?.display_name ?? candidate?.name ?? "No candidate yet"} />
          <Detail label="Headline" value={candidate?.headline ?? "Not set"} />
          <Detail label="Location" value={candidate?.location ?? "Not set"} />
          <Timeline title="Skills" items={candidate?.skills ?? []} />
        </Panel>
      </div>
    </section>
  );
}

function PageHeader({ title, subtitle }: { title: string; subtitle: string }) {
  return (
    <header className="page-header">
      <p className="eyebrow">Private beta</p>
      <h1>{title}</h1>
      <p>{subtitle}</p>
    </header>
  );
}

function Metric({ label, value }: { label: string; value?: number }) {
  return (
    <div className="metric-card">
      <span>{label}</span>
      <strong>{value ?? 0}</strong>
    </div>
  );
}

function Panel({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <section className="panel">
      <h2>{title}</h2>
      {children}
    </section>
  );
}

function Detail({ label, value }: { label: string; value?: string }) {
  return (
    <p className="detail">
      <span>{label}</span>
      <strong>{value ?? "0"}</strong>
    </p>
  );
}

function Timeline({ title, items }: { title: string; items: string[] }) {
  return (
    <div>
      <h3 className="subheading">{title}</h3>
      <ul className="timeline">
        {(items.length ? items : ["None"]).map((item, index) => (
          <li key={`${item}-${index}`}>{labelize(item)}</li>
        ))}
      </ul>
    </div>
  );
}

function Readiness({ summary }: { summary: ApplicationSummary }) {
  return (
    <div className="readiness">
      {Object.entries(summary.artifact_readiness).map(([key, value]) => (
        <span className={value ? "ready" : "missing"} key={key}>
          {labelize(key)}
        </span>
      ))}
    </div>
  );
}

function FunnelSummary({ funnel }: { funnel?: FunnelReport }) {
  return (
    <div className="status-grid">
      <span>
        <strong>Applications</strong>
        {funnel?.applications ?? 0}
      </span>
      <span>
        <strong>Replies</strong>
        {funnel?.recruiter_replies ?? 0}
      </span>
      <span>
        <strong>Interviews</strong>
        {funnel?.interviews ?? 0}
      </span>
      <span>
        <strong>Offers</strong>
        {funnel?.offers ?? 0}
      </span>
      <span>
        <strong>Reply Rate</strong>
        {formatRate(funnel?.application_to_reply_rate)}
      </span>
    </div>
  );
}

function Notice({ message }: { message: string }) {
  return <p className="notice">{message}</p>;
}

function useResource<T>(loader: () => Promise<T>, deps: React.DependencyList = []) {
  const [data, setData] = useState<T | undefined>();
  const [error, setError] = useState("");

  async function load() {
    try {
      setError("");
      setData(await loader());
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Unable to load data");
    }
  }

  useEffect(() => {
    load();
  }, deps);

  return { data, error, reload: load };
}

function labelize(value: string) {
  return value.replaceAll("_", " ").replace(/\b\w/g, (letter) => letter.toUpperCase());
}

function formatRate(value?: number) {
  return `${Math.round((value ?? 0) * 100)}%`;
}
