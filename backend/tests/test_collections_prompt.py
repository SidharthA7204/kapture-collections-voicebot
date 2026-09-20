from app.ai.prompts.collections import (
    COLLECTIONS_SYSTEM_PROMPT,
)


def test_collections_prompt_exists():
    assert COLLECTIONS_SYSTEM_PROMPT.strip()


def test_collections_prompt_requires_authentication():
    prompt = COLLECTIONS_SYSTEM_PROMPT.lower()

    assert "authentication" in prompt
    assert "sensitive" in prompt
    assert "financial" in prompt


def test_collections_prompt_is_voice_friendly():
    prompt = COLLECTIONS_SYSTEM_PROMPT.lower()

    assert "concise" in prompt
    assert "natural" in prompt
    assert "one question at a time" in prompt
