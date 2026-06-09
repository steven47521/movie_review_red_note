DRAFT_SYSTEM = """你是小红书思想向影评作者。
根据选定论述路线写标题、hooks、正文、标签。
要求：有观点、非剧情复述、反AI套话（禁止「综上所述」等）。
返回 JSON：{"title": "...", "hooks": ["...", "..."], "body": "...", "tags": ["#...", ...]}
"""

REVISION_SYSTEM = """你是改稿 Writer Agent。
根据 Moderator 指令修订文案，在聊天室说明修改摘要。
返回 JSON：{"title": "...", "hooks": [...], "body": "...", "tags": [...], "summary": "修改摘要"}
"""


def build_draft_user(movie: dict, angle: dict, route: dict) -> str:
    return (
        f"电影：{movie.get('title')} ({movie.get('year', '')})\n"
        f"主题角度：{angle.get('title')} — {angle.get('description', '')}\n"
        f"论述路线：{route.get('title')}\n"
        f"大纲：{route.get('outline')}\n"
        "请生成小红书思想向影评文案。"
    )


def build_revision_user(draft: dict, instructions: str) -> str:
    return (
        f"改稿指令：{instructions}\n"
        f"当前标题：{draft.get('title')}\n"
        f"当前正文：{draft.get('body')}\n"
        f"当前标签：{draft.get('tags')}\n"
        "请输出修订稿。"
    )
