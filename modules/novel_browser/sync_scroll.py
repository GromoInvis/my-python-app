from PyQt5.QtCore import QObject, pyqtSignal, QEvent


class SyncScroll(QObject):
    """Зв’язує прокрутку між двома QWebEngineView."""
    scroll_changed = pyqtSignal(float)

    def __init__(self, left_browser, right_browser):
        super().__init__()
        self.left_browser = left_browser
        self.right_browser = right_browser
        self.scroll_changed.connect(self._on_scroll_changed)

    def link_scrollbars(self):
        """Активує синхронізацію між двома браузерами."""
        self.left_browser.installEventFilter(self)
        self.right_browser.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.Wheel:
            delta = event.angleDelta().y()
            target = self.right_browser if obj == self.left_browser else self.left_browser
            script = f"""
            let doc = document.scrollingElement || document.body;
            doc.scrollTop = doc.scrollTop - {delta};
            """
            target.page().runJavaScript(script)
        return False

    def _on_scroll_changed(self, ratio):
        js = f"""
        let doc = document.scrollingElement || document.body;
        let maxScroll = doc.scrollHeight - doc.clientHeight;
        doc.scrollTop = maxScroll * {ratio};
        """
        self.right_browser.page().runJavaScript(js)
