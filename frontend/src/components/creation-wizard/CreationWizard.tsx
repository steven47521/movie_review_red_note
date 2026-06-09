"use client";

import Link from "next/link";
import { useCallback, useEffect, useState } from "react";

import ChatPanel from "@/components/review-room/ChatPanel";
import DraftEditor from "@/components/draft-editor/DraftEditor";
import ImageGallery from "@/components/image-gallery/ImageGallery";
import AngleSelectStep from "@/components/ideation-wizard/AngleSelectStep";
import MovieInputStep from "@/components/ideation-wizard/MovieInputStep";
import RouteSelectStep from "@/components/ideation-wizard/RouteSelectStep";
import { api, type Angle, type Draft, type ImageAsset, type Route } from "@/lib/api";

type WizardStep =
  | "movie"
  | "angles"
  | "routes"
  | "text_review"
  | "images"
  | "complete";

const STEP_LABELS: Record<WizardStep, string> = {
  movie: "调研",
  angles: "选题",
  routes: "路线",
  text_review: "文案审稿",
  images: "配图",
  complete: "完成",
};

const WIZARD_STEPS: WizardStep[] = [
  "movie",
  "angles",
  "routes",
  "text_review",
  "images",
  "complete",
];

function stepIndex(step: WizardStep): number {
  return WIZARD_STEPS.indexOf(step);
}

function isStepReachable(target: WizardStep, furthestIndex: number): boolean {
  return stepIndex(target) <= furthestIndex;
}

type CreationWizardProps = {
  resumeSessionId?: string | null;
  onSessionCreated?: (sessionId: string) => void;
  onProgress?: () => void;
};

function formatResearchSummary(
  movie: { title: string; year?: number },
  opinions: Array<{ text: string }>
): string {
  const lines = opinions
    .slice(0, 3)
    .map((item) => `· ${item.text}`)
    .join("\n");
  const year = movie.year ? ` (${movie.year})` : "";
  return `${movie.title}${year}\n${lines}`;
}

export default function CreationWizard({
  resumeSessionId = null,
  onSessionCreated,
  onProgress,
}: CreationWizardProps) {
  const [step, setStep] = useState<WizardStep>("movie");
  const [furthestStepIndex, setFurthestStepIndex] = useState(0);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [anglesLoading, setAnglesLoading] = useState(false);
  const [routesLoading, setRoutesLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [statusHint, setStatusHint] = useState<string | null>(null);

  const [researchSummary, setResearchSummary] = useState<string | null>(null);
  const [angles, setAngles] = useState<Angle[]>([]);
  const [routes, setRoutes] = useState<Route[]>([]);
  const [selectedAngle, setSelectedAngle] = useState<Angle | null>(null);
  const [selectedRoute, setSelectedRoute] = useState<Route | null>(null);
  const [draft, setDraft] = useState<Draft | null>(null);
  const [images, setImages] = useState<ImageAsset[]>([]);
  const [busyImageId, setBusyImageId] = useState<string | null>(null);
  const [imagesRefreshKey, setImagesRefreshKey] = useState(0);

  const advanceToStep = useCallback((next: WizardStep) => {
    setStep(next);
    setFurthestStepIndex((prev) => Math.max(prev, stepIndex(next)));
  }, []);

  const goToStep = useCallback(
    (target: WizardStep) => {
      if (!isStepReachable(target, furthestStepIndex)) return;
      setStep(target);
      setError(null);
      if (target === "images" && sessionId) {
        void api.listImages(sessionId).then(
          (resp) => setImages(resp.images),
          () => undefined
        );
      }
    },
    [furthestStepIndex, sessionId]
  );

  const isIdeationReadOnly =
    stepIndex(step) < furthestStepIndex &&
    (step === "movie" || step === "angles" || step === "routes");

  const loadAngles = useCallback(
    async (id: string, force = false) => {
      setAnglesLoading(true);
      setError(null);
      setStatusHint("正在生成选题角度（约 30–60 秒）…");
      try {
        if (!force) {
          try {
            const cached = await api.getAngles(id);
            if (cached.angles?.length) {
              setAngles(cached.angles);
              return;
            }
          } catch {
            // not cached yet — generate below
          }
        }
        const angleResp = await api.generateAngles(id, force);
        setAngles(angleResp.angles);
        onProgress?.();
      } catch (err) {
        setError(err instanceof Error ? err.message : "生成选题失败");
      } finally {
        setAnglesLoading(false);
        setStatusHint(null);
      }
    },
    [onProgress]
  );

  const loadRoutes = useCallback(
    async (id: string, force = false) => {
      setRoutesLoading(true);
      setError(null);
      setStatusHint("正在加载论述路线…");
      try {
        if (!force) {
          try {
            const cached = await api.getRoutes(id);
            if (cached.routes?.length) {
              setRoutes(cached.routes);
              return;
            }
          } catch {
            // not cached yet
          }
        }
        const routeResp = await api.generateRoutes(id, force);
        setRoutes(routeResp.routes);
        onProgress?.();
      } catch (err) {
        setError(err instanceof Error ? err.message : "生成路线失败");
      } finally {
        setRoutesLoading(false);
        setStatusHint(null);
      }
    },
    [onProgress]
  );

  const run = useCallback(async (task: () => Promise<void>) => {
    setLoading(true);
    setError(null);
    try {
      await task();
      onProgress?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "操作失败");
    } finally {
      setLoading(false);
    }
  }, [onProgress]);

  const loadResearchSummary = useCallback(async (id: string) => {
    try {
      const research = await api.getResearch(id);
      setResearchSummary(formatResearchSummary(research.movie, research.opinions));
    } catch {
      setResearchSummary(null);
    }
  }, []);

  const resumeSession = useCallback(
    async (id: string) => {
      setSessionId(id);
      setLoading(true);
      setError(null);
      try {
        const detail = await api.getSession(id);
        await loadResearchSummary(id);

        if (detail.selected_angle?.title) {
          setSelectedAngle({
            id: (detail.selected_angle as Angle).id ?? "selected-angle",
            title: detail.selected_angle.title,
            description: detail.selected_angle.description,
          });
        }
        if (detail.selected_route?.title) {
          setSelectedRoute({
            id: (detail.selected_route as Route).id ?? "selected-route",
            title: detail.selected_route.title,
            outline: detail.selected_route.outline,
          });
        }

        if (detail.status === "angles_ready") {
          advanceToStep("angles");
          await loadAngles(id);
          return;
        }

        if (detail.status === "route_ready") {
          advanceToStep("routes");
          await loadRoutes(id);
          return;
        }

        try {
          const latest = await api.getDraft(id);
          setDraft({
            version: latest.version,
            title: latest.title,
            hooks: latest.hooks,
            body: latest.body,
            tags: latest.tags,
            review_round: latest.review_round,
          });
          if (detail.status === "text_finalized" || detail.status === "image_generating") {
            try {
              const imageResp = await api.listImages(id);
              setImages(imageResp.images);
            } catch {
              setImages([]);
            }
            advanceToStep("images");
          } else if (detail.status === "completed") {
            try {
              const imageResp = await api.listImages(id);
              setImages(imageResp.images);
            } catch {
              setImages([]);
            }
            advanceToStep("complete");
          } else {
            advanceToStep("text_review");
          }
          return;
        } catch {
          setStep("movie");
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : "恢复会话失败");
      } finally {
        setLoading(false);
        setStatusHint(null);
      }
    },
    [loadResearchSummary, advanceToStep, loadAngles, loadRoutes]
  );

  useEffect(() => {
    if (!resumeSessionId) return;
    void resumeSession(resumeSessionId);
  }, [resumeSessionId, resumeSession]);

  const handleMovieSubmit = async (title: string, year?: number) => {
    setLoading(true);
    setError(null);
    let newSessionId: string | null = null;
    try {
      setStatusHint("正在创建会话并调研影片…");
      const session = await api.createSession(title, year);
      newSessionId = session.id;
      setSessionId(session.id);
      onSessionCreated?.(session.id);

      const research = await api.research(session.id);
      setResearchSummary(formatResearchSummary(research.movie, research.opinions));

      advanceToStep("angles");
      onProgress?.();
    } catch (err) {
      setError(err instanceof Error ? err.message : "操作失败");
    } finally {
      setLoading(false);
      setStatusHint(null);
    }

    if (newSessionId) {
      await loadAngles(newSessionId);
    }
  };

  const handleAngleSelect = (angle: Angle) =>
    run(async () => {
      if (!sessionId) return;
      setStatusHint("已选角度，正在生成论述路线…");
      await api.selectAngle(sessionId, angle);
      setSelectedAngle(angle);
      advanceToStep("routes");
      await loadRoutes(sessionId);
    });

  const handleRouteSelect = (route: Route) =>
    run(async () => {
      if (!sessionId) return;
      setStatusHint("正在匹配评审团并生成初稿…");
      await api.selectRoute(sessionId, route);
      setSelectedRoute(route);
      await api.matchReviewers(sessionId);
      const draftResp = await api.generateDraft(sessionId);
      setDraft(draftResp.draft);
      advanceToStep("text_review");
      setStatusHint(null);
    });

  const refreshDraft = async () => {
    if (!sessionId) return;
    const latest = await api.getDraft(sessionId);
    setDraft({
      version: latest.version,
      title: latest.title,
      hooks: latest.hooks,
      body: latest.body,
      tags: latest.tags,
      review_round: latest.review_round,
    });
  };

  const handleDraftSave = (patch: Partial<Draft>) =>
    run(async () => {
      if (!sessionId) return;
      const resp = await api.patchDraft(sessionId, patch);
      setDraft(resp.draft);
    });

  const handleRegenerate = (part: "title" | "hooks" | "body" | "tags") =>
    run(async () => {
      if (!sessionId) return;
      const resp = await api.regeneratePart(sessionId, part);
      setDraft(resp.draft);
    });

  const handleDeAiPolish = () =>
    run(async () => {
      if (!sessionId) return;
      const resp = await api.deAiPolish(sessionId);
      setDraft(resp.draft);
    });

  const handleFinalizeText = () =>
    run(async () => {
      if (!sessionId) return;
      await api.finalizeText(sessionId);
      advanceToStep("images");
    });

  const handleGenerateImages = () =>
    run(async () => {
      if (!sessionId) return;
      setStatusHint("正在生成配图…");
      const resp = await api.generateImages(sessionId);
      setImages(resp.images);
      setImagesRefreshKey((key) => key + 1);
      setStatusHint(null);
    });

  const refreshImages = async () => {
    if (!sessionId) return;
    const resp = await api.listImages(sessionId);
    setImages(resp.images);
  };

  const handleRegenerateImage = (image: ImageAsset) =>
    run(async () => {
      if (!sessionId) return;
      setBusyImageId(image.id);
      try {
        await api.regenerateImage(sessionId, image.id, "审稿反馈优化");
        await refreshImages();
        setImagesRefreshKey((key) => key + 1);
      } finally {
        setBusyImageId(null);
      }
    });

  const handleFinalize = () =>
    run(async () => {
      if (!sessionId) return;
      await api.finalize(sessionId);
      advanceToStep("complete");
    });

  const viewingPastStep = stepIndex(step) < furthestStepIndex;
  const currentStepLabel = STEP_LABELS[WIZARD_STEPS[furthestStepIndex] ?? "movie"];

  return (
    <div data-testid="creation-wizard">
      <nav
        aria-label="创作步骤"
        style={{ display: "flex", flexWrap: "wrap", gap: "var(--space-2)", marginBottom: "var(--space-5)" }}
      >
        {WIZARD_STEPS.map((key) => {
          const reachable = isStepReachable(key, furthestStepIndex);
          const isCurrent = step === key;
          return (
            <button
              key={key}
              type="button"
              className="od-pill"
              aria-current={isCurrent ? "step" : undefined}
              disabled={!reachable || loading || anglesLoading || routesLoading}
              onClick={() => goToStep(key)}
              style={{
                color: isCurrent ? "var(--accent-hover)" : reachable ? "var(--fg)" : "var(--muted)",
                borderColor: isCurrent ? "rgba(94,106,210,0.5)" : undefined,
                cursor: reachable && !loading && !anglesLoading && !routesLoading ? "pointer" : "not-allowed",
                opacity: reachable ? 1 : 0.45,
              }}
            >
              {STEP_LABELS[key]}
            </button>
          );
        })}
      </nav>

      {viewingPastStep ? (
        <p
          className="od-muted"
          style={{ marginBottom: "var(--space-4)", fontSize: "var(--text-sm)" }}
        >
          正在查看前期内容。
          <button
            type="button"
            className="od-btn od-btn-ghost"
            style={{ marginLeft: "var(--space-2)", padding: "2px 8px", fontSize: "var(--text-xs)" }}
            onClick={() => goToStep(WIZARD_STEPS[furthestStepIndex])}
          >
            返回{currentStepLabel}
          </button>
        </p>
      ) : null}

      {statusHint ? (
        <p className="od-muted" style={{ marginBottom: "var(--space-4)", fontSize: "var(--text-sm)" }}>
          {statusHint}
        </p>
      ) : null}

      {error ? (
        <p style={{ color: "var(--danger)", marginBottom: "var(--space-4)", fontSize: "var(--text-sm)" }}>
          {error}
        </p>
      ) : null}

      {step === "movie" ? (
        <MovieInputStep
          onSubmit={handleMovieSubmit}
          loading={loading}
          researchSummary={researchSummary}
          readOnly={isIdeationReadOnly}
        />
      ) : null}

      {step === "angles" ? (
        <AngleSelectStep
          angles={angles}
          loading={anglesLoading}
          error={error}
          onSelect={handleAngleSelect}
          onRetry={sessionId ? () => loadAngles(sessionId, true) : undefined}
          readOnly={isIdeationReadOnly}
          selectedId={selectedAngle?.id ?? null}
          selectedTitle={selectedAngle?.title ?? null}
        />
      ) : null}

      {step === "routes" ? (
        <RouteSelectStep
          routes={routes}
          loading={loading || routesLoading}
          onSelect={handleRouteSelect}
          readOnly={isIdeationReadOnly}
          selectedId={selectedRoute?.id ?? null}
          selectedTitle={selectedRoute?.title ?? null}
        />
      ) : null}

      {step === "text_review" && sessionId && draft ? (
        <div style={{ display: "grid", gap: "var(--space-5)" }}>
          <DraftEditor
            draft={draft}
            onSave={handleDraftSave}
            onRegenerate={handleRegenerate}
            onDeAiPolish={handleDeAiPolish}
            busy={loading}
          />
          <ChatPanel sessionId={sessionId} phase="text" autoStart />
          <div style={{ display: "flex", gap: "var(--space-3)" }}>
            <button
              type="button"
              className="od-btn od-btn-ghost"
              onClick={() => refreshDraft()}
              disabled={loading}
            >
              刷新草稿
            </button>
            <button
              type="button"
              className="od-btn od-btn-primary"
              onClick={handleFinalizeText}
              disabled={loading}
            >
              文案满意，进入配图
            </button>
          </div>
        </div>
      ) : null}

      {step === "images" && sessionId ? (
        <div style={{ display: "grid", gap: "var(--space-5)" }}>
          <div style={{ display: "flex", gap: "var(--space-3)" }}>
            <button
              type="button"
              className="od-btn od-btn-primary"
              onClick={handleGenerateImages}
              disabled={loading}
            >
              {loading ? "生成中…" : "生成配图"}
            </button>
            <button
              type="button"
              className="od-btn od-btn-ghost"
              onClick={() => refreshImages()}
              disabled={loading}
            >
              刷新配图
            </button>
          </div>
          <ImageGallery
            images={images}
            onRegenerate={handleRegenerateImage}
            busyId={busyImageId}
          />
          <ChatPanel sessionId={sessionId} phase="image" autoStart={false} imagesRefreshKey={imagesRefreshKey} fallbackImages={images} />
          <button
            type="button"
            className="od-btn od-btn-primary"
            onClick={handleFinalize}
            disabled={loading}
          >
            完成创作
          </button>
        </div>
      ) : null}

      {step === "complete" && sessionId ? (
        <section className="od-card">
          <p className="od-eyebrow">Complete</p>
          <h3 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-2)" }}>
            创作已完成
          </h3>
          <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
            文案、审稿记录与配图已写入历史，可收藏或回放时间线。
          </p>
          <div style={{ marginTop: "var(--space-5)", display: "flex", gap: "var(--space-3)" }}>
            <Link href="/dashboard" className="btn btn-secondary">
              返回工作台
            </Link>
            <Link href={`/dashboard?session=${sessionId}`} className="btn btn-primary">
              查看时间线
            </Link>
          </div>
        </section>
      ) : null}
    </div>
  );
}
