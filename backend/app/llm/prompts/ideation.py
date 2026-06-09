ANGLES_SYSTEM = """你是经典电影小红书选题顾问。
根据主流观点摘要，提出 3-5 个「思想/主题向」切入点。
要求：
- 必须是可讨论的观点角度，不是剧情梗概
- 标题简洁有吸引力
- 用 JSON 返回：{"angles": [{"id": "a1", "title": "...", "description": "..."}]}
"""

ROUTES_SYSTEM = """你是影评结构策划。
根据已选主题角度，设计 2 套不同的论述路线（论证结构须明显不同）。
用 JSON 返回：{"routes": [{"id": "r1", "title": "...", "outline": ["...", "..."]}]}
"""


def build_angles_user(movie: dict, opinions: list[dict]) -> str:
    opinion_lines = "\n".join(
        f"- [{o.get('source', 'unknown')}] {o.get('text', '')}" for o in opinions
    )
    return (
        f"电影：{movie.get('title')} ({movie.get('year', '')})\n"
        f"类型：{', '.join(movie.get('genres') or [])}\n"
        f"主流观点摘要：\n{opinion_lines}\n"
        "请给出 3-5 个思想向主题切入点。"
    )


def build_routes_user(movie: dict, angle: dict, opinions: list[dict]) -> str:
    opinion_lines = "\n".join(f"- {o.get('text', '')}" for o in opinions[:5])
    return (
        f"电影：{movie.get('title')}\n"
        f"选定主题：{angle.get('title')} — {angle.get('description', '')}\n"
        f"参考观点：\n{opinion_lines}\n"
        "请给出 2 套论述结构不同的写作路线。"
    )
