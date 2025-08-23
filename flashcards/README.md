# Flashcards

Simple flashcard generator using Hugging Face Transformers (t5-small) with a safe heuristic fallback.

## Usage

```python
from flashcards import generate_flashcards

text = "The mitochondria is the powerhouse of the cell. It produces energy in the form of ATP."
cards = generate_flashcards(text, num_cards=5)
for c in cards:
    print(c)
```

Output shape:

```json
{"question": "...", "answer": "..."}
```

Notes:
- If `transformers` or model download is unavailable, a heuristic fallback produces concise question/answer pairs.
- For deterministic CI/tests, you can rely on the fallback by not installing model weights.
