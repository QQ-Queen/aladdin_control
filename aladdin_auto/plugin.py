"""
This module contains fixtures that can be used to set up/tear down the Aladdin Web Application for running Playwright tests.
The fixtures that are most likely to be needed for tests are defaultAladdinBrowser, primaryAladdinStandaloneBrowser, and primaryAladdinStandaloneBrowserDeveloperMode.
"""
import pytest
import subprocess
import os
import math
import easygui
from datetime import datetime
from aladdin_auto.standaloneappbrowser import *
from aladdin_auto.webbrowser import *
from aladdin_auto.fileutils import FileUtils
from aladdin_auto.config import Config, AladdinBrowserType
from pytest import StashKey, CollectReport
from typing import Dict

phase_report_key = StashKey[Dict[str, CollectReport]]()
startTime = datetime.now()

@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_makereport(item, call):
    """

    :meta private:
    """
    # execute all other hooks to obtain the report object
    outcome = yield
    rep = outcome.get_result()

    # store test results for each phase of a call, which can
    # be "setup", "call", "teardown"
    item.stash.setdefault(phase_report_key, {})[rep.when] = rep

    # record timestamp for report
    rep.timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

    return rep

def pytest_addoption(parser: pytest.Parser):
    """

    :meta private:
    """
    Config.addCmdLineOptions(parser)

def pytest_configure(config):
    """

    :meta private:
    """
    config.addinivalue_line(
        "markers", "semiauto: mark test to indicate that it requires some input from the tester"
    )

# following three methods define the table in the generated report
def pytest_html_results_table_header(cells: list):
    """

    :meta private:
    """
    cells.insert(1, "<th class='sortable time asc' data-column-type='time'>Time</th>")

def pytest_html_results_table_row(report, cells: list):
    """

    :meta private:
    """
    cells.insert(1, f"<td class='col-time'>{report.timestamp}</td>")

def _format_duration(duration):
    if duration < 1:
        return "{} ms".format(round(duration * 1000))

    hours = math.floor(duration / 3600)
    remaining_seconds = duration % 3600
    minutes = math.floor(remaining_seconds / 60)
    remaining_seconds = remaining_seconds % 60
    seconds = round(remaining_seconds)

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"

def pytest_html_results_summary(prefix: list, summary: list, postfix: list):
    """

    :meta private:
    """
    # tester name
    prefix.append(f"<p>Tester name: {Config.testerName()}</p>")
    # log config
    prefix.append("<p>")

    # build and append config html element
    configHtmlElem = "<details><summary>Config</summary>"
    for key, value in Config.getFullConfigDictionary().items():
        configHtmlElem += f"<p>{key}={value}</p>"
    configHtmlElem += "</details>"
    prefix.append(configHtmlElem)

    # add time to execute start to finish
    executeTime = datetime.now() - startTime
    durationElem = f"<p>Time to execute: {_format_duration(executeTime.seconds)}</p>"
    prefix.append(durationElem)
#######################

# adds html report argument with timestamp if not defined in command line
def pytest_cmdline_main(config: pytest.Config):
    """

    :meta private:
    """
    Config.processCmdLineOptions(config)
    if config.getoption("--html") is None:
        if Config.reportName() != "":
            html_file = os.path.join(Config.reportFolderPath(),Config.reportName())
        else:
            html_file = os.path.join(Config.reportFolderPath(), f"report_{datetime.now().strftime('%Y-%m-%d_%H%M%S')}.html")
        config.option.htmlpath=html_file

@pytest.fixture(scope="session")
def requestTesterName():
    """

    :meta private:
    """
    if Config.testerName() == "":
        name = easygui.enterbox(msg="Enter the tester name (for future sessions, this name can be set in the config.ini file):", title="Enter tester name")
        if name is not None:
            Config.setTesterName(name)


@pytest.fixture(scope="function")
def aladdinProcess() -> subprocess.Popen:
    """
    Fixture that sets up/tears down the Aladdin Standalone Application.

    It is recommended to use the fixture 'defaultAladdinBrowser' or 'primaryAladdinStandaloneBrowser' instead to control
    the application with Playwright.

    Use by including "aladdinProcess" in a test's arguments.
    """
    aladdinProcess = subprocess.Popen(Config.aladdinStandalonePath())
    yield aladdinProcess
    aladdinProcess.terminate()

@pytest.fixture(scope="function")
def aladdinProcessDeveloperMode() -> subprocess.Popen:
    """
    Fixture that sets up/tears down the Aladdin Standalone Application in developer mode.

    It is recommended to use the fixture 'primaryAladdinStandaloneBrowserDeveloperMode' instead to control
    the application with Playwright.

    Use by including "aladdinProcessDeveloperMode" in a test's arguments.
    """
    aladdinProcess = subprocess.Popen([Config.aladdinStandalonePath(),"+d"])
    yield aladdinProcess
    aladdinProcess.terminate()

# Scope for when we launch Aladdin browser can be in each test or in each module.
# Playwright is having memory issues if you pile on too many tests without relaunching, but it would be good to not have
# to launch with every single test to save time. To make experimentation with scope easier for now we have two different
# internal helper functions for each type of browser.
@pytest.fixture(scope="module")
def _moduleScopePrimaryAladdinStandaloneBrowser(aladdinProcess,playwright):
    browser, page = initPrimaryBrowser(playwright, Config.primaryBrowserPort(), "home")
    yield AladdinBrowser(browser, page)
    browser.close()

@pytest.fixture(scope="function")
def _functionScopePrimaryAladdinStandaloneBrowser(aladdinProcess,playwright):
    if Config.skipNotDefaultBrowser() and (Config.defaultAladdinBrowserType() != AladdinBrowserType.STANDALONE_APP):
        pytest.skip(f"Skipping Standalone Browser test because default_browser_type is: {Config.defaultAladdinBrowserType().name}")
    browser, page = initPrimaryBrowser(playwright, Config.primaryBrowserPort(), "home")
    yield AladdinBrowser(browser, page)
    browser.close()

@pytest.fixture(scope="function")
def _functionScopePrimaryAladdinStandaloneBrowserDeveloperMode(aladdinProcessDeveloperMode,playwright):
    if Config.skipNotDefaultBrowser() and (Config.defaultAladdinBrowserType() != AladdinBrowserType.STANDALONE_APP):
        pytest.skip(f"Skipping Standalone Browser test because default_browser_type is: {Config.defaultAladdinBrowserType().name}")
    browser, page = initPrimaryBrowser(playwright, Config.primaryBrowserPort(), "home")
    yield AladdinBrowser(browser, page)
    browser.close()

@pytest.fixture(scope="module")
def _moduleScopeAladdinUrlWebBrowser(playwright):
    browser, page = connectToWebBrowser(playwright, Config.webUrl(), [])
    yield AladdinBrowser(browser, page)
    browser.close()

@pytest.fixture(scope="function")
def _functionScopeAladdinUrlWebBrowser(playwright):
    if Config.skipNotDefaultBrowser() and (Config.defaultAladdinBrowserType() != AladdinBrowserType.WEBAPP_URL):
        pytest.skip(f"Skipping URL Web Browser test because default_browser_type is: {Config.defaultAladdinBrowserType().name}")
    browser, page = connectToWebBrowser(playwright, Config.webUrl(), [])
    yield AladdinBrowser(browser, page)
    browser.close()

@pytest.fixture(scope="module")
def _moduleScopeAladdinLocalWebBrowser(playwright):
    browser, page = connectToWebBrowser(playwright, "file://" + Config.aladdinWebAppPath(), ['--disable-web-security','--allow-file-access-from-files'])
    yield AladdinBrowser(browser, page)
    browser.close()

@pytest.fixture(scope="function")
def _functionScopeAladdinLocalWebBrowser(playwright):
    if Config.skipNotDefaultBrowser() and (Config.defaultAladdinBrowserType() != AladdinBrowserType.WEBAPP_LOCAL):
        pytest.skip(f"Skipping Local Web Browser test because default_browser_type is: {Config.defaultAladdinBrowserType().name}")
    browser, page = connectToWebBrowser(playwright, "file://" + Config.aladdinWebAppPath(), ['--disable-web-security','--allow-file-access-from-files'])
    yield AladdinBrowser(browser, page)
    browser.close()

def _stopContextTracing(inputRequest, browser: AladdinBrowser):
    if Config.contextTracing():
        skipContextTracing = False
        if Config.skipContextTracingOnExpected():
            reportsDict: Dict = inputRequest.node.stash[phase_report_key]
            expected = True
            for report in reportsDict.values():
                if (not hasattr(report, "wasxfail") and report.failed) or (hasattr(report, "wasxfail") and report.passed):
                    expected = False
            if expected:
                skipContextTracing = True

        if not skipContextTracing:
            tracePath = os.path.join(Config.traceFolderPath(), f'{inputRequest.node.name}.zip')
            browser.page.context.tracing.stop(path=tracePath)
            if Config.traceFileSizeLimit() >= 0:
                FileUtils.deleteOldestTraces(Config.traceFolderPath(),Config.traceFileSizeLimit()*1000)
        else:
            browser.page.context.tracing.stop()

@pytest.fixture(scope="function")
def primaryAladdinStandaloneBrowser(requestTesterName, _functionScopePrimaryAladdinStandaloneBrowser, request) -> AladdinBrowser:
    """
    Fixture that sets up/tears down the Aladdin Standalone Application.

    The application can be controlled using Playwright.

    Use by including "primaryAladdinStandaloneBrowser" in a test's arguments.
    """
    if Config.contextTracing():
        _functionScopePrimaryAladdinStandaloneBrowser.page.context.tracing.start(
            screenshots=Config.contextTracingScreenshots(), snapshots=Config.contextTracingSnapshots(), sources=Config.contextTracingSources())
    yield _functionScopePrimaryAladdinStandaloneBrowser
    _stopContextTracing(request, _functionScopePrimaryAladdinStandaloneBrowser)

@pytest.fixture(scope="function")
def primaryAladdinStandaloneBrowserDeveloperMode(requestTesterName, _functionScopePrimaryAladdinStandaloneBrowserDeveloperMode, request) -> AladdinBrowser:
    """
    Fixture that sets up/tears down the Aladdin Standalone Application in developer mode.

    The application can be controlled using Playwright.

    Use by including "primaryAladdinStandaloneBrowserDeveloperMode" in a test's arguments.
    """
    if Config.contextTracing():
        _functionScopePrimaryAladdinStandaloneBrowserDeveloperMode.page.context.tracing.start(
            screenshots=Config.contextTracingScreenshots(), snapshots=Config.contextTracingSnapshots(), sources=Config.contextTracingSources())
    yield _functionScopePrimaryAladdinStandaloneBrowserDeveloperMode
    _stopContextTracing(request, _functionScopePrimaryAladdinStandaloneBrowserDeveloperMode)

@pytest.fixture(scope="function")
def aladdinUrlWebBrowser(requestTesterName, _functionScopeAladdinUrlWebBrowser, request) -> AladdinBrowser:
    """
    Fixture that sets up/tears down a browser containing the Aladdin Web application hosted on a web page.

    The browser can be controlled using Playwright.

    It is recommended to use the fixture 'defaultAladdinBrowser' instead to allow the tester to choose which version of Aladdin to test.

    Use by including "aladdinUrlWebBrowser" in a test's arguments.
    """
    if Config.contextTracing():
        _functionScopeAladdinUrlWebBrowser.page.context.tracing.start(
            screenshots=Config.contextTracingScreenshots(), snapshots=Config.contextTracingSnapshots(), sources=Config.contextTracingSources())
    yield _functionScopeAladdinUrlWebBrowser
    _stopContextTracing(request, _functionScopeAladdinUrlWebBrowser)

@pytest.fixture(scope="function")
def aladdinLocalWebBrowser(requestTesterName, _functionScopeAladdinLocalWebBrowser, request) -> AladdinBrowser:
    """
    Fixture that sets up/tears down a browser containing the Aladdin Web application saved locally.

    The browser can be controlled using Playwright.

    It is recommended to use the fixture 'defaultAladdinBrowser' instead to allow the tester to choose which version of Aladdin to test.

    Use by including "aladdinLocalWebBrowser" in a test's arguments.
    """
    if Config.contextTracing():
        _functionScopeAladdinLocalWebBrowser.page.context.tracing.start(
            screenshots=Config.contextTracingScreenshots(), snapshots=Config.contextTracingSnapshots(), sources=Config.contextTracingSources())
    yield _functionScopeAladdinLocalWebBrowser
    _stopContextTracing(request, _functionScopeAladdinLocalWebBrowser)

@pytest.fixture(scope="function")
def aladdinWebBrowser(request) -> AladdinBrowser:
    """
    Fixture that sets up/tears down an Aladdin web application. The application can be run from local files or a url based on the value of the web_browser_type configuration setting in the config.ini file.

    The browser can be controlled using Playwright.

    Use by including "aladdinWebBrowser" in a test's arguments.
    """
    if Config.defaultAladdinBrowserType() is AladdinBrowserType.WEBAPP_URL:
        yield request.getfixturevalue("aladdinUrlWebBrowser")
    elif Config.defaultAladdinBrowserType() is AladdinBrowserType.WEBAPP_LOCAL:
        yield request.getfixturevalue("aladdinLocalWebBrowser")
    else:
        raise Exception(f"Unexpected web browser type: {Config.defaultAladdinWebBrowserType().name}")

@pytest.fixture(scope="function")
def defaultAladdinBrowser(request) -> AladdinBrowser:
    """
    Fixture that sets up/tears down an Aladdin application. The type of application will be based on the value of the default_browser_type configuration setting in the config.ini file.

    The browser can be controlled using Playwright.

    Use by including "defaultAladdinBrowser" in a test's arguments.
    """
    if Config.defaultAladdinBrowserType() is AladdinBrowserType.STANDALONE_APP:
        yield request.getfixturevalue("primaryAladdinStandaloneBrowser")
    elif Config.defaultAladdinBrowserType() is AladdinBrowserType.WEBAPP_URL:
        yield request.getfixturevalue("aladdinUrlWebBrowser")
    elif Config.defaultAladdinBrowserType() is AladdinBrowserType.WEBAPP_LOCAL:
        yield request.getfixturevalue("aladdinLocalWebBrowser")
    else:
        raise Exception(f"Unexpected default browser type: {Config.defaultAladdinBrowserType().name}")
    
    