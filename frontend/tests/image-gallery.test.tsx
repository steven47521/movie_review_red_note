import { cleanup, render, screen } from "@testing-library/react";
import { afterEach, describe, expect, test, vi } from "vitest";

import ImageGallery from "@/components/image-gallery/ImageGallery";

describe("ImageGallery", () => {
  afterEach(() => cleanup());

  test("renders cover and content images", () => {
    render(
      <ImageGallery
        images={[
          { id: "img-1", type: "cover", url: "https://cdn.example/cover.png" },
          { id: "img-2", type: "quote_card", url: "https://cdn.example/quote.png" },
          { id: "img-3", type: "mood_shot", url: "https://cdn.example/mood.png" },
        ]}
        onRegenerate={vi.fn()}
      />
    );

    expect(screen.getByRole("button", { name: /重生成封面/i })).toBeInTheDocument();
    expect(screen.getAllByRole("img")).toHaveLength(3);
  });
});
