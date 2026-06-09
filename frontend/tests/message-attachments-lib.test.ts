import { describe, expect, test } from "vitest";

import { extractAttachmentImages } from "@/lib/message-attachments";

describe("message attachments lib", () => {
  test("extracts images array from attachment", () => {
    const items = extractAttachmentImages({
      images: [
        { id: "1", type: "cover", url: "/static/images/s1/cover.jpg", label: "封面" },
      ],
    });
    expect(items).toHaveLength(1);
    expect(items[0]?.url).toBe("/static/images/s1/cover.jpg");
  });

  test("resolves regenerated ids from fallback images", () => {
    const items = extractAttachmentImages(
      { regenerated: ["img-2"] },
      [{ id: "img-2", type: "quote_card", url: "/static/images/s1/q.jpg" }]
    );
    expect(items[0]?.type).toBe("quote_card");
    expect(items[0]?.url).toBe("/static/images/s1/q.jpg");
  });
});
