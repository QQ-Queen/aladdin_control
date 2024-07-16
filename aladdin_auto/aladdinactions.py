from aladdin_auto.parameter import Parameter
from aladdin_auto.productxml import ProductXML
from playwright.sync_api import expect, Page
import time

def selectDeviceFromHomePageWithSearch(page: Page, deviceName: str):
    """
    Use Playwright to search for a device and select it from the Aladdin home page.

    :param page: Playwright page to click from
    :param deviceName: name of device
    """
    searchBox = page.locator("xpath=//*[@id=\"frm-search\"]/input")
    searchBox.click()
    searchBox.fill(deviceName)
    page.get_by_role("link", name=deviceName).first.click()

def selectRelease(page: Page, releaseNumber: str):
    """
    Use Playwright to select a release number from the product page in Aladdin.

    :param page: Playwright page to click from
    :param releaseNumber: release number
    """
    releaseSelection = page.locator("xpath=//*[@id=\"release\"]/descendant::select")
    releaseSelection.select_option(releaseNumber)

def selectDeviceAndReleaseFromHomePage(page: Page, xml: ProductXML):
    """
    Use Playwright to search for a device and select a release number from the home page in Aladdin.
    Also checks that these steps happened correctly before moving on.

    :param page: Playwright page
    :param xml: ProductXML object to search for
    """
    selectDeviceFromHomePageWithSearch(page, xml.menuProductName)
    # check for product tab (if we don't do this, it will move too quickly and the release selection won't take effect).
    productTab = page.locator("li").get_by_text(xml.menuProductName)
    expect(productTab).to_be_visible()
    # select the release
    if xml.mcf is None:
        selectRelease(page, xml.releaseNumber)
    else:
        selectRelease(page, f"{xml.releaseNumber} (MCF: {xml.mcf})")
    # check for correct number of top level pages (if we skip this, could search before pages have loaded)
    topLevelPages = page.locator("app-param-section")
    expect(topLevelPages).to_have_count(count=len(xml.getAllUserTopLevelPages()))

def _waitForAttribute(page, locator, attribute, attributeExpectedValue, timeout):
    """
    Wait until attribute of element is equal to a certain value (or timeout)

    :param page: Playwright page
    :param locator: Playwright locator for element
    :param attribute: Name of attribute
    :param attributeExpectedValue: Expected value of attribute
    :param timeout: Timeout in seconds
    :return: True if expected attribute found, False if timed out
    """
    startTime = time.time()
    attributeValue = None
    attributeValue = locator.get_attribute(attribute)
    while attributeExpectedValue != attributeValue and time.time()-startTime < timeout:
        page.wait_for_timeout(100)
        attributeValue = locator.get_attribute(attribute)
    if attributeExpectedValue == attributeValue:
        return True
    else:
        return False

def searchForParameterByCode(page: Page, param: Parameter):
    """
    Use Playwright to use the search bar to navigate to a particular parameter from the product page in Aladdin.

    :param page: Playwright page to click from
    :param param: Parameter to navigate to
    """
    searchArea = page.locator("xpath=//form[@id='frm-search']")
    searchBar = searchArea.locator("xpath=//input[@name='searchValue']")
    searchBar.type(param.code)
    searchResult = searchArea.locator("xpath=//div[@class='result']")
    searchResult.first.click()


def selectPageForParameter(page: Page, param: Parameter):
    """
    Use Playwright to select the page for the given parameter from the product page in Aladdin.

    :param page: Playwright page to click from
    :param param: Parameter to navigate to
    """
    topLevelPageName = None
    startIndex = 0
    if len(param.parentPageTitles) > 0:
        startIndex += 1
        if "2D Imager Scanner" == param.parentPageTitles[0]:
            if len(param.parentPageTitles) > 1:
                topLevelPageName = param.parentPageTitles[1]
                startIndex += 1
        else:
            topLevelPageName = param.parentPageTitles[0]
    else:
        raise ValueError("Length of param.parentPageTitles is zero")

    topLevelSection = page.locator("app-param-section").filter(has_text=topLevelPageName)
    topLevelButton = topLevelSection.locator("button")
    # click top level page if top level page needs to be expanded, or if top level page is the final page
    if topLevelButton.get_attribute("aria-expanded") != "true" or startIndex == len(param.parentPageTitles):
        topLevelButton.click()
        if not _waitForAttribute(page, topLevelButton, "aria-expanded", "true", 5):  # make sure first click worked. If not, click again.
            topLevelButton.click()

    for buttonName in param.parentPageTitles[startIndex:-1]:
        paramPage = topLevelSection.locator(
            f"xpath=//div[contains(@class, 'tree-node') and starts-with(., '{buttonName}')]")
        if "tree-node-collapsed" in paramPage.get_attribute("class"):
            expander = paramPage.locator("tree-node-expander")
            expander.click()

    if startIndex < len(param.parentPageTitles):  # then top level page is not the final page
        finalPage = topLevelSection.locator("tree-node-wrapper").get_by_text(param.parentPageTitles[-1], exact=True)
        finalPage.click()

# 
# ThanhNT
# 

def clickButton(page: Page, param: Parameter):
    pass