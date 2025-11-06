# modules/novel_browser/ui.py
import html
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QSplitter, QPushButton, QMessageBox
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineProfile
from PyQt5.QtCore import Qt, QUrl, QTimer
from .translator import SafeTranslator
from .adblock import AdBlocker
from .save import save_translated_chapter
from bs4 import BeautifulSoup  # 👈 НОВИЙ ІМПОРТ


class NovelBrowserUI(QWidget):
    def __init__(self):
        super().__init__()
        self.current_theme = "light"  # 👈 НОВЕ: Зберігаємо поточну тему
        self._build_ui()
        self.scroll_sync_timer = QTimer(self)
        self.scroll_sync_timer.timeout.connect(self._sync_scroll_loop)

    def _build_ui(self):
        # ... (код _build_ui без змін, я його приховав для стислості) ...
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        profile = QWebEngineProfile.defaultProfile()
        ad_domains = ["googlesyndication", "doubleclick", "adservice", "tracking"]
        profile.setUrlRequestInterceptor(AdBlocker(ad_domains))
        self.left_browser = QWebEngineView()
        self.left_browser.setUrl(QUrl(
            "https://www.webnovel.com/book/eternally-regressing-knight_33789555708924705"
        ))
        self.right_browser = QWebEngineView()
        self.right_browser.setHtml("<p>Тут з’явиться переклад сторінки…</p>")
        self.btn_translate = QPushButton("🔁 Перекласти сторінку")
        self.btn_translate.clicked.connect(self.translate_page)
        self.btn_save = QPushButton("💾 Зберегти переклад")
        self.btn_save.clicked.connect(self.save_translated)
        self.splitter = QSplitter(Qt.Horizontal)
        self.splitter.addWidget(self.left_browser)
        self.splitter.addWidget(self.right_browser)
        self.splitter.setSizes([700, 700])
        layout.addWidget(self.splitter)
        layout.addWidget(self.btn_translate)
        layout.addWidget(self.btn_save)
        self._last_scroll_ratio = 0.0
        # ... (кінець _build_ui) ...

    # ──────────────────────────────
    # ⏯️ Керування таймером (без змін)
    # ──────────────────────────────
    def pause_sync(self):
        self.scroll_sync_timer.stop()

    def resume_sync(self):
        self.scroll_sync_timer.start(50)

    def cleanup(self):
        print(f"🧹 Очищення {self.__class__.__name__}...")
        self.pause_sync()
        if self.left_browser:
            self.left_browser.page().deleteLater()
            self.left_browser.deleteLater()
            self.left_browser = None
        if self.right_browser:
            self.right_browser.page().deleteLater()
            self.right_browser.deleteLater()
            self.right_browser = None

    # ──────────────────────────────
    # 🔄 Синхронізація скролу (без змін)
    # ──────────────────────────────
    def _sync_scroll_loop(self):
        if not self.left_browser: return
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
        """Smoothly scrolls the right browser to the same percentage."""
        if ratio is None or abs(ratio - self._last_scroll_ratio) < 0.001:
            return
        if not self.right_browser: # Check added
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
    # 🎨 Керування темою (НОВІ МЕТОДИ)
    # ──────────────────────────────
    def apply_theme(self, theme_name: str):
        """Отримує сигнал про зміну теми від wrapper'а."""
        self.current_theme = theme_name
        self._update_theme_css()

    def _get_theme_css(self) -> str:
        """Повертає CSS-рядок для поточної теми."""
        # 🎨 Тут можна налаштувати шрифти, кольори тощо.
        font_family = "'Georgia', 'Times New Roman', serif"
        font_size = "16px"
        line_height = "1.5"

        if self.current_theme == 'dark':
            return f"""
            body {{ margin:0; background:#1e1e1e; color:#ddd; }}
            #translated-root {{
                padding: 10px 25px;
                font-family: {font_family};
                font-size: {font_size};
                line-height: {line_height};
                box-sizing: border-box;
            }}
            #translated-root p {{ margin:0 0 1em 0; }}
            #translated-root img {{ max-width: 90%; height: auto; display: block; margin: 1em auto; border-radius: 4px; }}
            """
        else:  # 'light'
            return f"""
            body {{ margin:0; background:#fafafa; color:#222; }}
            #translated-root {{
                padding: 10px 25px;
                font-family: {font_family};
                font-size: {font_size};
                line-height: {line_height};
                box-sizing: border-box;
            }}
            #translated-root p {{ margin:0 0 1em 0; }}
            #translated-root img {{ max-width: 90%; height: auto; display: block; margin: 1em auto; border-radius: 4px; }}
            """

    def _update_theme_css(self):
        """Динамічно оновлює CSS у вже завантаженому правому браузері."""
        if not self.right_browser: return
        css = self._get_theme_css()
        # 'js-beautify' вимагає екранування рядків для ін'єкції
        js_safe_css = css.replace('\\', '\\\\').replace('`', '\\`').replace('$', '\\$')
        js = f"""
        let style = document.getElementById('theme-style');
        if (!style) {{
            style = document.createElement('style');
            style.id = 'theme-style';
            document.head.appendChild(style);
        }}
        style.innerHTML = `{js_safe_css}`;
        """
        self.right_browser.page().runJavaScript(js)


    # ──────────────────────────────
    # 🌍 Переклад сторінки (ПОВНІСТЮ ПЕРЕПИСАНО)
    # ──────────────────────────────
    
    def translate_page(self):
        """Крок 1: Отримуємо HTML контенту, а не просто текст."""
        if not self.left_browser: return
        js = """
        (function() {
            let content = document.querySelector('#chapter-content, .cha-words, .chapter-content, .read-content');
            return content ? content.innerHTML : document.body.innerHTML;
        })();
        """
        # Викликаємо новий обробник
        self.left_browser.page().runJavaScript(js, self._on_html_extracted)

    def _on_html_extracted(self, html_content: str):
        """Крок 2: Отримали HTML, показуємо статус і запускаємо обробку."""
        if not self.right_browser: return
        
        if not html_content or len(html_content.strip()) < 50:
            self.right_browser.setHtml("<p>⚠️ Не вдалося знайти HTML контент.</p>")
            return

        self.right_browser.setHtml("<p>⏳ Обробляю HTML та перекладаю... (це може зайняти час)</p>")
        # Використовуємо QTimer, щоб не "вішати" UI
        QTimer.singleShot(100, lambda: self._translate_html_content(html_content))

    def _translate_html_content(self, html_content: str):
        """
        Крок 3: Найскладніший. Парсимо HTML, витягуємо текст,
        перекладаємо і збираємо HTML назад.
        """
        if not self.right_browser: return

        try:
            # 1. Парсимо HTML
            try:
                soup = BeautifulSoup(html_content, 'lxml')
            except Exception:
                soup = BeautifulSoup(html_content, 'html.parser')

            # 2. Знаходимо ВСІ текстові вузли, які варто перекладати
            texts_to_translate = [] # Рядки для перекладача
            text_nodes = []         # Посилання на вузли в 'soup'
            
            for node in soup.find_all(string=True):
                # Ігноруємо текст у <script>, <style> та порожні рядки
                if node.parent.name in ['script', 'style', 'head', 'title', 'a']:
                    continue
                text = node.string.strip()
                if text:
                    texts_to_translate.append(text)
                    text_nodes.append(node)
            
            if not texts_to_translate:
                # Це може статися, якщо весь контент - лише картинки
                self.right_browser.setHtml(str(soup))
                self._update_theme_css() # Застосовуємо тему
                return
            
            # 3. Об'єднуємо текст в один великий блок для SafeTranslator
            # Використовуємо унікальний роздільник, який перекладач не повинен змінити
            SEPARATOR = "\n<br_sep>\n"
            full_text = SEPARATOR.join(texts_to_translate)

            # 4. Перекладаємо
            translator = SafeTranslator(source="auto", target="uk")
            translated_full_text = translator.translate_large_text(full_text)
            
            # 5. Розбиваємо переклад назад на шматки
            translated_chunks = translated_full_text.split(SEPARATOR)
            
            # 6. Перевірка, чи все збігається
            if len(translated_chunks) != len(text_nodes):
                print(f"⚠️ Помилка збігу: {len(text_nodes)} вузлів != {len(translated_chunks)} перекладів.")
                # Якщо щось пішло не так - просто показуємо суцільний переклад
                self._fallback_to_plain_text(soup)
                return

            # 7. Замінюємо старий текст на новий прямо в 'soup'
            for node, translated_text in zip(text_nodes, translated_chunks):
                node.string.replace_with(translated_text)
            
            # 8. Отримуємо CSS для теми
            css = self._get_theme_css()

            # 9. Формуємо кінцевий HTML
            # 'str(soup)' - це наш HTML зі збереженими <img> і перекладеним текстом
            final_html = f"""
            <!doctype html>
            <html>
            <head>
                <meta charset='utf-8'>
                <style id='theme-style'>{css}</style>
            </head>
            <body>
                <div id='translated-root'>{str(soup)}</div>
            </body>
            </html>
            """
            self.right_browser.setHtml(final_html)

        except Exception as e:
            print(f"❌ Помилка перекладу HTML: {e}. Повертаюсь до старого методу.")
            # План Б: якщо розбір HTML не вдався, повертаємось до старого методу (лише текст)
            self._fallback_to_plain_text(BeautifulSoup(html_content, 'html.parser'))

    def _fallback_to_plain_text(self, soup: BeautifulSoup):
        """План Б: Старий метод (показати лише текст), але з підтримкою тем."""
        
        text = soup.get_text() # Отримуємо весь текст без HTML
        
        try:
            translator = SafeTranslator(source="auto", target="uk")
            translated = translator.translate_large_text(text)

            paras = [p.strip() for p in translated.split("\n\n") if p.strip()]
            para_html = ""
            for p in paras:
                safe = html.escape(p).replace("\r", "").replace("\n", "<br>")
                para_html += f"<p>{safe}</p>\n"

            css = self._get_theme_css() # <-- Використовуємо CSS з теми

            final_html = f"""
            <!doctype html>
            <html>
            <head><meta charset='utf-8'><style id='theme-style'>{css}</style></head>
            <body><div id='translated-root'>{para_html}</div></body>
            </html>
            """
            self.right_browser.setHtml(final_html)
        except Exception as e:
            self.right_browser.setHtml(f"<p>❌ Помилка резервного перекладу: {html.escape(str(e))}</p>")


    # ──────────────────────────────
    # 💾 Збереження (без змін)
    # ──────────────────────────────
    def save_translated(self):
        if not self.left_browser: return
        js_novel = "(document.querySelector('.j_book_name') && document.querySelector('.j_book_name').innerText) || 'Без назви';"
        self.left_browser.page().runJavaScript(js_novel, self._save_with_novel_title)

    def _save_with_novel_title(self, novel_title):
        if not self.left_browser: return
        if not novel_title or len(novel_title.strip()) < 2: novel_title = "Невідома новела"
        js_chapter = "(document.querySelector('h3.cha-tit') && document.querySelector('h3.cha-tit').innerText) || 'Без назви глави';"
        self.left_browser.page().runJavaScript(js_chapter, lambda ct: self._save_with_titles(novel_title, ct))

    def _save_with_titles(self, novel_title, chapter_title):
        if not self.right_browser: return
        # Отримуємо текст з нашого 'translated-root'
        js = "document.getElementById('translated-root').innerText || document.body.innerText;"
        self.right_browser.page().runJavaScript(js, lambda text: self._write_docx(novel_title, chapter_title, text))

    def _write_docx(self, novel_title, chapter_title, text):
        if not text or len(text.strip()) < 10:
            QMessageBox.warning(self, "Порожньо", "Немає перекладеного тексту.")
            return
        try:
            path = save_translated_chapter(novel_title, chapter_title, text)
            QMessageBox.information(self, "✅ Збережено", f"Файл збережено:\n{path}")
        except Exception as e:
            QMessageBox.critical(self, "❌ Помилка", f"Не вдалося зберегти:\n{e}")