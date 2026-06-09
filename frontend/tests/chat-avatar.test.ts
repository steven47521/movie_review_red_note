import { describe, expect, test } from "vitest";

import { avatarLabel, avatarTone, resolveMbti } from "@/lib/chat-avatar";
import type { ReviewStreamMessage } from "@/lib/review-types";

describe("chat avatar", () => {
  test("reviewer uses MBTI label from attachment when API mbti is missing", () => {
    const message: ReviewStreamMessage = {
      id: "m1",
      role: "reviewer",
      content: "不错",
      round: 1,
      nickname: "INTJ影评人·30s",
      attachment: { mbti: "INTJ" },
    };

    expect(resolveMbti(message)).toBe("INTJ");
    expect(avatarLabel(message)).toBe("INTJ");
    expect(avatarTone(message)).toBe("#5e6ad2");
  });

  test("reviewer falls back to nickname prefix MBTI", () => {
    const message: ReviewStreamMessage = {
      id: "m2",
      role: "reviewer",
      content: "可以",
      round: 1,
      nickname: "ENFP影评人·20s",
    };

    expect(resolveMbti(message)).toBe("ENFP");
    expect(avatarLabel(message)).toBe("ENFP");
  });
});
