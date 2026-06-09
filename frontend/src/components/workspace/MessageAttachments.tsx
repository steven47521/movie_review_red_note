"use client";

import type { ImageAsset } from "@/lib/api";
import { resolveAssetUrl } from "@/lib/api";
import {
  extractAttachmentImages,
  labelForImageType,
  type AttachmentImage,
} from "@/lib/message-attachments";

type MessageAttachmentsProps = {
  attachment?: Record<string, unknown>;
  fallbackImages?: ImageAsset[];
  title?: string;
};

export default function MessageAttachments({
  attachment,
  fallbackImages = [],
  title = "配图预览",
}: MessageAttachmentsProps) {
  const items = extractAttachmentImages(attachment, fallbackImages);
  if (!items.length) return null;

  return (
    <div className="message-attachment" data-testid="message-attachments">
      <p className="attachment-title">{title}</p>
      <div className="attachment-grid">
        {items.map((item) => (
          <AttachmentCell key={item.id ?? `${item.type}-${item.url}`} item={item} />
        ))}
      </div>
    </div>
  );
}

function AttachmentCell({ item }: { item: AttachmentImage }) {
  const label = item.label ?? labelForImageType(item.type);
  const src = resolveAssetUrl(item.url);

  return (
    <article className="attachment-cell">
      <strong>{label}</strong>
      {item.version ? (
        <span className="small-copy">v{item.version}</span>
      ) : null}
      <a href={src} target="_blank" rel="noreferrer">
        <img src={src} alt={label} className="attachment-image" loading="lazy" />
      </a>
    </article>
  );
}
