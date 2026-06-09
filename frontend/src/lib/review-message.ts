import type { ReviewMessageRecord } from "@/lib/api";
import { resolveMbti } from "@/lib/chat-avatar";
import type { ReviewStreamMessage } from "@/lib/review-types";

export function sortReviewMessages(messages: ReviewStreamMessage[]): ReviewStreamMessage[] {
  return [...messages].sort((left, right) => {
    const leftTime = left.created_at ? Date.parse(left.created_at) : 0;
    const rightTime = right.created_at ? Date.parse(right.created_at) : 0;
    if (leftTime !== rightTime) return leftTime - rightTime;
    if (left.round !== right.round) return left.round - right.round;
    return left.id.localeCompare(right.id);
  });
}

export function toStreamMessage(record: ReviewMessageRecord): ReviewStreamMessage {
  const role = record.role as ReviewStreamMessage["role"];
  const attachment = record.attachment ?? undefined;
  const message: ReviewStreamMessage = {
    id: record.id,
    role,
    content: record.content,
    round: record.round,
    nickname:
      record.nickname ??
      (role === "user"
        ? "你"
        : role === "moderator"
          ? "主持人"
          : role === "writer"
            ? "Writer"
            : role === "system"
              ? "系统"
              : "审稿人"),
    avatar_url: record.avatar_url ?? undefined,
    mbti: record.mbti ?? undefined,
    persona_id: record.persona_id ?? undefined,
    attachment,
    created_at: record.created_at,
  };
  if (!message.mbti) {
    message.mbti = resolveMbti(message);
  }
  return message;
}
