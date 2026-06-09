export type ReviewPhase = "text" | "image";

export type ReviewRole = "reviewer" | "moderator" | "writer" | "user" | "system";

export type ReviewStreamMessage = {
  id: string;
  role: ReviewRole;
  content: string;
  round: number;
  nickname?: string;
  avatar_url?: string;
  mbti?: string;
  persona_id?: string;
  attachment?: Record<string, unknown>;
  created_at?: string;
};

export type ReviewRoundGroup = {
  round: number;
  messages: ReviewStreamMessage[];
  collapsed: boolean;
};

export const SSE_EVENTS = [
  "round_started",
  "draft_created",
  "reviewer_message",
  "moderator_summary",
  "writer_revision",
  "draft_updated",
  "image_updated",
  "round_complete",
  "error",
] as const;

export type SseEventName = (typeof SSE_EVENTS)[number];
