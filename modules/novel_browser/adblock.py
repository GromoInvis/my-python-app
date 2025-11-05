from PyQt5.QtWebEngineCore import QWebEngineUrlRequestInterceptor


class AdBlocker(QWebEngineUrlRequestInterceptor):
    """Блокує запити до рекламних і трекінгових доменів."""
    def __init__(self, blocked_domains):
        super().__init__()
        self.blocked_domains = blocked_domains

    def interceptRequest(self, info):
        url = info.requestUrl().toString()
        for domain in self.blocked_domains:
            if domain in url:
                info.block(True)
                return
