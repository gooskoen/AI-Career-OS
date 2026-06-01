import type React from "react";
import { useEffect, useMemo, useState } from "react";
import {
  BarChart3,
  BriefcaseBusiness,
  ClipboardList,
  LayoutDashboard,
  LogOut,
  UserRound
} from "lucide-react";
import { api, getStoredUser, isAuthenticated } from "./api";
import type {
  ApplicationBoard,
  ApplicationRecord,
  ApplicationSummary,
  CandidateProfile,
  DashboardReport,
  FunnelReport,
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
        {page === "dashboard" && <DashboardPage />}
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

function DashboardPage() {
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
      <BetaWorkflow />
    </section>
  );
}

function BetaWorkflow() {
  const [candidate, setCandidate] = useState<CandidateProfile | null>(null);
  const [job, setJob] = useState<unknown>(null);
  const [matchResult, setMatchResult] = useState<unknown>(null);
  const [application, setApplication] = useState<ApplicationRecord | null>(null);
  const [packageGenerated, setPackageGenerated] = useState(false);
  const [outcomeRecorded, setOutcomeRecorded] = useState(false);
  const [message, setMessage] = useState("");

  const candidateId = candidate?.id;
  const jobId = typeof job === "object" && job && "id" in job ? String(job.id) : "";
  const matchId =
    typeof matchResult === "object" && matchResult && "id" in matchResult
      ? String(matchResult.id)
      : "";

  const steps: WorkflowStep[] = [
    { label: "Register", status: "done" },
    { label: "Login", status: "done" },
    { label: "Create Candidate", status: candidate ? "done" : "todo" },
    { label: "Import Job", status: job ? "done" : "todo" },
    { label: "Review Match", status: matchResult ? "done" : "todo" },
    { label: "Generate Package", status: packageGenerated ? "done" : "todo" },
    { label: "Create Application", status: application ? "done" : "todo" },
    { label: "Move Through Pipeline", status: application?.status === "applied" ? "done" : "todo" },
    { label: "Record Outcome", status: outcomeRecorded ? "done" : "todo" },
    { label: "View Insights", status: "todo" }
  ];

  async function runStep(step: string) {
    setMessage("");
    if (step === "candidate") {
      const created = await api.createCandidate({
        name: "Private Beta Candidate",
        headline: "AI Operations and Reporting Specialist",
        location: "Remote",
        summary: "Builds workflow automation, reporting, and application systems.",
        target_roles: ["AI Operations Lead"],
        skills: ["Python", "SQL", "workflow automation", "reporting"],
        experience_highlights: ["Built reporting workflows for operations teams."]
      });
      setCandidate(created);
      setMessage("candidate created");
    }
    if (step === "job" && candidateId) {
      const imported = await api.importJob(
        [
          "AI Operations Lead",
          "ExampleTech",
          "Remote",
          "Lead workflow automation, reporting, analytics, and stakeholder delivery.",
          "Required skills: Python, SQL, workflow automation, reporting"
        ].join("\n"),
        candidateId
      );
      setJob(imported.job);
      setMatchResult(imported.match ?? null);
      setMessage("job imported");
    }
    if (step === "match" && candidateId && jobId) {
      const created = await api.createMatch(candidateId, jobId);
      setMatchResult(created);
      setMessage("match reviewed");
    }
    if (step === "package" && candidate && job && matchResult) {
      await api.generatePackage(candidate, job, matchResult);
      setPackageGenerated(true);
      setMessage("package generated");
    }
    if (step === "application" && candidateId && jobId) {
      const created = await api.createApplication(candidateId, jobId, matchId || undefined);
      setApplication(created);
      setMessage("application created");
    }
    if (step === "pipeline" && application) {
      const updated = (await api.transitionApplication(application.id, "applied")) as ApplicationRecord;
      setApplication({ ...application, ...updated, status: "applied" });
      setMessage("pipeline updated");
    }
    if (step === "outcome" && candidateId && jobId && application) {
      await api.recordOutcome(candidateId, jobId, application.id);
      setOutcomeRecorded(true);
      setMessage("outcome recorded");
    }
  }

  return (
    <Panel title="Beta Workflow Validation">
      <p className="muted">
        Guided API-first workflow for private beta validation. Each action calls an
        existing backend endpoint.
      </p>
      <div className="workflow-steps">
        {steps.map((step) => (
          <span className={step.status === "done" ? "done" : "todo"} key={step.label}>
            {step.label}
          </span>
        ))}
      </div>
      <div className="workflow-actions">
        <button onClick={() => runStep("candidate")}>Create Candidate</button>
        <button disabled={!candidateId} onClick={() => runStep("job")}>
          Import Job
        </button>
        <button disabled={!candidateId || !jobId} onClick={() => runStep("match")}>
          Review Match
        </button>
        <button disabled={!candidate || !job || !matchResult} onClick={() => runStep("package")}>
          Generate Package
        </button>
        <button disabled={!candidateId || !jobId} onClick={() => runStep("application")}>
          Create Application
        </button>
        <button disabled={!application} onClick={() => runStep("pipeline")}>
          Move To Applied
        </button>
        <button disabled={!application || !candidateId || !jobId} onClick={() => runStep("outcome")}>
          Record Outcome
        </button>
      </div>
      {message && <p className="notice success">{message}</p>}
    </Panel>
  );
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
