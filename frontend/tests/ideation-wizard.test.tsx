import { cleanup, render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { afterEach, describe, expect, test, vi } from "vitest";

import AngleSelectStep from "@/components/ideation-wizard/AngleSelectStep";
import MovieInputStep from "@/components/ideation-wizard/MovieInputStep";
import RouteSelectStep from "@/components/ideation-wizard/RouteSelectStep";

describe("Ideation wizard steps", () => {
  afterEach(() => cleanup());

  test("movie input step renders title field and submit", () => {
    render(<MovieInputStep onSubmit={vi.fn()} loading={false} />);
    expect(screen.getByLabelText(/电影片名/i)).toBeInTheDocument();
    expect(screen.getByRole("button", { name: /开始调研/i })).toBeInTheDocument();
  });

  test("angle step renders selectable cards", async () => {
    const onSelect = vi.fn();
    render(
      <AngleSelectStep
        angles={[
          { id: "a1", title: "体制与希望", description: "主题向" },
          { id: "a2", title: "友谊与自由", description: "关系向" },
          { id: "a3", title: "时间与人性", description: "叙事向" },
        ]}
        onSelect={onSelect}
      />
    );

    await userEvent.click(screen.getByRole("button", { name: /体制与希望/i }));
    expect(onSelect).toHaveBeenCalledWith(
      expect.objectContaining({ id: "a1", title: "体制与希望" })
    );
  });

  test("route step renders two distinct routes", async () => {
    const onSelect = vi.fn();
    render(
      <RouteSelectStep
        routes={[
          { id: "r1", title: "情绪共鸣路线", outline: ["开场", "共鸣", "收束"] },
          { id: "r2", title: "结构拆解路线", outline: ["镜头", "叙事", "主题"] },
        ]}
        onSelect={onSelect}
      />
    );

    expect(screen.getByText("情绪共鸣路线")).toBeInTheDocument();
    expect(screen.getByText("结构拆解路线")).toBeInTheDocument();
    await userEvent.click(screen.getByRole("button", { name: /结构拆解路线/i }));
    expect(onSelect).toHaveBeenCalledWith(
      expect.objectContaining({ id: "r2" })
    );
  });
});
