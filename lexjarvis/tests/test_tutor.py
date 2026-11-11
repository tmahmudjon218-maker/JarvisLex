import pytest

from lexjarvis.knowledge import KnowledgeBase, split_into_chunks
from lexjarvis.prompts import NO_SOURCE_MESSAGE
from lexjarvis.tutor import Tutor, parse_quiz_json

TEXT = "# Huquq normalari\n\nHuquq normasi — majburiy xulq-atvor qoidasi."


class FakeBlock:
    type = "text"

    def __init__(self, text):
        self.text = text


class FakeClient:
    """Records the request and returns a canned reply; no network involved."""

    def __init__(self, reply):
        self.reply = reply
        self.calls = []
        self.messages = self

    def create(self, **kwargs):
        self.calls.append(kwargs)
        return type("R", (), {"content": [FakeBlock(self.reply)]})()


def make_tutor(reply="Javob [a.md#0]"):
    kb = KnowledgeBase(split_into_chunks("a.md", TEXT))
    client = FakeClient(reply)
    return Tutor(kb, client=client, model="test-model"), client


def test_ask_grounds_prompt_in_sources():
    tutor, client = make_tutor()
    answer = tutor.ask("Huquq normasi nima?")
    assert answer.grounded and answer.sources == ["a.md#0"]
    call = client.calls[0]
    assert call["model"] == "test-model"
    assert "majburiy xulq-atvor" in call["messages"][-1]["content"]


def test_ask_without_sources_never_calls_the_model():
    tutor, client = make_tutor()
    answer = tutor.ask("kvant fizikasi")
    assert not answer.grounded and answer.text == NO_SOURCE_MESSAGE
    assert client.calls == []


QUIZ = (
    '```json\n[{"question": "Q?", "options": ["a", "b", "c", "d"], "answer": 2,'
    ' "explanation": "e", "source": "a.md#0"},'
    ' {"question": "bad", "options": ["a"], "answer": 9}]\n```'
)


def test_parse_quiz_skips_malformed_and_strips_fences():
    questions = parse_quiz_json(QUIZ)
    assert len(questions) == 1 and questions[0].answer == 2


def test_parse_quiz_rejects_garbage():
    with pytest.raises(ValueError):
        parse_quiz_json("kechirasiz, test tuza olmadim")


def test_quiz_uses_model_output():
    tutor, _ = make_tutor(QUIZ)
    assert tutor.quiz("huquq normasi", n=3)[0].question == "Q?"
