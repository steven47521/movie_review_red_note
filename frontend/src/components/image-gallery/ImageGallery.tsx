"use client";

import type { ImageAsset } from "@/lib/api";
import { resolveAssetUrl } from "@/lib/api";

const TYPE_LABELS: Record<string, string> = {
  cover: "封面",
  quote_card: "金句卡",
  mood_shot: "氛围图",
  theme_visual: "主题视觉",
};

type ImageGalleryProps = {
  images: ImageAsset[];
  onRegenerate?: (image: ImageAsset) => void | Promise<void>;
  busyId?: string | null;
};

export default function ImageGallery({
  images,
  onRegenerate,
  busyId = null,
}: ImageGalleryProps) {
  if (!images.length) {
    return (
      <section className="od-card" data-testid="image-gallery">
        <p className="od-muted">尚未生成配图，请先完成文案定稿并触发生成。</p>
      </section>
    );
  }

  return (
    <section className="od-card" data-testid="image-gallery">
      <p className="od-eyebrow">Image Gallery</p>
      <h3 className="od-title" style={{ fontSize: "var(--text-lg)", marginTop: "var(--space-2)" }}>
        配图预览
      </h3>
      <p className="od-muted" style={{ marginTop: "var(--space-2)" }}>
        封面 + 内容图，支持单张重生成与下载预览。
      </p>

      <div
        style={{
          marginTop: "var(--space-5)",
          display: "grid",
          gap: "var(--space-4)",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
        }}
      >
        {images.map((image) => {
          const label = TYPE_LABELS[image.type] ?? image.type;
          const regenerateLabel = `重生成${label}`;

          return (
            <article key={image.id} className="od-card" style={{ padding: "var(--space-4)" }}>
              <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                <span className="od-pill">{label}</span>
                <span className="od-muted" style={{ fontSize: "var(--text-xs)" }}>
                  v{image.version ?? 1}
                </span>
              </div>

              <img
                src={resolveAssetUrl(image.url)}
                alt={label}
                style={{
                  marginTop: "var(--space-3)",
                  width: "100%",
                  aspectRatio: "4 / 5",
                  objectFit: "cover",
                  borderRadius: "var(--radius-md)",
                  border: "1px solid var(--border)",
                }}
              />

              <div style={{ marginTop: "var(--space-3)", display: "flex", gap: "var(--space-2)" }}>
                <a
                  href={resolveAssetUrl(image.url)}
                  target="_blank"
                  rel="noreferrer"
                  className="od-btn od-btn-ghost"
                  style={{ fontSize: "var(--text-xs)", padding: "6px 10px" }}
                >
                  预览
                </a>
                {onRegenerate ? (
                  <button
                    type="button"
                    className="od-btn od-btn-ghost"
                    style={{ fontSize: "var(--text-xs)", padding: "6px 10px" }}
                    onClick={() => onRegenerate(image)}
                    disabled={busyId === image.id}
                  >
                    {busyId === image.id ? "生成中…" : regenerateLabel}
                  </button>
                ) : null}
              </div>
            </article>
          );
        })}
      </div>
    </section>
  );
}
