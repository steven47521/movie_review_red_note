import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";

import DashboardPage from "@/app/dashboard/page";

vi.mock("next/navigation", () => ({
  useRouter: () => ({ replace: vi.fn() }),
  useSearchParams: () => new URLSearchParams(),
}));

vi.mock("@/lib/api", () => ({
  api: {
    listSessions: vi.fn().mockResolvedValue({ sessions: [], count: 0 }),
    getSession: vi.fn(),
    getDraft: vi.fn(),
    listImages: vi.fn(),
    getTimeline: vi.fn(),
    listReviewMessages: vi.fn().mockResolvedValue({ session_id: "", messages: [] }),
  },
}));

describe("DashboardPage", () => {
  afterEach(() => cleanup());

  test("dashboard uses Web-Prototype workspace shell", async () => {
    render(<DashboardPage />);
    expect(await screen.findByTestId("workspace-shell")).toBeInTheDocument();
    expect(screen.getByText("片语 RedNote")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /新建会话/i })).toBeInTheDocument();
  });
});
