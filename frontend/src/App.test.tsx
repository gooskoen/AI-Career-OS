import { cleanup, fireEvent, render, screen, waitFor } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";
import { App } from "./App";

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

describe("App", () => {
  beforeEach(() => {
    sessionStorage.clear();
    vi.stubGlobal("fetch", vi.fn(mockFetch));
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  test("logs in and renders the dashboard", async () => {
    render(<App />);

    const loginButtons = screen.getAllByRole("button", { name: "Login" });
    fireEvent.click(loginButtons[loginButtons.length - 1]);

    expect(await screen.findByText("Active Applications")).toBeInTheDocument();
    expect(await screen.findByText("Funnel Summary")).toBeInTheDocument();
    expect(await screen.findByText("Pipeline Totals")).toBeInTheDocument();
    expect(await screen.findByText("Beta Workflow Validation")).toBeInTheDocument();
  });

  test("protects app routes until authentication succeeds", () => {
    render(<App />);

    expect(screen.getAllByRole("button", { name: "Login" })).toHaveLength(2);
    expect(screen.queryByText("Dashboard")).not.toBeInTheDocument();
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

  test("guided workflow marks Generate Package complete after package generation", async () => {
    const { container } = renderAuthenticatedApp();

    await runWorkflowThroughMatch();
    fireEvent.click(screen.getByRole("button", { name: "Generate Package" }));

    expect(await screen.findByText("package generated")).toBeInTheDocument();
    expect(workflowChip(container, "Generate Package")).toHaveClass("done");
  });

  test("guided workflow marks View Insights complete after opening insights", async () => {
    const { container } = renderAuthenticatedApp();

    fireEvent.click(await screen.findByRole("button", { name: "View Insights" }));

    expect(await screen.findByText("Outcome Analytics")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Dashboard" }));

    expect(await screen.findByText("Beta Workflow Validation")).toBeInTheDocument();
    expect(workflowChip(container, "View Insights")).toHaveClass("done");
  });

  test("recording an outcome does not skip unresolved package or insights steps", async () => {
    const { container } = renderAuthenticatedApp();

    await runWorkflowThroughMatch();
    fireEvent.click(screen.getByRole("button", { name: "Create Application" }));
    expect(await screen.findByText("application created")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Move To Applied" }));
    expect(await screen.findByText("pipeline updated")).toBeInTheDocument();

    fireEvent.click(screen.getByRole("button", { name: "Record Outcome" }));
    expect(await screen.findByText("outcome recorded")).toBeInTheDocument();

    expect(workflowChip(container, "Record Outcome")).toHaveClass("done");
    expect(workflowChip(container, "Generate Package")).toHaveClass("todo");
    expect(workflowChip(container, "View Insights")).toHaveClass("todo");
  });

  test("logout returns to login screen", async () => {
    renderAuthenticatedApp();

    fireEvent.click(await screen.findByRole("button", { name: "Logout" }));

    await waitFor(() => {
      expect(screen.getAllByRole("button", { name: "Login" })).toHaveLength(2);
    });
  });
});

function renderAuthenticatedApp() {
  sessionStorage.setItem("ai-career-os.access-token", "access");
  sessionStorage.setItem("ai-career-os.refresh-token", "refresh");
  sessionStorage.setItem(
    "ai-career-os.user",
    JSON.stringify({ id: "user-1", email: "demo@example.com", display_name: "Demo User" })
  );
  return render(<App />);
}

async function runWorkflowThroughMatch() {
  fireEvent.click(await screen.findByRole("button", { name: "Create Candidate" }));
  expect(await screen.findByText("candidate created")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Import Job" }));
  expect(await screen.findByText("job imported")).toBeInTheDocument();

  fireEvent.click(screen.getByRole("button", { name: "Review Match" }));
  expect(await screen.findByText("match reviewed")).toBeInTheDocument();
}

function workflowChip(container: HTMLElement, label: string) {
  const chip = Array.from(container.querySelectorAll(".workflow-steps span")).find(
    (element) => element.textContent === label
  );
  expect(chip).toBeDefined();
  return chip as HTMLElement;
}

async function mockFetch(input: RequestInfo | URL, init?: RequestInit) {
  const url = String(input);
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
  if (url.endsWith("/candidates")) {
    if (init?.method === "POST") {
      return json({
        id: "candidate-1",
        name: "Private Beta Candidate",
        headline: "AI Operations and Reporting Specialist",
        skills: ["Python"]
      });
    }
    return json([{ display_name: "Demo Candidate", headline: "AI Operator", skills: ["Python"] }]);
  }
  if (url.endsWith("/jobs/import-text")) {
    return json({
      job: {
        id: "job-1",
        title: "AI Operations Lead",
        company: "ExampleTech",
        description: "Lead workflow automation.",
        required_skills: ["Python"],
        nice_to_have_skills: []
      },
      duplicate: false,
      match: { id: "match-imported" }
    });
  }
  if (url.endsWith("/matches/persist")) {
    return json({ id: "match-1", score: 86, strengths: ["Python"], gaps: [] });
  }
  if (url.endsWith("/applications/package")) {
    return json({
      tailored_summary: "Private beta package summary",
      cover_letter: "Short cover letter",
      talking_points: ["Workflow automation"]
    });
  }
  if (url.endsWith("/applications")) {
    return json({ id: "application-1", status: "drafted", source: "private_beta_ui" });
  }
  if (url.endsWith("/applications/application-1/transition")) {
    return json({ id: "application-1", status: "applied", source: "private_beta_ui" });
  }
  if (url.endsWith("/outcomes")) {
    return json({ id: "outcome-1", outcome: "applied" });
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
