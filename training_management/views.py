from django.http import HttpResponse
from django.shortcuts import render

try:
    # Prefer importing at module load; if transformers missing, our generator handles fallback
    from flashcards import generate_flashcards  # type: ignore
except Exception:  # pragma: no cover
    generate_flashcards = None  # type: ignore

def home(request):
    """Home page view"""
    context = {
        'title': 'Training Management System',
        'description': 'Bienvenue sur votre plateforme de gestion de formations'
    }
    return render(request, 'home.html', context)


def flashcards_generator(request):
    """Simple UI to generate flashcards from lesson text."""
    text = ""
    num_cards = 5
    cards = []

    if request.method == 'POST':
        text = (request.POST.get('text') or '').strip()
        try:
            num_cards = max(1, int(request.POST.get('num_cards') or 5))
        except Exception:
            num_cards = 5

        if generate_flashcards is not None and text:
            try:
                cards = generate_flashcards(text, num_cards)
            except Exception:
                # Soft-fail to empty list; template will show a gentle message
                cards = []

    context = {
        'title': 'Flashcard Generator',
        'text': text,
        'num_cards': num_cards,
        'cards': cards,
    }
    return render(request, 'flashcards/generator.html', context)
