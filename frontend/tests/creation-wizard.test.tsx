import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";

import CreationWizard from "@/components/creation-wizard/CreationWizard";

vi.mock("@/components/review-room/ChatPanel", () => ({
  default: () => <div data-testid="chat-panel-mock" />,
}));

describe("CreationWizard", () => {
  afterEach(() => cleanup());

  test("shows first step movie input", () => {
    render(<CreationWizard />);
    expect(screen.getByTestId("creation-wizard")).toBeInTheDocument();
    expect(screen.getByTestId("movie-input-step")).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "调研" })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "配图" })).toBeDisabled();
  });
});
