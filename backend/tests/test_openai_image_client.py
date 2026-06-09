from app.clients.openai_image_client import should_use_placeholder


def test_should_use_placeholder_false_by_default():
    assert should_use_placeholder() is False
