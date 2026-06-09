import Link from "next/link";

import {
  PLACEHOLDER_SESSIONS,
  STATUS_LABELS,
  type SessionPlaceholder,
} from "@/lib/placeholder-sessions";

function SessionCard({ session }: { session: SessionPlaceholder }) {
  const statusLabel = STATUS_LABELS[session.status] ?? session.status;

  return (
    <article className="od-card">
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", gap: "var(--space-3)" }}>
        <div>
          <h3 style={{ margin: 0, fontSize: "var(--text-base)", fontWeight: 510, color: "var(--fg)" }}>
            {session.movieTitle}
          </h3>
          <p className="od-muted" style={{ marginTop: "var(--space-1)" }}>
            更新于 {session.updatedAt}
          </p>
        </div>
        <span className="od-pill">{statusLabel}</span>
      </div>

      <div style={{ marginTop: "var(--space-4)", display: "flex", gap: "var(--space-2)" }}>
        {session.isFavorite ? (
          <span className="od-pill" style={{ color: "var(--accent-hover)" }}>
            已收藏
          </span>
        ) : null}
        {session.isPublished ? (
          <span className="od-pill" style={{ color: "var(--success)" }}>
            已发布
          </span>
        ) : null}
        <Link href="/dashboard/create" className="od-muted" style={{ fontSize: "var(--text-xs)" }}>
          继续创作 →
        </Link>
      </div>
    </article>
  );
}

export default function SessionList() {
  return (
    <section>
      <div
        style={{
          marginBottom: "var(--space-4)",
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
        }}
      >
        <h2 className="od-muted" style={{ margin: 0, fontWeight: 510 }}>
          创作历史
        </h2>
        <span className="od-muted" style={{ fontSize: "var(--text-xs)" }}>
          {PLACEHOLDER_SESSIONS.length} 条记录（占位）
        </span>
      </div>

      <div
        style={{
          display: "grid",
          gap: "var(--space-4)",
          gridTemplateColumns: "repeat(auto-fill, minmax(260px, 1fr))",
        }}
      >
        {PLACEHOLDER_SESSIONS.map((session) => (
          <SessionCard key={session.id} session={session} />
        ))}
      </div>
    </section>
  );
}
