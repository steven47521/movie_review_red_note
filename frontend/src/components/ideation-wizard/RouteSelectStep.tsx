"use client";

import type { Route } from "@/lib/api";

type RouteSelectStepProps = {
  routes: Route[];
  loading?: boolean;
  onSelect: (route: Route) => void;
  readOnly?: boolean;
  selectedId?: string | null;
  selectedTitle?: string | null;
};

export default function RouteSelectStep({
  routes,
  loading = false,
  onSelect,
  readOnly = false,
  selectedId = null,
  selectedTitle = null,
}: RouteSelectStepProps) {
  return (
    <section className="od-card" data-testid="route-select-step">
      <p className="od-eyebrow">Step 3</p>
      <h3 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-2)" }}>
        选择论述路线
      </h3>
      <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
        {readOnly
          ? "已选定的论述路线如下，点击顶部步骤可返回当前进度。"
          : "两套路线论证结构应明显不同，选定后进入成稿与审稿。"}
      </p>

      {loading ? <p className="od-muted">生成路线中…</p> : null}

      <div
        style={{
          marginTop: "var(--space-5)",
          display: "grid",
          gap: "var(--space-4)",
          gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))",
        }}
      >
        {routes.map((route) => {
          const isSelected =
            selectedId === route.id ||
            (!!selectedTitle && selectedTitle === route.title);
          return readOnly ? (
            <article
              key={route.id}
              className="od-card"
              style={{
                textAlign: "left",
                borderColor: isSelected ? "rgba(94,106,210,0.6)" : undefined,
                background: isSelected ? "rgba(94,106,210,0.08)" : undefined,
              }}
            >
              <p style={{ margin: 0, fontWeight: 510, color: "var(--fg)" }}>
                {route.title}
                {isSelected ? (
                  <span className="od-pill" style={{ marginLeft: "var(--space-2)", fontSize: "var(--text-xs)" }}>
                    已选
                  </span>
                ) : null}
              </p>
              {route.outline?.length ? (
                <ul className="od-muted" style={{ marginTop: "var(--space-3)", paddingLeft: "18px" }}>
                  {route.outline.map((item) => (
                    <li key={item}>{item}</li>
                  ))}
                </ul>
              ) : null}
            </article>
          ) : (
          <button
            key={route.id}
            type="button"
            className="od-card"
            onClick={() => onSelect(route)}
            disabled={loading}
            style={{
              textAlign: "left",
              cursor: loading ? "not-allowed" : "pointer",
              opacity: loading ? 0.6 : 1,
            }}
          >
            <p style={{ margin: 0, fontWeight: 510, color: "var(--fg)" }}>{route.title}</p>
            {route.outline?.length ? (
              <ul className="od-muted" style={{ marginTop: "var(--space-3)", paddingLeft: "18px" }}>
                {route.outline.map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            ) : null}
          </button>
          );
        })}
      </div>
    </section>
  );
}
