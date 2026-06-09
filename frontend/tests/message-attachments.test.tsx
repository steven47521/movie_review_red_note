import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, test } from "vitest";

import MessageAttachments from "@/components/workspace/MessageAttachments";

describe("MessageAttachments", () => {
  afterEach(() => cleanup());

  test("renders image preview with resolved backend url", () => {
    render(
      <MessageAttachments
        attachment={{
          images: [{ type: "cover", url: "/static/images/s1/cover.jpg", label: "封面" }],
        }}
      />
    );

    const img = screen.getByRole("img", { name: "封面" });
    expect(img).toHaveAttribute("src", "http://localhost:8000/static/images/s1/cover.jpg");
  });
});
