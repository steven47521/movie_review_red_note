import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, test, vi } from "vitest";

import DraftEditor from "@/components/draft-editor/DraftEditor";

const sampleDraft = {
  version: 1,
  title: "肖申克的救赎：希望如何穿过高墙",
  hooks: ["有些鸟注定不会被关住", "希望是好事，也许是人间至善"],
  body: "这部电影真正打动我的，是安迪在绝望里仍然保留行动能力。",
  tags: ["#经典电影", "#肖申克", "#影评", "#希望", "#自由"],
};

describe("DraftEditor", () => {
  afterEach(() => cleanup());

  test("renders draft fields and save action", async () => {
    const onSave = vi.fn();
    render(<DraftEditor draft={sampleDraft} onSave={onSave} />);

    expect(screen.getByDisplayValue(sampleDraft.title)).toBeInTheDocument();
    expect(screen.getByDisplayValue(sampleDraft.body)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /保存编辑/i })).toBeInTheDocument();
  });

  test("calls onSave with edited body", async () => {
    const onSave = vi.fn();
    render(<DraftEditor draft={sampleDraft} onSave={onSave} />);

    const bodyField = screen.getByLabelText(/正文/i);
    await userEvent.clear(bodyField);
    await userEvent.type(bodyField, "改写后的正文。");
    await userEvent.click(screen.getByRole("button", { name: /保存编辑/i }));

    expect(onSave).toHaveBeenCalledWith(
      expect.objectContaining({ body: "改写后的正文。" })
    );
  });
});
