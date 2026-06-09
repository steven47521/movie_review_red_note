import type { ImageAsset } from "@/lib/api";

export const IMAGE_TYPE_LABELS: Record<string, string> = {
  cover: "封面",
  quote_card: "金句卡",
  mood_shot: "氛围图",
  theme_visual: "主题视觉",
};

export type AttachmentImage = {
  id?: string;
  type?: string;
  url: string;
  label?: string;
  version?: number;
};

export function labelForImageType(type?: string): string {
  if (!type) return "配图";
  return IMAGE_TYPE_LABELS[type] ?? type;
}

export function extractAttachmentImages(
  attachment?: Record<string, unknown>,
  fallbackImages: ImageAsset[] = []
): AttachmentImage[] {
  if (!attachment) return [];

  const raw = attachment.images;
  if (Array.isArray(raw)) {
    const parsed: AttachmentImage[] = [];
    for (const item of raw) {
      if (typeof item === "string") {
        parsed.push({ url: item });
        continue;
      }
      if (item && typeof item === "object") {
        const record = item as Record<string, unknown>;
        const url = record.url ?? record.image_url;
        if (typeof url === "string" && url) {
          parsed.push({
            id: typeof record.id === "string" ? record.id : undefined,
            type: typeof record.type === "string" ? record.type : undefined,
            url,
            label: typeof record.label === "string" ? record.label : undefined,
            version: typeof record.version === "number" ? record.version : undefined,
          });
        }
      }
    }
    if (parsed.length) return parsed;
  }

  const regenerated = attachment.regenerated;
  if (Array.isArray(regenerated) && fallbackImages.length) {
    const ids = regenerated.filter((item): item is string => typeof item === "string");
    return fallbackImages
      .filter((image) => ids.includes(image.id))
      .map((image) => ({
        id: image.id,
        type: image.type,
        url: image.url,
        label: labelForImageType(image.type),
        version: image.version,
      }));
  }

  const singleUrl = attachment.url ?? attachment.image_url;
  if (typeof singleUrl === "string" && singleUrl) {
    return [
      {
        url: singleUrl,
        type: typeof attachment.type === "string" ? attachment.type : undefined,
        label:
          typeof attachment.label === "string"
            ? attachment.label
            : labelForImageType(
                typeof attachment.type === "string" ? attachment.type : undefined
              ),
      },
    ];
  }

  return [];
}
