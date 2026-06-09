import type { Draft, SessionSummary } from "@/lib/api";

export type SessionFilter = "all" | "text" | "image" | "done";

export const STAGE_ORDER = [
  { key: "research", label: "调研", hint: "影片元数据与主流观点" },
  { key: "angle", label: "选题", hint: "切入点与论证路线" },
  { key: "draft", label: "初稿", hint: "标题、引子、正文、标签" },
  { key: "review", label: "评审", hint: "多人回合制审稿" },
  { key: "assets", label: "配图", hint: "封面、金句卡、氛围图" },
] as const;

export const STATUS_LABELS: Record<string, string> = {
  created: "已创建",
  researching: "调研中",
  angles_ready: "待选题",
  route_ready: "待定路线",
  drafting: "成稿中",
  text_reviewing: "文案评审中",
  text_finalized: "文案已定",
  image_generating: "配图生成中",
  image_reviewing: "配图审稿中",
  completed: "已完成",
};

export function statusPillClass(status: string): string {
  if (status === "completed") return "is-success";
  if (status === "text_reviewing" || status === "image_reviewing") return "is-warn";
  if (status === "image_generating") return "is-danger";
  if (status === "angles_ready" || status === "route_ready") return "is-neutral";
  return "is-muted";
}

export function stageIndexForStatus(status: string): number {
  const map: Record<string, number> = {
    created: 0,
    researching: 0,
    angles_ready: 1,
    route_ready: 1,
    drafting: 2,
    text_reviewing: 3,
    text_finalized: 4,
    image_generating: 4,
    image_reviewing: 4,
    completed: 4,
  };
  return map[status] ?? 0;
}

export function primaryActionForStatus(status: string): string {
  if (status === "text_reviewing") return "继续评审";
  if (status === "image_reviewing") return "继续配图";
  if (status === "angles_ready") return "继续选题";
  if (status === "route_ready") return "继续定路线";
  if (status === "text_finalized" || status === "image_generating") return "生成配图";
  if (status === "completed") return "查看归档";
  return "继续创作";
}

export function sessionMatchesFilter(session: SessionSummary, filter: SessionFilter): boolean {
  if (filter === "all") return true;
  if (filter === "text") return session.status === "text_reviewing";
  if (filter === "image") return session.status === "image_reviewing";
  if (filter === "done") return session.status === "completed";
  return true;
}

export function formatUpdatedAt(value: string): string {
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) return value;
  const now = new Date();
  const sameDay =
    date.getFullYear() === now.getFullYear() &&
    date.getMonth() === now.getMonth() &&
    date.getDate() === now.getDate();
  if (sameDay) {
    return `今天 ${date.getHours().toString().padStart(2, "0")}:${date.getMinutes().toString().padStart(2, "0")}`;
  }
  return date.toLocaleDateString("zh-CN");
}

export function sessionOverview(session: SessionSummary): string {
  const label = STATUS_LABELS[session.status] ?? session.status;
  return `${session.movie_title} · ${label}`;
}

export function draftExcerpt(draft: Draft, maxLen = 120): string {
  const text = draft.body.replace(/\s+/g, " ").trim();
  if (text.length <= maxLen) return text;
  return `${text.slice(0, maxLen)}…`;
}
