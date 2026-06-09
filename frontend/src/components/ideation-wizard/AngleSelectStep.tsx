"use client";

import type { Angle } from "@/lib/api";

type AngleSelectStepProps = {
  angles: Angle[];
  loading?: boolean;
  error?: string | null;
  onSelect: (angle: Angle) => void;
  onRetry?: () => void;
  readOnly?: boolean;
  selectedId?: string | null;
  selectedTitle?: string | null;
};

export default function AngleSelectStep({
  angles,
  loading = false,
  error = null,
  onSelect,
  onRetry,
  readOnly = false,
  selectedId = null,
  selectedTitle = null,
}: AngleSelectStepProps) {
  const showRetry = !readOnly && !loading && angles.length === 0 && onRetry;

  return (
    <section className="od-card" data-testid="angle-select-step">
      <p className="od-eyebrow">Step 2</p>
      <h3 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-2)" }}>
        选择主题切入点
      </h3>
      <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
        {readOnly
          ? "已选定的主题切入点如下，点击顶部步骤可返回当前进度。"
          : "从 3–5 个思想向角度中选 1 个，避免纯剧情复述。"}
      </p>

      {loading ? <p className="od-muted">生成切入点中…</p> : null}

      {error && !loading ? (
        <p style={{ color: "var(--danger)", marginTop: "var(--space-3)", fontSize: "var(--text-sm)" }}>
          {error}
        </p>
      ) : null}

      {showRetry ? (
        <button
          type="button"
          className="od-btn od-btn-primary"
          style={{ marginTop: "var(--space-4)" }}
          onClick={onRetry}
        >
          重新生成选题
        </button>
      ) : null}

      <div
        style={{
          marginTop: "var(--space-5)",
          display: "grid",
          gap: "var(--space-3)",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
        }}
      >
        {angles.map((angle) => {
          const isSelected =
            selectedId === angle.id ||
            (!!selectedTitle && selectedTitle === angle.title);
          return readOnly ? (
            <article
              key={angle.id}
              className="od-card"
              style={{
                textAlign: "left",
                borderColor: isSelected ? "rgba(94,106,210,0.6)" : undefined,
                background: isSelected ? "rgba(94,106,210,0.08)" : undefined,
              }}
            >
              <p style={{ margin: 0, fontWeight: 510, color: "var(--fg)" }}>
                {angle.title}
                {isSelected ? (
                  <span className="od-pill" style={{ marginLeft: "var(--space-2)", fontSize: "var(--text-xs)" }}>
                    已选
                  </span>
                ) : null}
              </p>
              {angle.description ? (
                <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
                  {angle.description}
                </p>
              ) : null}
            </article>
          ) : (
          <button
            key={angle.id}
            type="button"
            className="od-card"
            onClick={() => onSelect(angle)}
            disabled={loading}
            style={{
              textAlign: "left",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
            <p style={{ margin: 0, fontWeight: 510, color: "var(--fg)" }}>{angle.title}</p>
            {angle.description ? (
              <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
                {angle.description}
              </p>
            ) : null}
          </button>
          );
        })}
      </div>
    </section>
  );
}
