from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = "Pre-download and cache the T5 model for flashcard generation so first request is fast."

    def handle(self, *args, **options):
        try:
            from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Transformers not available: {e}"))
            return
        try:
            self.stdout.write("Downloading t5-small tokenizer...")
            AutoTokenizer.from_pretrained("t5-small")
            self.stdout.write(self.style.SUCCESS("Tokenizer cached."))
            self.stdout.write("Downloading t5-small model (this may take a minute)...")
            AutoModelForSeq2SeqLM.from_pretrained("t5-small")
            self.stdout.write(self.style.SUCCESS("Model cached."))
            self.stdout.write(self.style.SUCCESS("Flashcards model prewarmed successfully."))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Prewarm failed: {e}"))
