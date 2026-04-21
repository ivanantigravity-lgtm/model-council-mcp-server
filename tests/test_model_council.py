from model_council_mcp_server.server import MODEL_GUIDE, _message_text


def test_message_text_string() -> None:
    response = {"choices": [{"message": {"content": "ok"}}]}
    assert _message_text(response) == "ok"


def test_model_guide_mentions_all_models() -> None:
    guide = MODEL_GUIDE.lower()
    assert "grok" in guide
    assert "gemini" in guide
    assert "deepseek" in guide
