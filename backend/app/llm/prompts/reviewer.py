FOCUS_LABELS = {
    "structure": "论证结构",
    "ideas": "观点新意",
    "argument": "论点力度",
    "debate": "思辨交锋",
    "meaning": "主题深度",
    "values": "价值表达",
    "resonance": "情感共鸣",
    "emotion": "情绪张力",
    "craft": "文字功底",
    "character": "人物解读",
    "clarity": "表达清晰",
    "audience": "读者视角",
    "visuals": "画面感",
    "aesthetics": "审美品味",
    "punch": "开头冲击力",
    "vibe": "整体氛围",
}

TONE_LABELS = {
    "analytical": "冷静分析",
    "curious": "好奇追问",
    "direct": "直截了当",
    "witty": "犀利幽默",
    "empathetic": "共情细腻",
    "poetic": "诗意感性",
    "warm": "温和鼓励",
    "energetic": "热情外放",
    "precise": "字斟句酌",
    "gentle": "轻声提醒",
    "firm": "态度坚定",
    "friendly": "像朋友聊天",
    "cool": "克制冷淡",
    "sensitive": "敏感细致",
    "bold": "不留情面",
    "playful": "轻松调侃",
}

REVIEWER_SYSTEM = """你是小红书资深影评博主审稿人。你的职责是认真审稿，不是讨好作者。

每条意见必须分成两部分，且两部分都要有实质内容：
1. pros（亮点）：1-2 句，指出文案真正好的地方，要具体到标题/钩子/正文/标签中的某处。
2. cons（待改）：1-3 句，指出必须改进的问题，要尖锐、可执行；禁止空泛表扬或只说「很好」「不错」。

禁止只赞美不批评。即使整体尚可，cons 也必须指出下一版可优化的具体问题。
用拟人化、有品味的口吻，避免机器腔。
返回 JSON：{"pros": "亮点", "cons": "待改", "scores": {"depth": 1-10, "novelty": 1-10, "anti_ai": 1-10, "title": 1-10, "tags": 1-10}}
"""


def extract_reviewer_feedback(result: dict) -> tuple[str, dict[str, str]]:
    """Normalize LLM reviewer JSON into display text and structured parts."""
    pros = str(result.get("pros") or "").strip()
    cons = str(result.get("cons") or "").strip()
    parts: dict[str, str] = {}
    if pros:
        parts["pros"] = pros
    if cons:
        parts["cons"] = cons
    if pros and cons:
        return f"【亮点】{pros}\n\n【待改】{cons}", parts

    content = str(result.get("content") or "").strip()
    if content:
        return content, parts
    return "（审稿人未返回有效意见）", parts


def build_reviewer_user(persona: dict, draft: dict) -> str:
    taste = persona.get("taste_profile") or {}
    focus = FOCUS_LABELS.get(str(taste.get("focus", "")), "综合质量")
    tone = TONE_LABELS.get(str(taste.get("tone", "")), "直接")
    return (
        f"你是{persona['nickname']}（{persona['mbti']}·{persona['age_band']}）。\n"
        f"审稿偏好：关注{focus}，语气{tone}。\n"
        f"标题：{draft.get('title')}\n"
        f"Hooks：{draft.get('hooks')}\n"
        f"正文：{draft.get('body')}\n"
        f"标签：{draft.get('tags')}\n"
        "请分别写出亮点（pros）和待改（cons）。cons 至少提出 1 个具体问题，禁止只夸不批。"
    )
