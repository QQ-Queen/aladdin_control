from typing import Tuple
from playwright.sync_api import Browser, Page
from aladdin_auto.aladdinbrowser import AladdinBrowser
from aladdin_auto.config import Config
import time


def _connectToAppBrowser(playwright, port: int, pageURLEnding: str, maxConnectTries: int) -> Tuple[Browser, Page]:
    connectTries = 0
    if maxConnectTries is None:
        maxConnectTries = Config.standaloneStartupSecs()
    connected = False
    page = None
    browser = None
    while connectTries < maxConnectTries and not connected:
        try:
            time.sleep(1)
            browser = playwright.chromium.connect_over_cdp("http://localhost:" + str(port), slow_mo=Config.slowMo())
            default_context = browser.contexts[0]
            page = default_context.pages[0]
            if page.url.endswith(pageURLEnding):
                connected = True
            else:
                browser.close()
                connectTries += 1
        except Exception:
            connectTries += 1
    if not connected:
        raise Exception("Could not connect to Aladdin browser")

    return browser, page

def initPrimaryBrowser(playwright, port: int, pageURLEnding: str) -> Tuple[Browser, Page]:
    """Attach to the primary browser in an already running Aladdin Standalone Application.

    The defaultAladdinBrowser, primaryAladdinStandaloneBrowser, and primaryAladdinStandaloneBrowserDeveloperMode fixtures
    will take care of this step for you.

    :param port: number of port. Should match PrimarySeleniumPort in Aladdin's config.properties
    :param pageURLEnding: Ending of the URL for the primary browser's page (usually 'home')
    :return: tuple of the Playwright browser and current page.
    """
    maxConnectTries = Config.standaloneStartupSecs()
    browser, page = _connectToAppBrowser(playwright, port, pageURLEnding, maxConnectTries)

    # wait for standalone components to display
    print('Waiting for button: Device Detection')
    page.get_by_role("button", name="Device Detection").wait_for()
    print('Found button: Device Detection')
    # wait a second for standalone app to attach events to buttons
    time.sleep(1)

    return browser, page


def initSecondaryBrowser(playwright) -> AladdinBrowser:
    """Attach to the secondary browser in an already running Aladdin Standalone Application. The page must be already open
    when this method is called. Used for controlling pages like the device detection page or the firmware update page.
    """
    maxConnectTries = Config.secondaryBrowserStartupSecs()
    browser, page = _connectToAppBrowser(playwright, Config.secondaryBrowserPort(), "index.html", maxConnectTries)
    return AladdinBrowser(browser, page)


# 
# ThanhNT 
# 

def connectPrimaryBrowser(playwright, port: int, pageURLEnding: str) -> Tuple[Browser, Page]:
    """Attach to the primary browser in an already running Aladdin Standalone Application.

    The defaultAladdinBrowser, primaryAladdinStandaloneBrowser, and primaryAladdinStandaloneBrowserDeveloperMode fixtures
    will take care of this step for you.

    :param port: number of port. Should match PrimarySeleniumPort in Aladdin's config.properties
    :param pageURLEnding: Ending of the URL for the primary browser's page (usually 'home')
    :return: tuple of the Playwright browser and current page.
    """
    maxConnectTries = Config.standaloneStartupSecs()
    browser, page = _connectToAppBrowser(playwright, port, pageURLEnding, maxConnectTries)

    # wait a second for standalone app to attach events to buttons
    time.sleep(1)


    return browser, page