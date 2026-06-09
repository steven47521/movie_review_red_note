MODERATOR_SYSTEM = """你是审稿团汇总编辑（Moderator）。
阅读所有审稿人的亮点与待改意见，给出综合结论与明确改稿指令。
优先汇总 cons 中的共性问题，不要只复述 praise。
返回 JSON：{"content": "综合评语", "revision_instructions": "改稿指令"}
"""


def build_moderator_user(reviews: list[dict], draft: dict) -> str:
    review_lines = "\n".join(f"- {r['nickname']}: {r['content']}" for r in reviews)
    return (
        f"当前文案标题：{draft.get('title')}\n"
        f"审稿意见：\n{review_lines}\n"
        "请汇总必须修改的点。"
    )
