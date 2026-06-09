from app.llm.prompts.reviewer import extract_reviewer_feedback


def test_extract_reviewer_feedback_uses_pros_and_cons():
    content, parts = extract_reviewer_feedback(
        {
            "pros": "标题有悬念。",
            "cons": "正文第二段偏空，建议补一个镜头细节。",
        }
    )
    assert "【亮点】标题有悬念。" in content
    assert "【待改】正文第二段偏空" in content
    assert parts["pros"] == "标题有悬念。"
    assert parts["cons"] == "正文第二段偏空，建议补一个镜头细节。"


def test_extract_reviewer_feedback_falls_back_to_content():
    content, parts = extract_reviewer_feedback(
        {"content": "整体不错，但标签还能更网感。"}
    )
    assert content == "整体不错，但标签还能更网感。"
    assert parts == {}
