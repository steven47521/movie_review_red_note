"use client";

import { useEffect, useRef, useState } from "react";

import ReviewerBubble from "@/components/review-room/ReviewerBubble";
import { useReviewStream } from "@/hooks/useReviewStream";
import type { ReviewPhase } from "@/lib/review-types";

type ChatPanelProps = {
  sessionId: string;
  phase?: ReviewPhase;
  autoStart?: boolean;
  imagesRefreshKey?: number;
  fallbackImages?: import("@/lib/api").ImageAsset[];
};

export default function ChatPanel({
  sessionId,
  phase = "text",
  autoStart = true,
  imagesRefreshKey = 0,
  fallbackImages = [],
}: ChatPanelProps) {
  const {
    rounds,
    isStreaming,
    isLoadingHistory,
    historyLoaded,
    error,
    currentRound,
    startStream,
    toggleRound,
    continueReview,
    finalizeReview,
    loadHistory,
  } = useReviewStream(sessionId, phase, { mergePhases: true });

  const [actionError, setActionError] = useState<string | null>(null);
  const autoStartedRef = useRef(false);

  useEffect(() => {
    autoStartedRef.current = false;
  }, [sessionId, phase]);

  useEffect(() => {
    if (!imagesRefreshKey) return;
    void loadHistory();
  }, [imagesRefreshKey, loadHistory]);

  useEffect(() => {
    if (!autoStart || !sessionId || !historyLoaded || autoStartedRef.current) {
      return;
    }
    if (rounds.length === 0 && !isStreaming && !isLoadingHistory) {
      autoStartedRef.current = true;
      startStream();
    }
  }, [
    autoStart,
    historyLoaded,
    isLoadingHistory,
    isStreaming,
    rounds.length,
    sessionId,
    startStream,
  ]);

  const onContinue = async () => {
    setActionError(null);
    try {
      await continueReview();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "继续优化失败");
    }
  };

  const onFinalize = async () => {
    setActionError(null);
    try {
      await finalizeReview();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "定稿失败");
    }
  };

  return (
    <section className="od-chat-panel" data-testid="chat-panel">
      <header className="od-chat-header">
        <div>
          <p className="od-eyebrow">Review Room</p>
          <h3 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-1)" }}>
            {phase === "text" ? "文案审稿" : "配图审稿"}
          </h3>
        </div>
        <span className="od-pill">
          {isStreaming ? "流式接收中" : currentRound ? `第 ${currentRound} 轮` : "待开始"}
        </span>
      </header>

      <div className="od-chat-body">
        {rounds.length === 0 ? (
          <p className="od-muted">等待审稿团发言…</p>
        ) : (
          rounds.map((group) => (
            <div key={group.round} className="od-round-group">
              <button
                type="button"
                className="od-round-title"
                onClick={() => toggleRound(group.round)}
                style={{
                  width: "100%",
                  border: "none",
                  background: "transparent",
                  cursor: "pointer",
                  textAlign: "left",
                }}
              >
                <span>第 {group.round} 轮</span>
                <span>{group.collapsed ? "展开" : "折叠"}</span>
              </button>

              {!group.collapsed
                ? group.messages.map((message) => (
                    <ReviewerBubble
                      key={message.id}
                      message={message}
                      fallbackImages={fallbackImages}
                    />
                  ))
                : null}
            </div>
          ))
        )}

        {error ? <p style={{ color: "var(--danger)", fontSize: "var(--text-sm)" }}>{error}</p> : null}
        {actionError ? (
          <p style={{ color: "var(--danger)", fontSize: "var(--text-sm)" }}>{actionError}</p>
        ) : null}
      </div>

      <footer className="od-chat-footer">
        <button
          type="button"
          className="od-btn od-btn-ghost"
          onClick={onContinue}
          disabled={isStreaming}
        >
          继续优化
        </button>
        <button
          type="button"
          className="od-btn od-btn-primary"
          onClick={onFinalize}
          disabled={isStreaming}
        >
          满意定稿
        </button>
      </footer>
    </section>
  );
}
