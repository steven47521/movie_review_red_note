from app.llm.prompts.reviewer import (
    FOCUS_LABELS,
    TONE_LABELS,
    extract_reviewer_feedback,
)

IMAGE_REVIEWER_SYSTEM = """你是小红书影视笔记配图审稿人。你的职责是认真审稿，不是讨好作者。

每条意见必须分成两部分，且两部分都要有实质内容：
1. pros（亮点）：1-2 句，指出配图真正好的地方，要具体到某张图的类型/风格/氛围。
2. cons（待改）：1-3 句，指出必须改进的问题，要尖锐、可执行；禁止空泛表扬。

禁止只赞美不批评。即使整体尚可，cons 也必须指出下一版可优化的具体问题。
返回 JSON：{"pros": "亮点", "cons": "待改", "scores": {"style":1-10,"quote_accuracy":1-10,"aesthetic":1-10,"consistency":1-10}}
"""

IMAGE_MODERATOR_SYSTEM = """你是配图审稿 Moderator。
汇总审稿意见，指出需要重生成的图片类型。
返回 JSON：{"content": "综合评语", "regenerate_types": ["cover"|"quote_card"|"mood_shot"|"theme_visual"]}
"""


def build_image_reviewer_user(persona: dict, images: list[dict], draft: dict) -> str:
    taste = persona.get("taste_profile") or {}
    focus = FOCUS_LABELS.get(str(taste.get("focus", "")), "综合质量")
    tone = TONE_LABELS.get(str(taste.get("tone", "")), "直接")
    image_lines = "\n".join(
        f"- {img['type']}: {img['url']} (prompt: {img['prompt'][:80]}...)"
        for img in images
    )
    return (
        f"审稿人：{persona['nickname']} ({persona['mbti']}·{persona['age_band']})\n"
        f"审稿偏好：关注{focus}，语气{tone}。\n"
        f"文案标题：{draft.get('title')}\n"
        f"配图列表：\n{image_lines}\n"
        "请分别写出亮点（pros）和待改（cons）。cons 至少提出 1 个具体问题，禁止只夸不批。"
    )


def build_image_moderator_user(reviews: list[dict], images: list[dict]) -> str:
    review_lines = "\n".join(f"- {r['nickname']}: {r['content']}" for r in reviews)
    return f"配图审稿意见：\n{review_lines}\n当前图片：{[i['type'] for i in images]}"
