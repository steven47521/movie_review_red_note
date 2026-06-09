const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const DEFAULT_TIMEOUT_MS = 180_000;

export function resolveAssetUrl(url: string): string {
  if (!url) return url;
  if (url.startsWith("http://") || url.startsWith("https://")) return url;
  return `${API_BASE}${url.startsWith("/") ? "" : "/"}${url}`;
}

export type Angle = {
  id: string;
  title: string;
  description?: string;
};

export type Route = {
  id: string;
  title: string;
  outline?: string[];
};

export type Draft = {
  version: number;
  title: string;
  hooks: string[];
  body: string;
  tags: string[];
  review_round?: number;
};

export type ImageAsset = {
  id: string;
  type: string;
  url: string;
  style_key?: string;
  version?: number;
  review_round?: number;
};

export type ResearchResult = {
  session_id: string;
  movie: {
    title: string;
    year?: number;
    director?: string;
    genres?: string[];
  };
  opinions: Array<{ text: string; source?: string }>;
  sources_summary?: string;
};

export type ReviewMessageRecord = {
  id: string;
  phase: string;
  round: number;
  role: string;
  persona_id?: string | null;
  nickname?: string | null;
  avatar_url?: string | null;
  mbti?: string | null;
  content: string;
  scores?: Record<string, unknown> | null;
  attachment?: Record<string, unknown> | null;
  created_at?: string;
};

export type SessionSummary = {
  id: string;
  movie_title: string;
  status: string;
  is_favorite: boolean;
  is_published: boolean;
  created_at: string;
  updated_at: string;
};

async function request<T>(
  path: string,
  init?: RequestInit & { timeoutMs?: number }
): Promise<T> {
  const timeoutMs = init?.timeoutMs ?? DEFAULT_TIMEOUT_MS;
  const controller = new AbortController();
  const timer = window.setTimeout(() => controller.abort(), timeoutMs);
  const { timeoutMs: _ignored, ...fetchInit } = init ?? {};

  let response: Response;
  try {
    response = await fetch(`${API_BASE}${path}`, {
      ...fetchInit,
      signal: controller.signal,
      headers: {
        "Content-Type": "application/json",
        ...(fetchInit.headers ?? {}),
      },
    });
  } catch (err) {
    if (err instanceof DOMException && err.name === "AbortError") {
      throw new Error(
        `请求超时（${Math.round(timeoutMs / 1000)} 秒）。AI 可能仍在处理，请稍候刷新重试。`
      );
    }
    throw new Error(
      `无法连接后端 ${API_BASE}。请先在项目根目录运行：powershell -File scripts/start-backend.ps1`
    );
  } finally {
    window.clearTimeout(timer);
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as { detail?: string };
    throw new Error(body.detail ?? `Request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const api = {
  createSession(title: string, year?: number) {
    return request<{ id: string; movie_title: string; status: string }>(
      "/api/v1/sessions",
      {
        method: "POST",
        body: JSON.stringify({ title, year }),
      }
    );
  },

  research(sessionId: string) {
    return request<ResearchResult>(`/api/v1/sessions/${sessionId}/research`, {
      method: "POST",
      timeoutMs: 120_000,
    });
  },

  getResearch(sessionId: string) {
    return request<ResearchResult>(`/api/v1/sessions/${sessionId}/research`, {
      timeoutMs: 30_000,
    });
  },

  getAngles(sessionId: string) {
    return request<{ angles: Angle[]; count: number }>(
      `/api/v1/sessions/${sessionId}/angles`,
      { timeoutMs: 15_000 }
    );
  },

  generateAngles(sessionId: string, force = false) {
    const query = force ? "?force=true" : "";
    return request<{ angles: Angle[]; count: number }>(
      `/api/v1/sessions/${sessionId}/angles/generate${query}`,
      { method: "POST", timeoutMs: 120_000 }
    );
  },

  selectAngle(sessionId: string, angle: Angle) {
    return request(`/api/v1/sessions/${sessionId}/angles/select`, {
      method: "POST",
      body: JSON.stringify({
        angle_id: angle.id,
        title: angle.title,
        description: angle.description ?? "",
      }),
    });
  },

  getRoutes(sessionId: string) {
    return request<{ routes: Route[]; count: number }>(
      `/api/v1/sessions/${sessionId}/routes`,
      { timeoutMs: 15_000 }
    );
  },

  generateRoutes(sessionId: string, force = false) {
    const query = force ? "?force=true" : "";
    return request<{ routes: Route[]; count: number }>(
      `/api/v1/sessions/${sessionId}/routes/generate${query}`,
      { method: "POST", timeoutMs: 120_000 }
    );
  },

  selectRoute(sessionId: string, route: Route) {
    return request(`/api/v1/sessions/${sessionId}/routes/select`, {
      method: "POST",
      body: JSON.stringify({
        route_id: route.id,
        title: route.title,
        outline: route.outline ?? [],
      }),
    });
  },

  matchReviewers(sessionId: string) {
    return request(`/api/v1/sessions/${sessionId}/reviewers/match`, {
      method: "POST",
    });
  },

  generateDraft(sessionId: string) {
    return request<{ draft: Draft }>(
      `/api/v1/sessions/${sessionId}/draft/generate`,
      { method: "POST", timeoutMs: 120_000 }
    );
  },

  getDraft(sessionId: string) {
    return request<Draft & { session_id: string }>(
      `/api/v1/sessions/${sessionId}/draft`
    );
  },

  patchDraft(sessionId: string, patch: Partial<Draft>) {
    return request<{ draft: Draft }>(`/api/v1/sessions/${sessionId}/draft`, {
      method: "PATCH",
      body: JSON.stringify(patch),
    });
  },

  regeneratePart(sessionId: string, part: "title" | "hooks" | "body" | "tags") {
    return request<{ draft: Draft }>(
      `/api/v1/sessions/${sessionId}/draft/regenerate`,
      {
        method: "POST",
        body: JSON.stringify({ part }),
      }
    );
  },

  deAiPolish(sessionId: string) {
    return request<{ draft: Draft }>(
      `/api/v1/sessions/${sessionId}/draft/de-ai-polish`,
      { method: "POST" }
    );
  },

  finalizeText(sessionId: string) {
    return request(`/api/v1/sessions/${sessionId}/review/finalize-text`, {
      method: "POST",
    });
  },

  generateImages(sessionId: string) {
    return request<{ images: ImageAsset[]; count: number }>(
      `/api/v1/sessions/${sessionId}/images/generate`,
      { method: "POST", timeoutMs: 180_000 }
    );
  },

  listImages(sessionId: string) {
    return request<{ images: ImageAsset[] }>(
      `/api/v1/sessions/${sessionId}/images`
    );
  },

  regenerateImage(sessionId: string, imageId: string, reason = "") {
    return request<{ image: ImageAsset }>(
      `/api/v1/sessions/${sessionId}/images/regenerate`,
      {
        method: "POST",
        body: JSON.stringify({ image_id: imageId, reason }),
      }
    );
  },

  finalize(sessionId: string) {
    return request(`/api/v1/sessions/${sessionId}/review/finalize`, {
      method: "POST",
    });
  },

  listSessions() {
    return request<{ sessions: SessionSummary[]; count: number }>(
      "/api/v1/sessions"
    );
  },

  getSession(sessionId: string) {
    return request<{
      id: string;
      movie_title: string;
      status: string;
      selected_angle?: { title?: string; description?: string };
      selected_route?: { title?: string; outline?: string[] };
      text_review_round?: number;
      image_review_round?: number;
      is_favorite: boolean;
      is_published: boolean;
      updated_at: string;
      movie?: { title?: string; year?: number; genres?: string[] };
    }>(`/api/v1/sessions/${sessionId}`);
  },

  getTimeline(sessionId: string) {
    return request<{ timeline: Array<{ type: string; timestamp: string }> }>(
      `/api/v1/sessions/${sessionId}/timeline`
    );
  },

  listReviewMessages(sessionId: string, phase: "text" | "image" | "all" = "text") {
    return request<{ session_id: string; messages: ReviewMessageRecord[] }>(
      `/api/v1/sessions/${sessionId}/review/messages?phase=${phase}`
    );
  },

  postUserMessage(sessionId: string, content: string, phase: "text" | "image" = "text") {
    return request<ReviewMessageRecord>(
      `/api/v1/sessions/${sessionId}/review/messages?phase=${phase}`,
      {
        method: "POST",
        body: JSON.stringify({ content }),
      }
    );
  },

  deleteSession(sessionId: string) {
    return request<{ id: string; deleted: boolean }>(
      `/api/v1/sessions/${sessionId}`,
      { method: "DELETE" }
    );
  },
};
