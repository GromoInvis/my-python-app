import os
import re
import html
from datetime import datetime
from docx import Document
from docx.shared import Pt


def _safe_filename(name: str) -> str:
    """Очищає назву файлу від заборонених символів."""
    safe = re.sub(r'[<>:"/\\|?*\x00-\x1F]', "_", name).strip()
    return safe or "chapter"


def save_translated_chapter(novel_name: str, chapter_title: str, text: str) -> str:
    """
    Зберігає перекладену главу у форматі .docx у теку 'saved_novels'.
    Назва файлу: <novel_name> - <chapter_title>_<дата>.docx
    """
    folder = os.path.join(os.getcwd(), "saved_novels")
    os.makedirs(folder, exist_ok=True)

    # Формування назви файлу
    full_title = f"{novel_name.strip()} - {chapter_title.strip()}"
    filename = f"{_safe_filename(full_title)}_{datetime.now().strftime('%Y-%m-%d_%H-%M')}.docx"
    path = os.path.join(folder, filename)

    # Створення документа
    doc = Document()
    doc.add_heading(full_title, level=1)
    doc.add_paragraph(f"Збережено: {datetime.now().strftime('%d.%m.%Y %H:%M')}")
    doc.add_paragraph("")

    # Основний текст
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    style = doc.styles['Normal']
    style.font.name = 'Times New Roman'
    style.font.size = Pt(12)

    for p in paragraphs:
        doc.add_paragraph(p)

    doc.save(path)
    return path
