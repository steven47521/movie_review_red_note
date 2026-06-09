"use client";

import { useEffect, useState } from "react";

import type { Draft } from "@/lib/api";

type DraftEditorProps = {
  draft: Draft;
  onSave: (patch: Partial<Draft>) => void | Promise<void>;
  onRegenerate?: (part: "title" | "hooks" | "body" | "tags") => void | Promise<void>;
  onDeAiPolish?: () => void | Promise<void>;
  busy?: boolean;
};

export default function DraftEditor({
  draft,
  onSave,
  onRegenerate,
  onDeAiPolish,
  busy = false,
}: DraftEditorProps) {
  const [title, setTitle] = useState(draft.title);
  const [hooksText, setHooksText] = useState(draft.hooks.join("\n"));
  const [body, setBody] = useState(draft.body);
  const [tagsText, setTagsText] = useState(draft.tags.join(" "));

  useEffect(() => {
    setTitle(draft.title);
    setHooksText(draft.hooks.join("\n"));
    setBody(draft.body);
    setTagsText(draft.tags.join(" "));
  }, [draft]);

  const handleSave = () => {
    onSave({
      title,
      hooks: hooksText.split("\n").map((line) => line.trim()).filter(Boolean),
      body,
      tags: tagsText.split(/\s+/).map((tag) => tag.trim()).filter(Boolean),
    });
  };

  const inputStyle = {
    width: "100%",
    background: "rgba(255,255,255,0.02)",
    border: "1px solid var(--border)",
    borderRadius: "var(--radius-sm)",
    color: "var(--fg-2)",
    padding: "12px 14px",
    fontFamily: "var(--font-body)",
    fontSize: "var(--text-sm)",
  } as const;

  return (
    <section className="od-card" data-testid="draft-editor">
      <p className="od-eyebrow">Draft Editor</p>
      <h3 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-2)" }}>
        文案编辑
      </h3>
      <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
        版本 v{draft.version} · 支持分段重写、去 AI 感、手动保存
      </p>

      <div style={{ marginTop: "var(--space-5)", display: "grid", gap: "var(--space-4)" }}>
        <label>
          <span className="od-muted" style={{ fontSize: "var(--text-sm)" }}>
            标题
          </span>
          <input
            aria-label="标题"
            value={title}
            onChange={(event) => setTitle(event.target.value)}
            style={{ ...inputStyle, marginTop: "var(--space-2)" }}
          />
        </label>

        <label>
          <span className="od-muted" style={{ fontSize: "var(--text-sm)" }}>
            Hooks（每行一条）
          </span>
          <textarea
            aria-label="Hooks"
            value={hooksText}
            onChange={(event) => setHooksText(event.target.value)}
            rows={3}
            style={{ ...inputStyle, marginTop: "var(--space-2)", resize: "vertical" }}
          />
        </label>

        <label>
          <span className="od-muted" style={{ fontSize: "var(--text-sm)" }}>
            正文
          </span>
          <textarea
            aria-label="正文"
            value={body}
            onChange={(event) => setBody(event.target.value)}
            rows={8}
            style={{ ...inputStyle, marginTop: "var(--space-2)", resize: "vertical" }}
          />
        </label>

        <label>
          <span className="od-muted" style={{ fontSize: "var(--text-sm)" }}>
            标签（空格分隔）
          </span>
          <input
            aria-label="标签"
            value={tagsText}
            onChange={(event) => setTagsText(event.target.value)}
            style={{ ...inputStyle, marginTop: "var(--space-2)" }}
          />
        </label>
      </div>

      <div style={{ marginTop: "var(--space-5)", display: "flex", flexWrap: "wrap", gap: "var(--space-3)" }}>
        <button type="button" className="od-btn od-btn-primary" onClick={handleSave} disabled={busy}>
          保存编辑
        </button>
        {onRegenerate ? (
          <>
            <button
              type="button"
              className="od-btn od-btn-ghost"
              onClick={() => onRegenerate("title")}
              disabled={busy}
            >
              重写标题
            </button>
            <button
              type="button"
              className="od-btn od-btn-ghost"
              onClick={() => onRegenerate("body")}
              disabled={busy}
            >
              重写正文
            </button>
          </>
        ) : null}
        {onDeAiPolish ? (
          <button type="button" className="od-btn od-btn-ghost" onClick={onDeAiPolish} disabled={busy}>
            去 AI 感润色
          </button>
        ) : null}
      </div>
    </section>
  );
}
