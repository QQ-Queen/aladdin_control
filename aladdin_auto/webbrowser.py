"""
This module contains methods related to connecting to Aladdin through a web browser.
It is recommended that you use the defaultAladdinBrowser fixture instead of using these methods directly.
"""
from typing import Tuple, List
from playwright.sync_api import Browser, Page
from aladdin_auto.config import Config


def connectToWebBrowser(playwright, url: str, launchArgs: List[str]) -> Tuple[Browser, Page]:
    """

    :param url: url to connect to
    :param launchArgs: arguments to launch chromium with
    :return: tuple of Playwright browser and page
    :meta private:
    """
    chromium = playwright.chromium
    browser = chromium.launch(headless=Config.headless(), slow_mo=Config.slowMo(), args=launchArgs)
    page = browser.new_page()
    page.goto(url)
    return browser, page
