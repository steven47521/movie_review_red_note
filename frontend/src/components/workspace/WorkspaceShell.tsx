"use client";

import { FormEvent, useCallback, useEffect, useMemo, useRef, useState } from "react";
import { useRouter, useSearchParams } from "next/navigation";

import CreationWizard from "@/components/creation-wizard/CreationWizard";
import ReviewFeedbackBody from "@/components/review-room/ReviewFeedbackBody";
import MessageAttachments from "@/components/workspace/MessageAttachments";
import MessageAvatar from "@/components/workspace/MessageAvatar";
import { useReviewStream } from "@/hooks/useReviewStream";
import { api, resolveAssetUrl, type Draft, type ImageAsset, type SessionSummary } from "@/lib/api";
import { labelForImageType } from "@/lib/message-attachments";
import { sortReviewMessages, toStreamMessage } from "@/lib/review-message";
import type { ReviewStreamMessage } from "@/lib/review-types";
import {
  STAGE_ORDER,
  STATUS_LABELS,
  draftExcerpt,
  formatUpdatedAt,
  primaryActionForStatus,
  sessionMatchesFilter,
  sessionOverview,
  stageIndexForStatus,
  statusPillClass,
  type SessionFilter,
} from "@/lib/session-ui";

type SideTab = "review" | "progress" | "versions" | "assets";

type TimelineEvent = {
  type: string;
  timestamp: string;
  data?: Record<string, unknown>;
};

function roleClass(role: string): string {
  if (role === "user") return "is-user";
  if (role === "writer") return "is-writer";
  if (role === "reviewer") return "is-reviewer";
  if (role === "moderator" || role === "system") return "is-system";
  return "";
}

function badgeForMessage(message: ReviewStreamMessage): string {
  if (message.role === "reviewer") return message.nickname?.slice(0, 4) ?? "审稿";
  if (message.role === "writer") return "改稿";
  if (message.role === "moderator") return "汇总";
  if (message.role === "user") return "指令";
  return "系统";
}

export default function WorkspaceShell() {
  const router = useRouter();
  const searchParams = useSearchParams();

  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);
  const [filter, setFilter] = useState<SessionFilter>("all");
  const [activeTab, setActiveTab] = useState<SideTab>("review");
  const [createMode, setCreateMode] = useState(false);
  const [leftOpen, setLeftOpen] = useState(false);
  const [rightOpen, setRightOpen] = useState(false);
  const [toast, setToast] = useState<string | null>(null);
  const [prompt, setPrompt] = useState("");
  const [draft, setDraft] = useState<Draft | null>(null);
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [timeline, setTimeline] = useState<TimelineEvent[]>([]);
  const [detailStatus, setDetailStatus] = useState<string>("");
  const [textRound, setTextRound] = useState(0);
  const [imageRound, setImageRound] = useState(0);
  const [loadingList, setLoadingList] = useState(true);
  const [actionError, setActionError] = useState<string | null>(null);
  const [draftPreviewOpen, setDraftPreviewOpen] = useState(false);
  const [imagesBusy, setImagesBusy] = useState(false);

  const activeSession = useMemo(
    () => sessions.find((item) => item.id === activeSessionId) ?? null,
    [activeSessionId, sessions]
  );

  const reviewPhase = useMemo((): "text" | "image" => {
    if (activeSession?.status === "image_reviewing") return "image";
    if (activeSession?.status === "text_reviewing") return "text";
    return images.length > 0 ? "image" : "text";
  }, [activeSession?.status, images.length]);

  const {
    rounds,
    isStreaming,
    isLoadingHistory,
    historyLoaded,
    error: streamError,
    continueReview,
    startStream,
    appendMessage,
    loadHistory,
  } = useReviewStream(activeSessionId ?? "", reviewPhase, { mergePhases: true });

  const flatMessages = useMemo(
    () => sortReviewMessages(rounds.flatMap((group) => group.messages)),
    [rounds]
  );

  const needsIdeation = useMemo(() => {
    if (!activeSession || createMode || draft) return false;
    return (
      activeSession.status === "researching" ||
      activeSession.status === "angles_ready" ||
      activeSession.status === "route_ready"
    );
  }, [activeSession, createMode, draft]);

  const reviewers = useMemo(() => {
    const seen = new Map<
      string,
      { name: string; profile: string; focus: string; message: ReviewStreamMessage }
    >();
    for (const message of flatMessages) {
      if (message.role !== "reviewer") continue;
      const key = message.persona_id ?? message.nickname ?? message.id;
      if (seen.has(key)) continue;
      const mbti = message.mbti ?? message.attachment?.mbti;
      seen.set(key, {
        name: message.nickname ?? "审稿人",
        profile: typeof mbti === "string" ? `${mbti.toUpperCase()} 人格` : "审稿人格",
        focus: message.content.slice(0, 80),
        message,
      });
    }
    return [...seen.values()];
  }, [flatMessages]);

  const showToast = useCallback((message: string) => {
    setToast(message);
    window.setTimeout(() => setToast(null), 2200);
  }, []);

  const refreshSessions = useCallback(async () => {
    setLoadingList(true);
    try {
      const resp = await api.listSessions();
      setSessions(resp.sessions);
      return resp.sessions;
    } catch {
      setSessions([]);
      return [];
    } finally {
      setLoadingList(false);
    }
  }, []);

  const loadSessionData = useCallback(async (sessionId: string) => {
    try {
      const detail = await api.getSession(sessionId);
      setDetailStatus(detail.status);
      setTextRound(detail.text_review_round ?? 0);
      setImageRound(detail.image_review_round ?? 0);

      try {
        const latest = await api.getDraft(sessionId);
        setDraft({
          version: latest.version,
          title: latest.title,
          hooks: latest.hooks,
          body: latest.body,
          tags: latest.tags,
          review_round: latest.review_round,
        });
      } catch {
        setDraft(null);
      }

      try {
        const imageResp = await api.listImages(sessionId);
        setImages(imageResp.images);
      } catch {
        setImages([]);
      }

      try {
        const timelineResp = await api.getTimeline(sessionId);
        setTimeline(timelineResp.timeline as TimelineEvent[]);
      } catch {
        setTimeline([]);
      }
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "加载会话失败");
    }
  }, []);

  useEffect(() => {
    void refreshSessions().then((list) => {
      const requested = searchParams.get("session");
      const isNew = searchParams.get("new") === "1";
      if (isNew) {
        setCreateMode(true);
        return;
      }
      if (requested) {
        setActiveSessionId(requested);
        setCreateMode(false);
        return;
      }
      if (list[0]) {
        setActiveSessionId(list[0].id);
      }
    });
  }, [refreshSessions, searchParams]);

  useEffect(() => {
    if (!activeSessionId || createMode) return;
    void loadSessionData(activeSessionId);
  }, [activeSessionId, createMode, loadSessionData]);

  useEffect(() => {
    setDraftPreviewOpen(false);
  }, [activeSessionId]);

  const autoReviewStartedRef = useRef(false);
  useEffect(() => {
    autoReviewStartedRef.current = false;
  }, [activeSessionId]);

  useEffect(() => {
    if (!activeSessionId || createMode || !activeSession) return;
    if (!historyLoaded || isLoadingHistory || isStreaming) return;
    if (flatMessages.length > 0) return;
    if (autoReviewStartedRef.current) return;
    if (activeSession.status !== "text_reviewing") return;

    autoReviewStartedRef.current = true;
    startStream();
  }, [
    activeSession,
    activeSessionId,
    createMode,
    flatMessages.length,
    historyLoaded,
    isLoadingHistory,
    isStreaming,
    startStream,
  ]);

  const prevStreamingRef = useRef(false);
  useEffect(() => {
    if (prevStreamingRef.current && !isStreaming && activeSessionId) {
      void loadSessionData(activeSessionId);
      void refreshSessions();
    }
    prevStreamingRef.current = isStreaming;
  }, [activeSessionId, isStreaming, loadSessionData, refreshSessions]);

  const filteredSessions = sessions.filter((session) =>
    sessionMatchesFilter(session, filter)
  );

  const stageIndex = stageIndexForStatus(
    activeSession?.status ?? detailStatus ?? "created"
  );

  const handleSelectSession = (sessionId: string) => {
    setActiveSessionId(sessionId);
    setCreateMode(false);
    setLeftOpen(false);
    router.replace(`/dashboard?session=${sessionId}`);
  };

  const handleDeleteSession = async (sessionId: string) => {
    const target = sessions.find((s) => s.id === sessionId);
    const label = target?.movie_title ?? "该会话";
    if (!window.confirm(`确定删除「${label}」？此操作不可恢复。`)) {
      return;
    }
    setActionError(null);
    try {
      await api.deleteSession(sessionId);
      const list = await refreshSessions();
      if (activeSessionId === sessionId) {
        const next = list[0]?.id ?? null;
        setActiveSessionId(next);
        setDraft(null);
        setImages([]);
        setTimeline([]);
        if (next) {
          router.replace(`/dashboard?session=${next}`);
        } else {
          setCreateMode(true);
          router.replace("/dashboard?new=1");
        }
      }
      showToast("会话已删除");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "删除失败");
    }
  };

  const handleNewSession = () => {
    setCreateMode(true);
    setActiveSessionId(null);
    setLeftOpen(false);
    router.replace("/dashboard?new=1");
  };

  const generateImagesForSession = useCallback(async (sessionId: string) => {
    setImagesBusy(true);
    try {
      await api.generateImages(sessionId);
      await loadHistory();
    } finally {
      setImagesBusy(false);
    }
  }, [loadHistory]);

  const handlePrimaryAction = async () => {
    if (!activeSessionId || !activeSession) {
      handleNewSession();
      return;
    }
    setActionError(null);
    try {
      if (activeSession.status === "text_reviewing") {
        if (isStreaming) return;
        await continueReview();
        setActiveTab("review");
        showToast("审稿团开始发言，请稍候…");
        return;
      }
      if (activeSession.status === "image_reviewing") {
        if (isStreaming) return;
        await continueReview();
        await loadSessionData(activeSessionId);
        await refreshSessions();
        setActiveTab("assets");
        showToast("已开始配图评审");
        return;
      }
      if (activeSession.status === "angles_ready" || activeSession.status === "route_ready") {
        setActiveTab("progress");
        showToast("请在主区域继续选题与定路线");
        return;
      }
      if (activeSession.status === "text_finalized" || activeSession.status === "image_generating") {
        await generateImagesForSession(activeSessionId);
        await loadSessionData(activeSessionId);
        await refreshSessions();
        setActiveTab("assets");
        showToast("配图已生成");
        return;
      }
      if (activeSession.status === "completed") {
        setActiveTab("assets");
        showToast("已打开产物归档");
        return;
      }
      handleNewSession();
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "操作失败");
    }
  };

  const saveUserMessage = async (content: string) => {
    if (!activeSessionId) return;
    const saved = await api.postUserMessage(activeSessionId, content, reviewPhase);
    appendMessage(toStreamMessage(saved));
  };

  const handleFinalizeText = async () => {
    if (!activeSessionId || !activeSession) return;
    if (activeSession.status !== "text_reviewing") return;
    setActionError(null);
    try {
      await saveUserMessage("文案满意，结束本轮评审，进入配图阶段。");
      await api.finalizeText(activeSessionId);
      await loadSessionData(activeSessionId);
      await refreshSessions();
      setActiveTab("assets");
      showToast("文案已定稿，可进入第 05 步生成配图");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "结束评审失败");
    }
  };

  const handleFinalizeCreation = async () => {
    if (!activeSessionId || !activeSession) return;
    if (activeSession.status !== "image_reviewing") return;
    setActionError(null);
    try {
      await saveUserMessage("配图满意，完成本次创作。");
      await api.finalize(activeSessionId);
      await loadSessionData(activeSessionId);
      await refreshSessions();
      setActiveTab("assets");
      showToast("创作已完成");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "完成创作失败");
    }
  };

  const handleComposerSubmit = async (event: FormEvent) => {
    event.preventDefault();
    const value = prompt.trim();
    if (!value || !activeSessionId) return;
    setPrompt("");
    setActionError(null);

    try {
      await saveUserMessage(value);
      if (value.includes("标题")) {
        await api.regeneratePart(activeSessionId, "title");
      } else if (value.includes("去 AI") || value.includes("AI 感")) {
        await api.deAiPolish(activeSessionId);
      } else if (
        value.includes("定稿") ||
        value.includes("满意") ||
        value.includes("结束评审")
      ) {
        await api.finalizeText(activeSessionId);
        setActiveTab("assets");
      } else if (value.includes("评审")) {
        await continueReview();
      } else if (value.includes("配图")) {
        if (activeSession?.status === "text_reviewing") {
          await api.finalizeText(activeSessionId);
        }
        await generateImagesForSession(activeSessionId);
        await loadSessionData(activeSessionId);
        await refreshSessions();
        setActiveTab("assets");
      } else {
        await api.patchDraft(activeSessionId, { body: value });
      }
      await loadSessionData(activeSessionId);
      await refreshSessions();
      showToast("指令已处理");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "指令失败");
    }
  };

  const handleQuickAction = async (action: "compress" | "title" | "review" | "images") => {
    if (!activeSessionId || isStreaming) return;
    setActionError(null);
    const quickLabels = {
      compress: "压缩开头的剧情复述，把重点拉回到人物关系与时代空间。",
      title: "重写标题，保留高级感，但更像小红书会点开的写法。",
      review: "继续评审这一版，重点听听三位评审对引子和结尾的意见。",
      images: "整理三张配图方向：封面、金句卡、氛围图。",
    } as const;
    try {
      await saveUserMessage(quickLabels[action]);
      if (action === "compress") {
        await api.regeneratePart(activeSessionId, "body");
      } else if (action === "title") {
        await api.regeneratePart(activeSessionId, "title");
      } else if (action === "review") {
        await continueReview();
      } else if (action === "images") {
        if (activeSession?.status === "text_reviewing") {
          await api.finalizeText(activeSessionId);
        }
        await generateImagesForSession(activeSessionId);
        setActiveTab("assets");
      }
      await loadSessionData(activeSessionId);
      await refreshSessions();
      showToast("操作已完成");
    } catch (err) {
      setActionError(err instanceof Error ? err.message : "快捷操作失败");
    }
  };

  const copyTitle = async () => {
    if (!draft?.title) return;
    try {
      await navigator.clipboard.writeText(draft.title);
      showToast("标题已复制");
    } catch {
      showToast("复制失败");
    }
  };

  const renderSidePanel = () => {
    if (!activeSession) {
      return (
        <section className="inspector-card">
          <h3>侧栏</h3>
          <p className="caption">选择会话或新建创作后，这里会显示评审团、进度与产物。</p>
        </section>
      );
    }

    if (activeTab === "progress") {
      return (
        <>
          <section className="inspector-card">
            <h3>当前进度</h3>
            <ul className="progress-list">
              {STAGE_ORDER.map((stage, index) => (
                <li key={stage.key} className="progress-row">
                  <div className="progress-title">
                    <span>{stage.label}</span>
                    <span
                      className={`status-pill ${
                        index < stageIndex
                          ? "is-success"
                          : index === stageIndex
                            ? statusPillClass(activeSession.status)
                            : "is-muted"
                      }`}
                    >
                      <span className="status-dot" />
                      {index < stageIndex ? "完成" : index === stageIndex ? "进行中" : "待开始"}
                    </span>
                  </div>
                  <p className="progress-copy">
                    {index === 3
                      ? `文案评审进行到第 ${textRound} 轮。`
                      : index === 4
                        ? `配图审稿轮次：${imageRound}。`
                        : stage.hint}
                  </p>
                </li>
              ))}
            </ul>
          </section>
          <section className="inspector-card">
            <h3>时间线</h3>
            <ul className="audit-list">
              {timeline.slice(-6).reverse().map((item, index) => (
                <li key={`${item.type}-${index}`} className="audit-row">
                  <div className="audit-head">
                    <span>{item.type}</span>
                    <span className="num">{formatUpdatedAt(item.timestamp)}</span>
                  </div>
                </li>
              ))}
            </ul>
          </section>
        </>
      );
    }

    if (activeTab === "versions") {
      return (
        <>
          <section className="inspector-card">
            <h3>当前稿件</h3>
            <p className="caption">完整版本历史会随审稿轮次写入时间线。</p>
          </section>
          {draft ? (
            <div className="version-list">
              <article className="version-row" aria-current="true">
                <div className="version-row-top">
                  <div>
                    <div className="version-title">
                      v{draft.version} · 当前稿
                    </div>
                    <div className="small-copy">{draft.title}</div>
                  </div>
                  <span className="role-chip">{draft.tags[0] ?? "稿件"}</span>
                </div>
                <p className="version-excerpt">{draftExcerpt(draft)}</p>
              </article>
            </div>
          ) : (
            <p className="caption">暂无稿件版本。</p>
          )}
        </>
      );
    }

    if (activeTab === "assets") {
      return (
        <>
          <section className="inspector-card">
            <h3>产物与配图</h3>
            <p className="caption">封面、金句卡与氛围图会固定展示在这里。</p>
          </section>
          <div className="asset-grid">
            {(images.length ? images : [{ id: "p1", type: "cover", url: "" }]).map(
              (asset, index) => (
                <article key={asset.id ?? index} className="reviewer-row">
                  <div className="asset-head">
                    <div className="reviewer-id">
                      <strong>{labelForImageType(asset.type)}</strong>
                      <span>{asset.url ? "已生成" : "待生成"}</span>
                    </div>
                  </div>
                  {asset.url ? (
                    <img
                      src={resolveAssetUrl(asset.url)}
                      alt={asset.type}
                      className="artifact-shot"
                    />
                  ) : (
                    <div className="artifact-shot">等待文案定稿后生成配图</div>
                  )}
                </article>
              )
            )}
          </div>
        </>
      );
    }

    return (
      <>
        <section className="inspector-card">
          <h3>当前评审团</h3>
          <p className="caption">按电影气质匹配的审稿人格，提供多元意见。</p>
        </section>
        <div className="reviewer-grid">
          {reviewers.length ? (
            reviewers.map((reviewer) => (
              <article key={reviewer.message.id} className="reviewer-row">
                <div className="reviewer-top">
                  <MessageAvatar message={reviewer.message} />
                  <div className="reviewer-id">
                    <strong>{reviewer.name}</strong>
                    <span>{reviewer.profile}</span>
                  </div>
                  <span className="role-chip">活跃</span>
                </div>
                <p className="reviewer-note">{reviewer.focus}</p>
              </article>
            ))
          ) : (
            <p className="caption">进入审稿阶段后，评审团意见会显示在这里。</p>
          )}
        </div>
      </>
    );
  };

  return (
    <div
      className="rp-app app-shell"
      data-left-open={leftOpen ? "true" : "false"}
      data-right-open={rightOpen ? "true" : "false"}
      data-testid="workspace-shell"
    >
      <header className="topnav">
        <div className="topnav-inner">
          <div className="brand-lockup">
            <strong className="brand-title">片语 RedNote</strong>
            <span className="brand-meta">经典电影小红书稿件创作台</span>
          </div>
          <div className="workspace-summary" aria-label="工作台摘要">
            <span className="meta-pill">
              <span className="status-dot" />
              个人创作空间
            </span>
            <span className="meta-pill">
              <span className="num">{sessions.length}</span> 个会话
            </span>
            <span className="meta-pill">自动保存已开启</span>
          </div>
          <div className="topnav-actions">
            <button
              className="btn btn-secondary btn-small mobile-toggle is-left"
              type="button"
              onClick={() => {
                setLeftOpen((open) => !open);
                setRightOpen(false);
              }}
            >
              会话
            </button>
            <button
              className="btn btn-secondary btn-small mobile-toggle is-right"
              type="button"
              onClick={() => {
                setRightOpen((open) => !open);
                setLeftOpen(false);
              }}
            >
              侧栏
            </button>
            <button className="btn btn-secondary" type="button" onClick={handleNewSession}>
              新建会话
            </button>
            {activeSession?.status === "text_reviewing" ? (
              <button
                className="btn btn-secondary"
                type="button"
                disabled={isStreaming}
                onClick={() => void handleFinalizeText()}
              >
                结束评审
              </button>
            ) : null}
            {activeSession?.status === "image_reviewing" ? (
              <button
                className="btn btn-secondary"
                type="button"
                disabled={isStreaming}
                onClick={() => void handleFinalizeCreation()}
              >
                完成创作
              </button>
            ) : null}
            <button
              className="btn btn-primary"
              type="button"
              disabled={isStreaming}
              onClick={() => void handlePrimaryAction()}
            >
              {isStreaming
                ? "评审进行中…"
                : activeSession
                  ? primaryActionForStatus(activeSession.status)
                  : "开始创作"}
            </button>
          </div>
        </div>
      </header>

      <main className="workspace">
        <section className="workspace-grid">
          <aside className="panel left-rail" aria-label="会话列表">
            <div className="panel-head">
              <div className="sidebar-headline">
                <div>
                  <h2>工作台</h2>
                  <p className="sidebar-note">左侧聚焦项目，右侧始终保留评审与产物。</p>
                </div>
              </div>
              <div className="filter-row">
                {(
                  [
                    ["all", "全部"],
                    ["text", "文案中"],
                    ["image", "配图中"],
                    ["done", "已完成"],
                  ] as const
                ).map(([key, label]) => (
                  <button
                    key={key}
                    className="filter-chip"
                    type="button"
                    aria-pressed={filter === key}
                    onClick={() => setFilter(key)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="rail-stack">
              <div className="thread-list">
                {loadingList ? (
                  <p className="sidebar-note">加载会话中…</p>
                ) : filteredSessions.length ? (
                  filteredSessions.map((session) => (
                    <div
                      key={session.id}
                      className={`thread-card ${
                        session.id === activeSessionId && !createMode ? "is-active" : ""
                      }`}

                    >
                      <button
                        type="button"
                        style={{
                          width: "100%",
                          border: 0,
                          background: "transparent",
                          padding: 0,
                          textAlign: "left",
                          cursor: "pointer",
                          color: "inherit",
                        }}
                        onClick={() => handleSelectSession(session.id)}
                      >
                        <div className="thread-card-top">
                          <div>
                            <div className="thread-card-title">{session.movie_title}</div>
                            <div className="thread-card-subtitle">
                              {formatUpdatedAt(session.updated_at)}
                            </div>
                          </div>
                          <span
                            className={`status-pill ${statusPillClass(session.status)}`}
                          >
                            <span className="status-dot" />
                            {STATUS_LABELS[session.status] ?? session.status}
                          </span>
                        </div>
                        <p className="thread-card-snippet">{sessionOverview(session)}</p>
                      </button>
                      <div
                        className="thread-card-bottom"
                        style={{ justifyContent: "flex-end", marginTop: "var(--space-2)" }}
                      >
                        <button
                          type="button"
                          className="btn btn-ghost btn-small"
                          aria-label={`删除 ${session.movie_title}`}
                          onClick={(event) => {
                            event.stopPropagation();
                            void handleDeleteSession(session.id);
                          }}
                        >
                          删除
                        </button>
                      </div>
                    </div>
                  ))
                ) : (
                  <p className="sidebar-note">还没有会话，点击「新建会话」开始。</p>
                )}
              </div>
              <div className="sidebar-library">
                <div className="library-row">
                  <span>最近收藏</span>
                  <strong>随时查看</strong>
                </div>
                <div className="library-row">
                  <span>完整时间线</span>
                  <strong>可回放</strong>
                </div>
                <div className="library-row">
                  <span>发布归档</span>
                  <strong>已开启</strong>
                </div>
              </div>
            </div>
          </aside>

          <section className="panel center-stage" aria-label="主对话区">
            {createMode || needsIdeation ? (
              <div className="chat-scroll" style={{ padding: "var(--space-5)" }}>
                <CreationWizard
                  resumeSessionId={needsIdeation && activeSessionId ? activeSessionId : undefined}
                  onSessionCreated={(id) => {
                    setActiveSessionId(id);
                    void refreshSessions();
                  }}
                  onProgress={() => {
                    if (activeSessionId) void loadSessionData(activeSessionId);
                    void refreshSessions();
                  }}
                />
              </div>
            ) : (
              <>
                <div className="center-stage-meta">
                  <div className="stage-head stage-head-compact">
                    <div className="stage-title-row">
                      <div className="stage-headline">
                        <div className="stage-tags">
                          {activeSession ? (
                            <>
                              <span
                                className={`status-pill ${statusPillClass(activeSession.status)}`}
                              >
                                <span className="status-dot" />
                                {STATUS_LABELS[activeSession.status] ?? activeSession.status}
                              </span>
                              <span className="role-chip">
                                文案轮次 <span className="num">{textRound}</span>/5
                              </span>
                            </>
                          ) : (
                            <span className="role-chip">选择或新建会话</span>
                          )}
                        </div>
                        <h1>{activeSession?.movie_title ?? "创作工作台"}</h1>
                        {!draft ? (
                          <p className="stage-summary">
                            从片名调研到多元评审与配图，全流程在这一个界面完成。
                          </p>
                        ) : null}
                      </div>
                      <div className="stage-head-actions">
                        {draft ? (
                          <button
                            className="btn btn-secondary btn-small"
                            type="button"
                            aria-expanded={draftPreviewOpen}
                            onClick={() => setDraftPreviewOpen((open) => !open)}
                          >
                            {draftPreviewOpen ? "收起稿件" : "展开稿件"}
                          </button>
                        ) : null}
                        <button
                          className="btn btn-secondary btn-small"
                          type="button"
                          onClick={() => setActiveTab("versions")}
                        >
                          历史版本
                        </button>
                      </div>
                    </div>
                    <div className="stage-progress stage-progress-compact">
                      {STAGE_ORDER.map((stage, index) => (
                        <div
                          key={stage.key}
                          className={`stage-step ${
                            index < stageIndex
                              ? "is-done"
                              : index === stageIndex
                                ? "is-current"
                                : ""
                          }`}
                          title={stage.hint}
                        >
                          <span className="stage-step-index">
                            {String(index + 1).padStart(2, "0")}
                          </span>
                          <strong>{stage.label}</strong>
                        </div>
                      ))}
                    </div>
                  </div>

                  {draft && draftPreviewOpen ? (
                    <div className="draft-snapshot">
                      <div className="snapshot-top">
                        <div>
                          <div className="small-copy">当前展示</div>
                          <strong className="snapshot-title">{draft.title}</strong>
                        </div>
                        <div className="tag-row">
                          <span className="role-chip">v{draft.version}</span>
                          <button
                            className="btn btn-secondary btn-small"
                            type="button"
                            onClick={() => void copyTitle()}
                          >
                            复制标题
                          </button>
                        </div>
                      </div>
                      <div className="snapshot-body">
                        <div className="snapshot-card">
                          <div className="small-copy">当前引子</div>
                          <ul className="hook-list">
                            {draft.hooks.map((hook) => (
                              <li key={hook}>{hook}</li>
                            ))}
                          </ul>
                        </div>
                        <div className="snapshot-card">
                          <div className="small-copy">正文摘要</div>
                          <p className="draft-excerpt">{draftExcerpt(draft)}</p>
                          <div className="tag-row">
                            {draft.tags.map((tag) => (
                              <span key={tag} className="role-chip">
                                {tag}
                              </span>
                            ))}
                          </div>
                        </div>
                      </div>
                    </div>
                  ) : null}
                </div>

                <div className="chat-scroll" aria-live="polite" data-testid="chat-stream">
                  {isStreaming ? (
                    <p className="sidebar-note" style={{ marginBottom: "var(--space-3)" }}>
                      审稿团正在发言，请稍候（约 1–3 分钟）。发言会逐条出现在下方。
                    </p>
                  ) : null}
                  {flatMessages.length ? (
                    flatMessages.map((message) => (
                      <article
                        key={message.id}
                        className={`message ${message.role === "user" ? "is-user" : ""}`}
                      >
                        <MessageAvatar message={message} />
                        <div className={`message-card ${roleClass(message.role)}`}>
                          <div className="message-head">
                            <div className="message-author">
                              <span>{message.nickname ?? message.role}</span>
                              <span className="role-chip">{badgeForMessage(message)}</span>
                            </div>
                            {message.role === "user" ? null : (
                              <span className="small-copy num">第 {message.round} 轮</span>
                            )}
                          </div>
                          <ReviewFeedbackBody
                            message={message}
                            contentClassName="message-copy"
                          />
                          <MessageAttachments
                            attachment={message.attachment}
                            fallbackImages={images}
                          />
                        </div>
                      </article>
                    ))
                  ) : (
                    <p className="sidebar-note">
                      {activeSession
                        ? isLoadingHistory
                          ? "正在加载审稿记录…"
                          : "暂无审稿记录，点击顶部「继续评审」开始。"
                        : "请选择左侧会话，或新建创作。"}
                    </p>
                  )}
                  {streamError ? (
                    <p className="small-copy" style={{ color: "var(--danger)" }}>
                      {streamError}
                    </p>
                  ) : null}
                  {actionError ? <p className="small-copy">{actionError}</p> : null}
                </div>

                <form className="composer" onSubmit={(event) => void handleComposerSubmit(event)}>
                  <div className="quick-row">
                    <button
                      className="quick-action"
                      type="button"
                      disabled={!activeSessionId || isStreaming}
                      onClick={() => void handleQuickAction("compress")}
                    >
                      压缩剧情导入
                    </button>
                    <button
                      className="quick-action"
                      type="button"
                      disabled={!activeSessionId || isStreaming}
                      onClick={() => void handleQuickAction("title")}
                    >
                      重写标题
                    </button>
                    <button
                      className="quick-action"
                      type="button"
                      disabled={!activeSessionId || isStreaming}
                      onClick={() => void handleQuickAction("review")}
                    >
                      进入下一轮评审
                    </button>
                    <button
                      className="quick-action"
                      type="button"
                      disabled={!activeSessionId || isStreaming}
                      onClick={() => void handleQuickAction("images")}
                    >
                      生成配图方向
                    </button>
                  </div>
                  <div className="composer-box">
                    <label className="visually-hidden" htmlFor="promptInput">
                      输入你的改稿指令
                    </label>
                    <textarea
                      id="promptInput"
                      value={prompt}
                      onChange={(event) => setPrompt(event.target.value)}
                      placeholder="继续像聊天一样下指令，例如：把标题更收一点，但引子要更抓人。"
                    />
                    <div className="composer-actions">
                      <div className="composer-meta">
                        <span className="meta-pill">/调研</span>
                        <span className="meta-pill">/重写</span>
                        <span className="meta-pill">/去 AI 感</span>
                        <span className="meta-pill">/定稿</span>
                      </div>
                      <div style={{ display: "flex", gap: "var(--space-2)", flexWrap: "wrap" }}>
                        {activeSession?.status === "text_reviewing" ? (
                          <button
                            className="btn btn-secondary"
                            type="button"
                            disabled={isStreaming || !activeSessionId}
                            onClick={() => void handleFinalizeText()}
                          >
                            结束评审，进入配图
                          </button>
                        ) : null}
                        {activeSession?.status === "image_reviewing" ? (
                          <button
                            className="btn btn-secondary"
                            type="button"
                            disabled={isStreaming || !activeSessionId}
                            onClick={() => void handleFinalizeCreation()}
                          >
                            完成创作
                          </button>
                        ) : null}
                        <button
                          className="btn btn-primary"
                          type="submit"
                          disabled={isStreaming || !activeSessionId}
                        >
                          发送指令
                        </button>
                      </div>
                    </div>
                  </div>
                </form>
              </>
            )}
          </section>

          <aside className="panel right-rail" aria-label="进度与产物侧栏">
            <div className="tabs-bar">
              <h2>侧栏</h2>
              <div className="tabs-nav">
                {(
                  [
                    ["review", "评审团"],
                    ["progress", "进度"],
                    ["versions", "版本"],
                    ["assets", "产物"],
                  ] as const
                ).map(([key, label]) => (
                  <button
                    key={key}
                    className="tab-btn"
                    type="button"
                    aria-selected={activeTab === key}
                    onClick={() => setActiveTab(key)}
                  >
                    {label}
                  </button>
                ))}
              </div>
            </div>
            <div className="tabs-content">{renderSidePanel()}</div>
          </aside>
        </section>
      </main>

      <div
        className="scrim"
        onClick={() => {
          setLeftOpen(false);
          setRightOpen(false);
        }}
      />
      <div className={`toast ${toast ? "is-visible" : ""}`} role="status" aria-live="polite">
        {toast}
      </div>
    </div>
  );
}
