"""
Novel Browser Module for the modular Python GUI app

Features:
- Left pane: original (English) text
- Right pane: translated (Ukrainian) text
- URL input + Fetch button (accepts chapter URLs from WebNovel and similar sites)
- Paste fallback if the site blocks scraping (common on WebNovel)
- Translation using (in order of preference):
    1) Argos Translate (offline) if installed and model exists
    2) deep_translator.GoogleTranslator (requires internet)

Integration:
- This file exposes a Tkinter Frame subclass `NovelBrowserModule` that can be embedded into the main application's module-area.

Requirements (install as needed):
pip install requests beautifulsoup4 deep-translator argostranslate

Notes about WebNovel: many pages are behind JS or login; if `fetch` fails, copy the chapter text manually and click "Translate".

"""

import threading
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import requests
from bs4 import BeautifulSoup

# Try to import translation backends
_argos_available = False
_deep_available = False
try:
    import argostranslate.package
    import argostranslate.translate
    _argos_available = True
except Exception:
    _argos_available = False

try:
    from deep_translator import GoogleTranslator
    _deep_available = True
except Exception:
    _deep_available = False


class NovelBrowserModule(tk.Frame):
    """Tkinter Frame: left original text, right translated text."""

    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._build_ui()

    def _build_ui(self):
        # Top controls
        topbar = ttk.Frame(self)
        topbar.pack(fill='x', padx=6, pady=6)

        ttk.Label(topbar, text='Chapter URL or paste here:').pack(side='left')
        self.url_var = tk.StringVar()
        url_entry = ttk.Entry(topbar, textvariable=self.url_var, width=60)
        url_entry.pack(side='left', padx=6)
        ttk.Button(topbar, text='Fetch', command=self._on_fetch).pack(side='left')
        ttk.Button(topbar, text='Paste text', command=self._on_paste).pack(side='left', padx=4)
        ttk.Button(topbar, text='Save', command=self._on_save).pack(side='left')

        # Middle split panes
        panes = ttk.Panedwindow(self, orient='horizontal')
        panes.pack(fill='both', expand=True, padx=6, pady=6)

        # Left original
        left_frame = ttk.Frame(panes)
        self.left_text = tk.Text(left_frame, wrap='word')
        left_scroll = ttk.Scrollbar(left_frame, command=self.left_text.yview)
        self.left_text.configure(yscrollcommand=left_scroll.set)
        self.left_text.pack(side='left', fill='both', expand=True)
        left_scroll.pack(side='right', fill='y')
        panes.add(left_frame, weight=1)

        # Right translation
        right_frame = ttk.Frame(panes)
        self.right_text = tk.Text(right_frame, wrap='word')
        right_scroll = ttk.Scrollbar(right_frame, command=self.right_text.yview)
        self.right_text.configure(yscrollcommand=right_scroll.set)
        self.right_text.pack(side='left', fill='both', expand=True)
        right_scroll.pack(side='right', fill='y')
        panes.add(right_frame, weight=1)

        # Bottom controls
        bottombar = ttk.Frame(self)
        bottombar.pack(fill='x', padx=6, pady=(0,6))
        self.auto_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(bottombar, text='Auto-translate after fetch', variable=self.auto_var).pack(side='left')
        ttk.Button(bottombar, text='Translate', command=self._on_translate).pack(side='left', padx=6)

        # Info label
        info = 'Translation backends: '
        if _argos_available:
            info += 'Argos(offline) '
        if _deep_available:
            info += 'deep_translator '
        if not (_argos_available or _deep_available):
            info += 'None - install argostranslate or deep-translator'
        ttk.Label(bottombar, text=info).pack(side='right')

    def _on_paste(self):
        # paste from clipboard into left pane
        try:
            txt = self.clipboard_get()
        except Exception:
            txt = ''
        if not txt:
            messagebox.showinfo('Paste', 'Clipboard empty or not available. You can paste manually into the left pane.')
        else:
            self.left_text.delete('1.0', 'end')
            self.left_text.insert('1.0', txt)

    def _on_save(self):
        content = self.left_text.get('1.0', 'end').strip()
        if not content:
            messagebox.showwarning('Save', 'No original text to save.')
            return
        path = filedialog.asksaveasfilename(defaultextension='.txt', filetypes=[('Text','*.txt')])
        if path:
            with open(path, 'w', encoding='utf-8') as f:
                f.write('--- ORIGINAL ---\n')
                f.write(content + '\n\n')
                f.write('--- TRANSLATION ---\n')
                f.write(self.right_text.get('1.0', 'end'))
            messagebox.showinfo('Save', f'Saved to {path}')

    def _on_fetch(self):
        url = self.url_var.get().strip()
        if not url:
            messagebox.showwarning('Fetch', 'Enter a chapter URL or paste text.')
            return
        threading.Thread(target=self._fetch_thread, args=(url,), daemon=True).start()

    def _fetch_thread(self, url):
        self._set_status('Fetching...')
        try:
            headers = {'User-Agent': 'novel-browser/1.0'}
            r = requests.get(url, headers=headers, timeout=15)
            r.raise_for_status()
            soup = BeautifulSoup(r.text, 'html.parser')

            # heuristics: search common containers used by novel sites
            selectors = [
                'div#chapterContent',
                'div.chapter-content',
                'div.read-content',
                'div[class*="cha-words"]',
                'div[class*="content"]',
                'article'
            ]
            text = None
            for sel in selectors:
                el = soup.select_one(sel)
                if el and el.get_text(strip=True):
                    text = el.get_text('\n')
                    break
            # fallback: find the longest <p> aggregate
            if not text:
                ps = soup.find_all('p')
                if ps:
                    longest = max(ps, key=lambda p: len(p.get_text()))
                    text = longest.get_text('\n')

            if not text or len(text.strip()) < 30:
                # probably blocked by JS/login
                self._set_status('Fetch likely blocked (JS/login). Paste text manually or copy chapter HTML.')
                messagebox.showinfo('Fetch', 'Could not extract chapter content automatically (site may require login/JS). Please paste the chapter text into the left pane manually.')
                return

            # insert into left pane
            self.left_text.delete('1.0', 'end')
            self.left_text.insert('1.0', text)
            self._set_status('Fetched content.')

            if self.auto_var.get():
                self._on_translate()

        except Exception as e:
            self._set_status(f'Fetch error: {e}')
            messagebox.showerror('Fetch error', str(e))

    def _on_translate(self):
        text = self.left_text.get('1.0', 'end').strip()
        if not text:
            messagebox.showwarning('Translate', 'No text to translate.')
            return
        threading.Thread(target=self._translate_thread, args=(text,), daemon=True).start()

    def _translate_thread(self, text):
        self._set_status('Translating...')
        translated = None
        try:
            # Prefer Argos Translate (offline) if available
            if _argos_available:
                try:
                    # Attempt to translate using installed Argos models
                    from argostranslate import translate as argotrans
                    # argostranslate.translate.translate(text, from_code, to_code) can be used
                    # But API may vary; using argostranslate.translate.translate
                    translated = argostranslate.translate.translate(text, 'en', 'uk')
                except Exception:
                    translated = None

            if translated is None and _deep_available:
                try:
                    translated = GoogleTranslator(source='en', target='uk').translate(text)
                except Exception:
                    translated = None

            if translated is None:
                # last resort: naive sentence-by-sentence split and return the original with markers
                translated = '\n'.join(['[translation unavailable] ' + line for line in text.splitlines()])

            # put result into right pane
            self.right_text.delete('1.0', 'end')
            self.right_text.insert('1.0', translated)
            self._set_status('Translation done.')
        except Exception as e:
            self._set_status(f'Translation error: {e}')
            messagebox.showerror('Translate error', str(e))

    def _set_status(self, txt):
        # temporary: show as window title if available
        try:
            root = self.winfo_toplevel()
            root.title(f'Novel Browser — {txt}')
        except Exception:
            pass


# Quick demo runner if this file is executed directly
if __name__ == '__main__':
    root = tk.Tk()
    root.geometry('1000x700')
    frame = NovelBrowserModule(root)
    frame.pack(fill='both', expand=True)
    root.mainloop()
