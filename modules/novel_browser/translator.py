import re
import time
from deep_translator import GoogleTranslator


class SafeTranslator:
    """Перекладає великі тексти гарантовано повністю, з розбиттям на блоки."""
    def __init__(self, source="auto", target="uk", delay=0.4):
        self.translator = GoogleTranslator(source=source, target=target)
        self.delay = delay

    def _split_text(self, text: str, max_len=4500):
        sentences = re.split(r'(?<=[.!?]) +', text)
        chunks, current = [], ""
        for s in sentences:
            if len(current) + len(s) + 1 < max_len:
                current += s + " "
            else:
                chunks.append(current.strip())
                current = s + " "
        if current.strip():
            chunks.append(current.strip())
        return chunks

    def translate_large_text(self, text):
        chunks = self._split_text(text)
        result_parts = []
        for i, chunk in enumerate(chunks, 1):
            try:
                translated = self.translator.translate(chunk)
                result_parts.append(translated)
            except Exception as e:
                result_parts.append(f"[❌ Помилка в частині {i}: {e}]")
            time.sleep(self.delay)
        return "\n".join(result_parts)
