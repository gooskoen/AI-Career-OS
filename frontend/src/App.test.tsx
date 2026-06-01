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
  render(<App />);
}

async function mockFetch(input: RequestInfo | URL) {
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
    return json([{ display_name: "Demo Candidate", headline: "AI Operator", skills: ["Python"] }]);
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
