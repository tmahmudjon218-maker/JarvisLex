"""Command-line interface: ``lexjarvis ask|quiz|chat``."""

from __future__ import annotations

import argparse
import sys

from .knowledge import KnowledgeBase
from .tutor import Tutor

LETTERS = "ABCD"


def _build_tutor(sources: str) -> Tutor:
    kb = KnowledgeBase.from_directory(sources)
    if len(kb) == 0:
        sys.exit(f"'{sources}' papkasida .md yoki .txt manba topilmadi.")
    return Tutor(kb)


def _print_answer(answer) -> None:
    print(answer.text)
    if answer.sources:
        print("\nManbalar:", ", ".join(answer.sources))


def cmd_ask(args: argparse.Namespace) -> int:
    _print_answer(_build_tutor(args.sources).ask(args.question))
    return 0


def cmd_chat(args: argparse.Namespace) -> int:
    tutor = _build_tutor(args.sources)
    history: list[dict[str, str]] = []
    print("LexJarvis tayyor. Chiqish uchun 'exit' yozing.")
    while True:
        try:
            question = input("\n> ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return 0
        if question.lower() in {"exit", "quit", "chiqish"}:
            return 0
        if not question:
            continue
        answer = tutor.ask(question, history)
        _print_answer(answer)
        if answer.grounded:  # keep context only for real, source-backed turns
            history += [
                {"role": "user", "content": question},
                {"role": "assistant", "content": answer.text},
            ]
            history = history[-6:]


def cmd_quiz(args: argparse.Namespace) -> int:
    tutor = _build_tutor(args.sources)
    try:
        questions = tutor.quiz(args.topic, args.count)
    except (LookupError, ValueError) as exc:
        print(exc)
        return 1
    score = 0
    for i, q in enumerate(questions, 1):
        print(f"\n{i}. {q.question}")
        for letter, option in zip(LETTERS, q.options):
            print(f"   {letter}) {option}")
        choice = input("Javobingiz (A-D): ").strip().upper()
        if choice == LETTERS[q.answer]:
            score += 1
            print("To'g'ri!")
        else:
            print(f"Noto'g'ri. To'g'ri javob: {LETTERS[q.answer]}")
        print(f"{q.explanation} [{q.source}]")
    print(f"\nNatija: {score}/{len(questions)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="lexjarvis", description="Manbaga asoslangan o'zbekcha yuridik o'quv yordamchisi"
    )
    parser.add_argument("--sources", default="sources", help="manba fayllar papkasi")
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="bitta savol berish")
    ask.add_argument("question")
    ask.set_defaults(func=cmd_ask)

    sub.add_parser("chat", help="suhbat rejimi").set_defaults(func=cmd_chat)

    quiz = sub.add_parser("quiz", help="mavzu bo'yicha test")
    quiz.add_argument("topic")
    quiz.add_argument("-n", "--count", type=int, default=5)
    quiz.set_defaults(func=cmd_quiz)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
