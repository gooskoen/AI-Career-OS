import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { App } from "./App";

let packageFailure = false;

const dashboard = {
  active_applications: 3,
  interviews_scheduled: 1,
  offers_received: 1,
  hires: 0,
  rejections: 2,
  pipeline_totals: {
    drafted: 1,
    applied: 1,
    recruiter_replied: 0,
    interview_scheduled: 1,
    interview_completed: 0,
    offer_received: 1,
    hired: 0,
    rejected: 2,
    withdrawn: 0
  }
};

const funnel = {
  applications: 5,
  recruiter_replies: 2,
  interviews: 1,
  offers: 1,
  hires: 0,
  application_to_reply_rate: 0.4,
  reply_to_interview_rate: 0.5,
  interview_to_offer_rate: 1,
  offer_to_hire_rate: 0
};

const board = {
  drafted: [{ id: "drafted-application", status: "drafted", source: "manual" }],
  applied: [],
  recruiter_replied: [],
  interview_scheduled: [],
  interview_completed: [],
  offer_received: [],
  hired: [],
  rejected: [],
  withdrawn: []
};

const summary = {
  application: { id: "drafted-application", status: "drafted", source: "manual" },
  current_status: "drafted",
  next_action: "follow up recruiter",
  next_action_due: "2026-06-10",
  latest_notes: [{ note: "Prepare STAR story" }],
  artifact_readiness: {
    match_ready: true,
    package_ready: true,
    intelligence_ready: false
  },
  latest_outcome: { outcome: "applied" },
  status_history: [{ new_status: "drafted" }]
};

const candidate = {
  id: "candidate-1",
  name: "Koen Demo",
  display_name: "Koen Demo",
  headline: "AI Operations Lead",
  location: "Belgium",
  summary: "Builds practical AI operating systems.",
  skills: ["Python", "SQL", "workflow automation"],
  target_roles: ["AI Operations Lead"],
  experience_highlights: ["Led workflow automation delivery."]
};

const job = {
  id: "job-1",
  title: "AI Operations Lead",
  company: "ExampleTech",
  location: "Remote",
  description: "Lead workflow automation, reporting, analytics, and stakeholder delivery.",
  required_skills: ["Python", "SQL", "workflow automation"],
  nice_to_have_skills: ["BPMN"]
};

const match = {
  id: "match-1",
  score: 86,
  matched_skills: ["Python", "SQL", "workflow automation"],
  missing_skills: ["BPMN"],
  strengths: [
    {
      skill: "Python",
      contribution: 30,
      reason: "Required skill match",
      evidence: ["Python"]
    }
  ],
  gaps: {
    critical: [],
    moderate: ["BPMN"],
    optional: []
  },
  recommended_actions: ["Add BPMN modelling project to CV"],
  recommendation: "Strong fit with a focused BPMN proof point."
};

const applicationPackage = {
  tailored_summary: "Tailored summary for AI Operations Lead.",
  cover_letter: "Short cover letter draft.",
  talking_points: ["Automation delivery", "Reporting discipline"],
  key_strengths: ["Python", "workflow automation"],
  risk_gaps: ["BPMN"],
  recommended_cv_edits: ["Add BPMN modelling project to CV"]
};

describe("App", () => {
  beforeEach(() => {
    packageFailure = false;
    sessionStorage.clear();
    vi.stubGlobal("fetch", vi.fn(mockFetch));
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  test("logs in and renders the dashboard intake wizard", async () => {
    render(<App />);

    const loginButtons = screen.getAllByRole("button", { name: "Login" });
    fireEvent.click(loginButtons[loginButtons.length - 1]);

    expect(await screen.findByText("Active Applications")).toBeInTheDocument();
    expect(await screen.findByText("Funnel Summary")).toBeInTheDocument();
    expect(await screen.findByText("Pipeline Totals")).toBeInTheDocument();
    expect(await screen.findByText("User Intake Wizard")).toBeInTheDocument();
  });

  test("protects app routes until authentication succeeds", () => {
    render(<App />);

    expect(screen.getAllByRole("button", { name: "Login" })).toHaveLength(2);
    expect(screen.queryByText("Dashboard")).not.toBeInTheDocument();
  });

  test("creates a candidate through the intake form", async () => {
    renderAuthenticatedApp();

    await createCandidateFromWizard();

    expect(await screen.findByText("candidate saved")).toBeInTheDocument();
    expect(screen.getByText("Candidate ready: Koen Demo")).toBeInTheDocument();
  });

  test("imports a pasted job description through existing job intake", async () => {
    renderAuthenticatedApp();

    await createCandidateFromWizard();
    await importTextJobFromWizard();

    expect(await screen.findByText("job imported")).toBeInTheDocument();
    expect(screen.getAllByText("AI Operations Lead").length).toBeGreaterThan(1);
    expect(screen.getByText("ExampleTech")).toBeInTheDocument();
  });

  test("imports a job URL through existing job intake", async () => {
    renderAuthenticatedApp();

    await createCandidateFromWizard();
    fireEvent.click(await screen.findByRole("button", { name: "Paste URL" }));
    fireEvent.change(screen.getByLabelText("Job URL"), {
      target: { value: "https://example.com/jobs/ai-operations-lead" }
    });
    fireEvent.click(screen.getByRole("button", { name: "Import Job" }));

    expect(await screen.findByText("job imported")).toBeInTheDocument();
    expect(screen.getByText("ExampleTech")).toBeInTheDocument();
  });

  test("generates and displays a readable match review", async () => {
    renderAuthenticatedApp();

    await createCandidateFromWizard();
    await importTextJobFromWizard();
    fireEvent.click(screen.getByRole("button", { name: "Generate Match" }));

    expect(await screen.findByText("86% match")).toBeInTheDocument();
    expect(screen.getByText("Python")).toBeInTheDocument();
    expect(screen.getByText("BPMN")).toBeInTheDocument();
    expect(screen.getByText("Add BPMN Modelling Project To CV")).toBeInTheDocument();
  });

  test("progresses from intake to application creation", async () => {
    renderAuthenticatedApp();

    await createCandidateFromWizard();
    await importTextJobFromWizard();
    fireEvent.click(screen.getByRole("button", { name: "Generate Match" }));
    expect(await screen.findByText("match generated")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Generate Package" }));
    expect(await screen.findByText("package generated")).toBeInTheDocument();
    expect(screen.getByText("Tailored summary for AI Operations Lead.")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Create Application" }));
    expect(await screen.findByText("application created")).toBeInTheDocument();
    expect(screen.getByText("Status: Drafted")).toBeInTheDocument();
  });

  test("shows useful API errors during wizard actions", async () => {
    packageFailure = true;
    renderAuthenticatedApp();

    await createCandidateFromWizard();
    await importTextJobFromWizard();
    fireEvent.click(screen.getByRole("button", { name: "Generate Match" }));
    expect(await screen.findByText("match generated")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Generate Package" }));

    expect(await screen.findByText("Package service unavailable")).toBeInTheDocument();
    expect(screen.queryByText("package generated")).not.toBeInTheDocument();
  });

  test("renders the kanban board and application detail", async () => {
    renderAuthenticatedApp();

    fireEvent.click(await screen.findByRole("button", { name: "Applications" }));
    expect(await screen.findByTestId("kanban-board")).toBeInTheDocument();

    fireEvent.click(await screen.findByText("drafted-"));

    expect(await screen.findByTestId("application-detail")).toBeInTheDocument();
    expect(screen.getByText("follow up recruiter")).toBeInTheDocument();
    expect(screen.getByText("Prepare STAR Story")).toBeInTheDocument();
  });

  test("renders insights from reporting endpoints", async () => {
    renderAuthenticatedApp();

    fireEvent.click(await screen.findByRole("button", { name: "Insights" }));

    expect(await screen.findByText("Outcome Analytics")).toBeInTheDocument();
    expect(screen.getByText("Skill Analytics")).toBeInTheDocument();
    expect(screen.getByText("Recommendation Analytics")).toBeInTheDocument();
  });

  test("logout returns to login screen", async () => {
    renderAuthenticatedApp();

    fireEvent.click(await screen.findByRole("button", { name: "Logout" }));

    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Login" })).toHaveLength(2);
    });
  });
});

async function createCandidateFromWizard() {
  await screen.findByText("User Intake Wizard");
  fireEvent.change(screen.getByLabelText("Full Name"), { target: { value: "Koen Demo" } });
  fireEvent.change(screen.getByLabelText("Headline"), {
    target: { value: "AI Operations Lead" }
  });
  fireEvent.change(screen.getByLabelText("Location"), { target: { value: "Belgium" } });
  fireEvent.change(screen.getByLabelText("Summary"), {
    target: { value: "Builds practical AI operating systems." }
  });
  fireEvent.change(screen.getByLabelText("Skills"), {
    target: { value: "Python, SQL, workflow automation" }
  });
  fireEvent.change(screen.getByLabelText("Target Roles"), {
    target: { value: "AI Operations Lead" }
  });
  fireEvent.change(screen.getByLabelText("Experience Highlights"), {
    target: { value: "Led workflow automation delivery." }
  });
  fireEvent.click(screen.getByRole("button", { name: "Save Candidate" }));
  await screen.findByText("candidate saved");
}

async function importTextJobFromWizard() {
  fireEvent.change(screen.getByLabelText("Job Description"), {
    target: {
      value: [
        "AI Operations Lead",
        "ExampleTech",
        "Remote",
        "Required skills: Python, SQL, workflow automation"
      ].join("\n")
    }
  });
  fireEvent.click(screen.getByRole("button", { name: "Import Job" }));
  await screen.findByText("job imported");
}

function renderAuthenticatedApp() {
  sessionStorage.setItem("ai-career-os.access-token", "access");
  sessionStorage.setItem("ai-career-os.refresh-token", "refresh");
  sessionStorage.setItem(
    "ai-career-os.user",
    JSON.stringify({ id: "user-1", email: "demo@example.com", display_name: "Demo User" })
  );
  render(<App />);
}

async function mockFetch(input: RequestInfo | URL, init?: RequestInit) {
  const url = String(input);
  const method = init?.method ?? "GET";
  if (url.endsWith("/auth/login")) {
    return json({
      access_token: "access",
      refresh_token: "refresh",
      user: { id: "user-1", email: "demo@example.com", display_name: "Demo User" }
    });
  }
  if (url.endsWith("/reporting/dashboard")) {
    return json(dashboard);
  }
  if (url.endsWith("/reporting/funnel")) {
    return json(funnel);
  }
  if (url.endsWith("/reporting/outcomes")) {
    return json({
      rejection_rate: 0.4,
      offer_rate: 0.2,
      hire_rate: 0,
      outcome_trends: {}
    });
  }
  if (url.endsWith("/reporting/skills")) {
    return json({
      strongest_performing_skills: ["Python"],
      weakest_performing_skills: ["BPMN"],
      most_successful_skills: ["Python"],
      rejection_linked_skills: ["BPMN"]
    });
  }
  if (url.endsWith("/reporting/recommendations")) {
    return json({
      recommendations_followed: { cv_edits_applied: 1 },
      recommendations_ignored: { cv_edits_applied: 1 },
      recommendation_usage_rates: { cv_edits_applied: 0.5 }
    });
  }
  if (url.endsWith("/applications/board")) {
    return json(board);
  }
  if (url.endsWith("/applications/drafted-application/summary")) {
    return json(summary);
  }
  if (url.endsWith("/candidates") && method === "POST") {
    return json(candidate);
  }
  if (url.endsWith("/candidates")) {
    return json([candidate]);
  }
  if (url.endsWith("/jobs/import-text") || url.endsWith("/jobs/import-url")) {
    return json({ job, duplicate: false, match: null });
  }
  if (url.endsWith("/match")) {
    return json(match);
  }
  if (url.endsWith("/matches/persist")) {
    return json(match);
  }
  if (url.endsWith("/applications/package")) {
    if (packageFailure) {
      return jsonError("Package service unavailable", 503);
    }
    return json(applicationPackage);
  }
  if (url.endsWith("/applications") && method === "POST") {
    return json({ id: "application-1", status: "drafted", source: "private_beta_ui" });
  }
  return json({});
}

function json(body: unknown) {
  return Promise.resolve(
    new Response(JSON.stringify(body), {
      status: 200,
      headers: { "Content-Type": "application/json" }
    })
  );
}

function jsonError(message: string, status: number) {
  return Promise.resolve(
    new Response(JSON.stringify({ error: { message } }), {
      status,
      headers: { "Content-Type": "application/json" }
    })
  );
}
