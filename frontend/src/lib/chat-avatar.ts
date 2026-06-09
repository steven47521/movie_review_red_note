import type { ReviewStreamMessage } from "@/lib/review-types";

const ROLE_AVATAR_LABEL: Record<string, string> = {
  user: "你",
  moderator: "主持",
  writer: "改稿",
  system: "系统",
};

const MBTI_TONES: Record<string, string> = {
  INTJ: "#5e6ad2",
  INTP: "#6b7cff",
  ENTJ: "#4f46e5",
  ENTP: "#7c3aed",
  INFJ: "#0d9488",
  INFP: "#14b8a6",
  ENFJ: "#059669",
  ENFP: "#10b981",
  ISTJ: "#d97706",
  ISFJ: "#ea580c",
  ESTJ: "#c2410c",
  ESFJ: "#f97316",
  ISTP: "#db2777",
  ISFP: "#e11d48",
  ESTP: "#be185d",
  ESFP: "#ec4899",
};

const MBTI_PATTERN = /^([IE][SN][FT][JP])/i;

function hashHue(seed: string): number {
  let hash = 0;
  for (let i = 0; i < seed.length; i += 1) {
    hash = (hash * 31 + seed.charCodeAt(i)) >>> 0;
  }
  return hash % 360;
}

export function resolveMbti(message: ReviewStreamMessage): string | undefined {
  if (message.mbti) {
    return message.mbti.toUpperCase();
  }

  const attachmentMbti = message.attachment?.mbti;
  if (typeof attachmentMbti === "string" && attachmentMbti.length === 4) {
    return attachmentMbti.toUpperCase();
  }

  const nicknameMatch = message.nickname?.match(MBTI_PATTERN);
  if (nicknameMatch) {
    return nicknameMatch[1].toUpperCase();
  }

  return undefined;
}

export function avatarLabel(message: ReviewStreamMessage): string {
  const mbti = resolveMbti(message);
  if (message.role === "reviewer" && mbti) {
    return mbti;
  }
  if (message.nickname && message.role !== "reviewer") {
    return message.nickname.slice(0, 2);
  }
  return ROLE_AVATAR_LABEL[message.role] ?? "AI";
}

export function avatarTone(message: ReviewStreamMessage): string {
  if (message.role === "user") {
    return "var(--accent)";
  }
  if (message.role === "moderator") {
    return "#5e6ad2";
  }
  if (message.role === "writer") {
    return "#17a34a";
  }
  if (message.role === "system") {
    return "#6b7280";
  }

  const mbti = resolveMbti(message);
  if (mbti) {
    return MBTI_TONES[mbti] ?? `hsl(${hashHue(mbti)} 58% 46%)`;
  }

  const seed = message.persona_id ?? message.nickname ?? message.id;
  return `hsl(${hashHue(seed)} 58% 46%)`;
}

export function isReviewerMbtiAvatar(message: ReviewStreamMessage): boolean {
  return message.role === "reviewer" && Boolean(resolveMbti(message));
}
