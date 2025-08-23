from __future__ import annotations

import os
from dataclasses import dataclass
from typing import List, Dict

# Lazy import to keep startup light and allow heuristic fallback
try:
    from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM  # type: ignore
except Exception:  # pragma: no cover - optional dependency during tests
    pipeline = None  # type: ignore
    AutoTokenizer = None  # type: ignore
    AutoModelForSeq2SeqLM = None  # type: ignore


@dataclass
class Flashcard:
    question: str
    answer: str


def _split_sentences(text: str) -> List[str]:
    # Very light sentence splitter (avoid heavy deps)
    parts = []
    buf = []
    for ch in text.strip():
        buf.append(ch)
        if ch in ".!?" and (len(buf) > 2):
            seg = "".join(buf).strip()
            if seg:
                parts.append(seg)
            buf = []
    if buf:
        seg = "".join(buf).strip()
        if seg:
            parts.append(seg)
    return parts


def _heuristic_cards(text: str, num_cards: int) -> List[Flashcard]:
    sentences = _split_sentences(text) or [text.strip()]
    cards: List[Flashcard] = []
    for i, sent in enumerate(sentences[: num_cards]):
        # Build a simple who/what/where prompt from the sentence
        snippet = sent.strip().rstrip(".?!")
        if len(snippet) > 120:
            snippet = snippet[:117].rsplit(" ", 1)[0] + "…"
        q = f"What is the key idea in: '{snippet}'?"
        a = sent.strip()
        cards.append(Flashcard(question=q, answer=a))
    # Pad if needed
    while len(cards) < num_cards and cards:
        cards.append(cards[len(cards) % len(cards)])
    return cards[:num_cards]


def generate_flashcards(text: str, num_cards: int = 5) -> List[Dict[str, str]]:
    """
    Generate concise flashcards from a lesson text.

    Contract
    - Input: text (str), num_cards (int, default 5, >0)
    - Output: list of dicts: {"question": str, "answer": str}
    - Questions short, answerable in one sentence
    - Falls back to heuristics if transformers or model unavailable
    """
    text = (text or "").strip()
    if not text:
        return []
    num_cards = max(1, int(num_cards or 1))

    # If transformers pipeline is available, try T5 for QG; else fallback
    if pipeline is None or AutoTokenizer is None or AutoModelForSeq2SeqLM is None:
        return [fc.__dict__ for fc in _heuristic_cards(text, num_cards)]

    def _build_generator(local_only: bool):
        tok = AutoTokenizer.from_pretrained("t5-small", local_files_only=local_only)
        mdl = AutoModelForSeq2SeqLM.from_pretrained("t5-small", local_files_only=local_only)
        return pipeline("text2text-generation", model=mdl, tokenizer=tok)

    # Try local cache first to avoid blocking downloads during a web request
    generator = None
    try:
        generator = _build_generator(local_only=True)
    except Exception:
        # Only allow network download if explicitly opted-in
        if os.getenv("FLASHCARDS_ALLOW_DOWNLOAD", "0") == "1":
            try:
                generator = _build_generator(local_only=False)
            except Exception:
                generator = None
        else:
            generator = None

    if generator is None:
        return [fc.__dict__ for fc in _heuristic_cards(text, num_cards)]

    sentences = _split_sentences(text)
    if not sentences:
        sentences = [text]

    outputs: List[Flashcard] = []
    for sent in sentences[: num_cards]:
        prompt = f"generate a short question that can be answered in one sentence about: {sent}"
        try:
            # Slightly lighter decoding for faster responses
            gen = generator(prompt, max_new_tokens=24, num_beams=2, do_sample=False)
            question_raw = gen[0]["generated_text"].strip()
        except Exception:
            question_raw = "What is the key idea in this sentence?"
        # Basic cleanup for T5 outputs
        question = question_raw.rstrip(" .?") + "?"
        answer = sent.strip()
        outputs.append(Flashcard(question=question, answer=answer))

    if not outputs:
        outputs = _heuristic_cards(text, num_cards)

    return [fc.__dict__ for fc in outputs[: num_cards]]
