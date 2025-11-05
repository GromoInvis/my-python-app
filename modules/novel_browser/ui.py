from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QPushButton
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import Qt, QUrl, QTimer
from .translator import SafeTranslator
from .adblock import AdBlocker
from PyQt5.QtWidgets import QMessageBox
from .save import save_translated_chapter


class NovelBrowserUI(QWidget):
    def __init__(self):
        super().__init__()
        self._build_ui()
        self.scroll_sync_timer = QTimer(self)
        self.scroll_sync_timer.timeout.connect(self._sync_scroll_loop)
        self.scroll_sync_timer.start(50)  # оновлення 20 разів/сек

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)

        # 🔒 AdBlock
        profile = QWebEngineProfile.defaultProfile()
        ad_domains = ["googlesyndication", "doubleclick", "adservice", "tracking"]
        profile.setUrlRequestInterceptor(AdBlocker(ad_domains))

        # 🌐 Лівий браузер — оригінал
        self.left_browser = QWebEngineView()
        self.left_browser.setUrl(QUrl(
            "https://www.webnovel.com/book/eternally-regressing-knight_33789555708924705"
        ))

        # 🌐 Правий браузер — переклад
        self.right_browser = QWebEngineView()
        self.right_browser.setHtml("<p>Тут з’явиться переклад сторінки…</p>")

        # 🔁 Кнопка перекладу
        self.btn_translate = QPushButton("🔁 Перекласти сторінку")
        self.btn_translate.clicked.connect(self.translate_page)

        self.btn_save = QPushButton("💾 Зберегти переклад")
        self.btn_save.clicked.connect(self.save_translated)


        # Роздільник
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_browser)
        self.splitter.addWidget(self.right_browser)
        self.splitter.setSizes([700, 700])

        layout.addWidget(self.splitter)
        layout.addWidget(self.btn_translate)
        layout.addWidget(self.btn_save)


        # Змінна для синхронізації
        self._last_scroll_ratio = 0.0

    # ──────────────────────────────
    # 🔄 Синхронізація скролу
    # ──────────────────────────────
    def _sync_scroll_loop(self):
        """Зчитує позицію скролу зліва і застосовує її до правого браузера."""
        js = """
        (function(){
            let doc = document.scrollingElement || document.body;
            let top = doc.scrollTop;
            let height = doc.scrollHeight - doc.clientHeight;
            return (height > 0) ? (top / height) : 0;
        })();
        """
        self.left_browser.page().runJavaScript(js, self._apply_right_scroll)

    def _apply_right_scroll(self, ratio):
        """Плавно прокручує правий браузер у тому ж відсотку."""
        if ratio is None or abs(ratio - self._last_scroll_ratio) < 0.001:
            return
        self._last_scroll_ratio = ratio
        js = f"""
        (function(){{
            let doc = document.scrollingElement || document.body;
            let maxScroll = doc.scrollHeight - doc.clientHeight;
            doc.scrollTop = maxScroll * {ratio};
        }})();
        """
        self.right_browser.page().runJavaScript(js)

    # ──────────────────────────────
    # 🌍 Переклад сторінки
    # ──────────────────────────────
    def translate_page(self):
        js = """
        (function() {
            let content = document.querySelector('#chapter-content, .cha-words, .chapter-content, .read-content');
            return content ? content.innerText : document.body.innerText;
        })();
        """
        self.left_browser.page().runJavaScript(js, self._on_text_extracted)

    def _on_text_extracted(self, text):
        if not text or len(text.strip()) < 50:
            self.right_browser.setHtml("<p>⚠️ Не вдалося знайти текст.</p>")
            return

        self.right_browser.setHtml("<p>⏳ Перекладаю, зачекай кілька секунд…</p>")
        QTimer.singleShot(100, lambda: self._translate_and_display(text))

    def _translate_and_display(self, text):
        import html
        from .translator import SafeTranslator

        try:
            translator = SafeTranslator(source="auto", target="uk")
            translated = translator.translate_large_text(text)

            # Розбиваємо на параграфи
            paras = [p.strip() for p in translated.split("\n\n") if p.strip()]
            para_html = ""
            for p in paras:
                safe = html.escape(p).replace("\r", "").replace("\n", "<br>")
                para_html += f"<p>{safe}</p>\n"

            css = """
            body { margin:0; background:#fafafa; color:#222; }
            #translated-root {
                padding-left:25px;
                padding-right:40px;
                font-family:'Georgia','Times New Roman',serif;
                font-size:15px;
                line-height:1.45;
                box-sizing:border-box;
            }
            #translated-root p { margin:0 0 0.9em 0; }
            """

            final_html = f"""
            <!doctype html>
            <html>
            <head><meta charset='utf-8'><style>{css}</style></head>
            <body><div id='translated-root'>{para_html}</div></body>
            </html>
            """

            self.right_browser.setHtml(final_html)
        except Exception as e:
            self.right_browser.setHtml(f"<p>❌ Помилка перекладу або відображення: {html.escape(str(e))}</p>")


    # ──────────────────────────────
    # 💾 Збереження перекладеної глави (оновлено з назвою новели)
    # ──────────────────────────────
    def save_translated(self):
        """Отримує назву новели та заголовок глави перед збереженням."""
        try:
            # Спочатку беремо назву книги (зверху сторінки або з title)
            js_novel = "(document.querySelector('.novel-title, .book-title, h1, h2')?.innerText || document.title || 'Без назви');"
            self.left_browser.page().runJavaScript(js_novel, self._save_with_novel_title)
        except Exception as e:
            from PyQt5.QtWidgets import QMessageBox
            QMessageBox.critical(self, "Помилка", f"Не вдалося отримати назву новели: {e}")

    def _save_with_novel_title(self, novel_title):
        if not novel_title or len(novel_title.strip()) < 2:
            novel_title = "Невідома новела"

        # Потім отримуємо назву поточної глави
        js_chapter = "(document.querySelector('h1.chapter-title, .chapter-name, h2')?.innerText || 'Без назви глави');"
        self.left_browser.page().runJavaScript(
            js_chapter,
            lambda chapter_title: self._save_with_titles(novel_title, chapter_title)
        )

    def _save_with_titles(self, novel_title, chapter_title):
        """Після отримання назв — дістаємо текст перекладу."""
        js = "document.body.innerText || document.documentElement.innerText;"
        self.right_browser.page().runJavaScript(
            js,
            lambda text: self._write_docx(novel_title, chapter_title, text)
        )

    def _write_docx(self, novel_title, chapter_title, text):
        """Фактичне створення .docx через save_translated_chapter."""
        from PyQt5.QtWidgets import QMessageBox
        from .save import save_translated_chapter

        if not text or len(text.strip()) < 10:
            QMessageBox.warning(self, "Порожньо", "Немає перекладеного тексту для збереження.")
            return

        try:
            path = save_translated_chapter(novel_title, chapter_title, text)
            QMessageBox.information(
                self, "✅ Збережено",
                f"Файл збережено:\n{path}"
            )
        except Exception as e:
            QMessageBox.critical(self, "❌ Помилка", f"Не вдалося зберегти:\n{e}")




