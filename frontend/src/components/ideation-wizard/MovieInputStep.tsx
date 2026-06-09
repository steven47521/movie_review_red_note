"use client";

import { FormEvent, useState } from "react";

type MovieInputStepProps = {
  onSubmit: (title: string, year?: number) => void;
  loading?: boolean;
  researchSummary?: string | null;
  readOnly?: boolean;
};

export default function MovieInputStep({
  onSubmit,
  loading = false,
  researchSummary,
  readOnly = false,
}: MovieInputStepProps) {
  const [title, setTitle] = useState("");
  const [year, setYear] = useState("");

  const handleSubmit = (event: FormEvent) => {
    event.preventDefault();
    if (!title.trim()) return;
    onSubmit(title.trim(), year ? Number(year) : undefined);
  };

  return (
    <section className="od-card" data-testid="movie-input-step">
      <p className="od-eyebrow">Step 1</p>
      <h3 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-2)" }}>
        输入电影片名
      </h3>
      <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
        {readOnly
          ? "调研已完成，可在顶部步骤条切换查看各阶段内容。"
          : "系统会先调研影片元数据与主流观点，再进入选题。"}
      </p>

      {!readOnly ? (
      <form onSubmit={handleSubmit} style={{ marginTop: "var(--space-5)", display: "grid", gap: "var(--space-4)" }}>
        <label className="field">
          <span style={{ fontSize: "var(--text-sm)", color: "var(--muted)" }}>电影片名</span>
          <input
            aria-label="电影片名"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            placeholder="例如：肖申克的救赎"
            className="field-input"
          />
        </label>

        <label className="field">
          <span style={{ fontSize: "var(--text-sm)", color: "var(--muted)" }}>年份（可选）</span>
          <input
            aria-label="年份"
            value={year}
            onChange={(event) => setYear(event.target.value)}
            placeholder="1994"
            inputMode="numeric"
            className="field-input"
          />
        </label>

        <button type="submit" className="btn btn-primary" disabled={loading || !title.trim()}>
          {loading ? "调研中…" : "开始调研"}
        </button>
      </form>
      ) : null}

      {researchSummary ? (
        <div
          className="od-card"
          style={{ marginTop: "var(--space-5)", padding: "var(--space-4)", background: "rgba(255,255,255,0.03)" }}
        >
          <p className="od-eyebrow">调研摘要</p>
          <p className="od-muted" style={{ marginTop: "var(--space-2)", whiteSpace: "pre-wrap" }}>
            {researchSummary}
          </p>
        </div>
      ) : null}
    </section>
  );
}
