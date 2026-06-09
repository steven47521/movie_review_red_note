"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import { api } from "@/lib/api";
import { resolveMbti } from "@/lib/chat-avatar";
import { toStreamMessage, sortReviewMessages } from "@/lib/review-message";
import {
  SSE_EVENTS,
  type ReviewPhase,
  type ReviewRoundGroup,
  type ReviewStreamMessage,
  type SseEventName,
} from "@/lib/review-types";

const API_BASE = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
const IMAGE_CONTINUE_TIMEOUT_MS = 180_000;

function buildRoundsFromMessages(messages: ReviewStreamMessage[]): ReviewRoundGroup[] {
  const ordered = sortReviewMessages(messages);
  const groups = new Map<number, ReviewStreamMessage[]>();
  for (const message of ordered) {
    const bucket = groups.get(message.round) ?? [];
    bucket.push(message);
    groups.set(message.round, bucket);
  }
  return [...groups.entries()]
    .sort(([left], [right]) => left - right)
    .map(([round, roundMessages]) => ({
      round,
      messages: roundMessages,
      collapsed: false,
    }));
}

function upsertMessage(
  groups: ReviewRoundGroup[],
  message: ReviewStreamMessage
): ReviewRoundGroup[] {
  const next = groups.map((group) => ({ ...group, messages: [...group.messages] }));
  const index = next.findIndex((group) => group.round === message.round);

  if (index === -1) {
    next.push({ round: message.round, messages: [message], collapsed: false });
    return next.sort((a, b) => a.round - b.round);
  }

  const existing = next[index].messages.find((item) => item.id === message.id);
  if (!existing) {
    next[index].messages.push(message);
  }
  return next;
}

function finalizeStreamMessage(message: ReviewStreamMessage): ReviewStreamMessage {
  if (!message.mbti) {
    message.mbti = resolveMbti(message);
  }
  return message;
}

function parseMessage(event: SseEventName, payload: Record<string, unknown>): ReviewStreamMessage | null {
  if (event === "reviewer_message") {
    return finalizeStreamMessage({
      id: String(payload.id ?? `msg-${Date.now()}`),
      role: "reviewer",
      content: String(payload.content ?? ""),
      round: Number(payload.round ?? 1),
      nickname: payload.nickname ? String(payload.nickname) : "审稿人",
      avatar_url: payload.avatar_url ? String(payload.avatar_url) : undefined,
      mbti: payload.mbti ? String(payload.mbti) : undefined,
      persona_id: payload.persona_id ? String(payload.persona_id) : undefined,
      attachment: (payload.attachment as Record<string, unknown>) ?? undefined,
    });
  }

  if (event === "moderator_summary") {
    return {
      id: String(payload.id ?? `msg-${Date.now()}`),
      role: "moderator",
      content: String(payload.content ?? ""),
      round: Number(payload.round ?? 1),
      nickname: "主持人",
    };
  }

  if (event === "writer_revision" || event === "image_updated") {
    return {
      id: String(payload.id ?? `msg-${Date.now()}`),
      role: "writer",
      content: String(payload.content ?? ""),
      round: Number(payload.round ?? 1),
      nickname: "Writer",
      attachment: (payload.attachment as Record<string, unknown>) ?? undefined,
    };
  }

  return null;
}

export function useReviewStream(
  sessionId: string,
  phase: ReviewPhase,
  options?: { mergePhases?: boolean }
) {
  const mergePhases = options?.mergePhases ?? false;
  const sourceRef = useRef<EventSource | null>(null);
  const streamCompletedRef = useRef(false);
  const [rounds, setRounds] = useState<ReviewRoundGroup[]>([]);
  const [isStreaming, setIsStreaming] = useState(false);
  const [isLoadingHistory, setIsLoadingHistory] = useState(false);
  const [historyLoaded, setHistoryLoaded] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [currentRound, setCurrentRound] = useState(0);

  const closeStream = useCallback(() => {
    sourceRef.current?.close();
    sourceRef.current = null;
    setIsStreaming(false);
  }, []);

  const loadHistory = useCallback(async () => {
    if (!sessionId) {
      setRounds([]);
      setCurrentRound(0);
      setHistoryLoaded(false);
      return 0;
    }

    setIsLoadingHistory(true);
    setError(null);
    try {
      const response = await api.listReviewMessages(
        sessionId,
        mergePhases ? "all" : phase
      );
      const messages = sortReviewMessages(response.messages.map(toStreamMessage));
      setRounds(buildRoundsFromMessages(messages));
      setCurrentRound(messages.length ? Math.max(...messages.map((item) => item.round)) : 0);
      return messages.length;
    } catch (err) {
      setRounds([]);
      setCurrentRound(0);
      setError(err instanceof Error ? err.message : "加载审稿记录失败");
      return 0;
    } finally {
      setIsLoadingHistory(false);
      setHistoryLoaded(true);
    }
  }, [mergePhases, phase, sessionId]);

  useEffect(() => {
    closeStream();
    if (!sessionId) {
      setRounds([]);
      setCurrentRound(0);
      setHistoryLoaded(false);
      return;
    }
    void loadHistory();
  }, [closeStream, loadHistory, sessionId]);

  const startStream = useCallback(() => {
    if (!sessionId) {
      setError("缺少 session id");
      return;
    }

    closeStream();
    setError(null);
    setIsStreaming(true);
    streamCompletedRef.current = false;

    const url = `${API_BASE}/api/v1/sessions/${sessionId}/review/stream?phase=${phase}`;
    const source = new EventSource(url);
    sourceRef.current = source;

    const handlePayload = (eventName: SseEventName, raw: string) => {
      let payload: Record<string, unknown> = {};
      try {
        payload = JSON.parse(raw) as Record<string, unknown>;
      } catch {
        setError("SSE 数据解析失败");
        closeStream();
        return;
      }

      if (eventName === "error") {
        setError(String(payload.message ?? "审稿流错误"));
        closeStream();
        return;
      }

      if (eventName === "round_complete") {
        streamCompletedRef.current = true;
        setCurrentRound(Number(payload.round ?? 0));
        closeStream();
        return;
      }

      const message = parseMessage(eventName, payload);
      if (message) {
        setRounds((prev) => upsertMessage(prev, message));
      }
    };

    for (const eventName of SSE_EVENTS) {
      source.addEventListener(eventName, (event) => {
        const messageEvent = event as MessageEvent<string>;
        handlePayload(eventName, messageEvent.data);
      });
    }

    source.onerror = () => {
      if (streamCompletedRef.current || sourceRef.current !== source) {
        return;
      }
      setError("SSE 连接中断，请检查后端是否在运行并重试。");
      closeStream();
    };
  }, [closeStream, phase, sessionId]);

  const appendMessage = useCallback((message: ReviewStreamMessage) => {
    setRounds((prev) => upsertMessage(prev, message));
    setCurrentRound((prev) => Math.max(prev, message.round));
  }, []);

  const toggleRound = useCallback((round: number) => {
    setRounds((prev) =>
      prev.map((group) =>
        group.round === round ? { ...group, collapsed: !group.collapsed } : group
      )
    );
  }, []);

  const continueImageReview = useCallback(async () => {
    if (!sessionId) {
      setError("缺少 session id");
      return;
    }

    setError(null);
    setIsStreaming(true);
    const controller = new AbortController();
    const timer = window.setTimeout(() => controller.abort(), IMAGE_CONTINUE_TIMEOUT_MS);

    try {
      const response = await fetch(
        `${API_BASE}/api/v1/sessions/${sessionId}/review/continue?phase=image`,
        { method: "POST", signal: controller.signal }
      );
      if (!response.ok) {
        const body = (await response.json().catch(() => ({}))) as { detail?: string };
        throw new Error(body.detail ?? "继续配图评审失败");
      }
      await loadHistory();
    } catch (err) {
      if (err instanceof DOMException && err.name === "AbortError") {
        setError("配图评审超时，请稍后重试。");
      } else {
        setError(err instanceof Error ? err.message : "继续配图评审失败");
      }
    } finally {
      window.clearTimeout(timer);
      setIsStreaming(false);
    }
  }, [loadHistory, sessionId]);

  const continueReview = useCallback(async () => {
    if (phase === "image") {
      await continueImageReview();
      return;
    }
    startStream();
  }, [continueImageReview, phase, startStream]);

  const finalizeReview = useCallback(async () => {
    const endpoint =
      phase === "text"
        ? `${API_BASE}/api/v1/sessions/${sessionId}/review/finalize-text`
        : `${API_BASE}/api/v1/sessions/${sessionId}/review/finalize`;
    const response = await fetch(endpoint, { method: "POST" });
    if (!response.ok) {
      const body = (await response.json().catch(() => ({}))) as { detail?: string };
      throw new Error(body.detail ?? "定稿失败");
    }
    closeStream();
  }, [closeStream, phase, sessionId]);

  useEffect(() => () => closeStream(), [closeStream]);

  return {
    rounds,
    isStreaming,
    isLoadingHistory,
    historyLoaded,
    error,
    currentRound,
    loadHistory,
    appendMessage,
    startStream,
    closeStream,
    toggleRound,
    continueReview,
    finalizeReview,
  };
}
