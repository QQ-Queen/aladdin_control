from playwright.sync_api import Browser, Page


class AladdinBrowser:

    _browser = None
    _page = None

    def __init__(self, browser: Browser, page: Page) -> None:
        self._browser = browser
        self._page = page
    
    @property
    def browser(self) -> Browser:
        """
        Return Playwright Browser instance.
        """
        return self._browser

    @property
    def page(self) -> Page:
        """
        Return Playwright Page instance.
        """
        return self._page
