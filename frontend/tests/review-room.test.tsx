import { cleanup, render, screen, waitFor, within } from "@testing-library/react";
import { afterEach, beforeEach, describe, expect, test, vi } from "vitest";

import ChatPanel from "@/components/review-room/ChatPanel";
import ReviewerBubble from "@/components/review-room/ReviewerBubble";

type Listener = (event: MessageEvent<string>) => void;

class MockEventSource {
  static instances: MockEventSource[] = [];
  url: string;
  listeners = new Map<string, Listener[]>();
  closed = false;

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(type: string, listener: Listener) {
    const current = this.listeners.get(type) ?? [];
    current.push(listener);
    this.listeners.set(type, current);
  }

  close() {
    this.closed = true;
  }

  emit(type: string, data: Record<string, unknown>) {
    const payload = new MessageEvent(type, {
      data: JSON.stringify(data),
    });
    for (const listener of this.listeners.get(type) ?? []) {
      listener(payload);
    }
  }
}

describe("Review Room", () => {
  beforeEach(() => {
    MockEventSource.instances = [];
    vi.stubGlobal("EventSource", MockEventSource);
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        json: async () => ({ session_id: "sess-1", messages: [] }),
      })
    );
  });

  afterEach(() => {
    cleanup();
    vi.unstubAllGlobals();
  });

  test("reviewer bubble renders avatar and content", () => {
    render(
      <ReviewerBubble
        message={{
          id: "msg-1",
          role: "reviewer",
          round: 1,
          nickname: "文艺青年",
          content: "标题可以更锋利一点。",
        }}
      />
    );

    expect(screen.getByTestId("message-avatar")).toBeInTheDocument();
    expect(screen.getByText("文艺青年")).toBeInTheDocument();
    expect(screen.getByText("标题可以更锋利一点。")).toBeInTheDocument();
  });

  test("reviewer bubble renders pros and cons sections", () => {
    render(
      <ReviewerBubble
        message={{
          id: "msg-2",
          role: "reviewer",
          round: 1,
          nickname: "毒舌影评人",
          content: "【亮点】开头有画面感。\n\n【待改】标签太泛。",
          attachment: {
            pros: "开头有画面感。",
            cons: "标签太泛，建议换成更具体的话题词。",
          },
        }}
      />
    );

    expect(screen.getByText("亮点")).toBeInTheDocument();
    expect(screen.getByText("待改")).toBeInTheDocument();
    expect(screen.getByText("开头有画面感。")).toBeInTheDocument();
    expect(screen.getByText("标签太泛，建议换成更具体的话题词。")).toBeInTheDocument();
  });

  test("chat panel renders reviewer messages from mocked EventSource", async () => {
    render(<ChatPanel sessionId="sess-1" phase="text" autoStart />);

    await waitFor(() => {
      expect(MockEventSource.instances.length).toBeGreaterThanOrEqual(1);
    });

    const source = MockEventSource.instances[0];
    expect(source.url).toContain("/api/v1/sessions/sess-1/review/stream?phase=text");

    source.emit("reviewer_message", {
      id: "r1",
      nickname: "毒舌影评人",
      mbti: "INTJ",
      content: "正文有点空泛，建议补一个具体镜头。",
      round: 1,
    });

    const panel = await screen.findByTestId("chat-panel");
    await waitFor(() => {
      expect(within(panel).getByTestId("message-avatar")).toBeInTheDocument();
      expect(within(panel).getByText("INTJ")).toBeInTheDocument();
      expect(within(panel).getByText("毒舌影评人")).toBeInTheDocument();
      expect(
        within(panel).getByText("正文有点空泛，建议补一个具体镜头。")
      ).toBeInTheDocument();
    });

    expect(screen.getByRole("button", { name: /继续优化/i })).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /满意定稿/i })).toBeInTheDocument();
  });
});
