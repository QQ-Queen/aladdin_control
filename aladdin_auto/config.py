from configparser import ConfigParser
from enum import Enum
import os
from typing import Type

import pytest
import argparse


class AladdinBrowserType(Enum):
    STANDALONE_APP = "STANDALONE_APP"
    WEBAPP_URL = "WEBAPP_URL"
    WEBAPP_LOCAL = "WEBAPP_LOCAL"

    def __str__(self):
        return self.value

class Config:

    _strOptions = {
        "standalone_path": "C:\\Program Files (x86)\\Datalogic\\Aladdin\\Aladdin.exe",
        "webapp_path": "C:\\ProgramData\\Datalogic\\Aladdin\\datalogic-aladdin\\index.html",
        "data_folder_path": "C:\\ProgramData\\Datalogic\\Aladdin\\datalogic-aladdin\\assets\\data",
        "report_name": "",
        "web_url": "https://aladdin.datalogic.com",
        "trace_folder_path": "traces",
        "report_folder_path": "reports",
        "tester_name": "",
        "test_log_folder_path" : "",
        "test_scanner_name" : "",
    }

    _booleanOptions = {
        "headless": True,
        "skip_not_default_browser": True,
        "context_tracing": False,
        "skip_context_tracing_on_expected": True,
        "context_tracing_screenshots": True,
        "context_tracing_snapshots": False,
        "context_tracing_sources": False
    }

    _floatOptions = {
        "slow_mo": 0
    }

    _intOptions = {
        "primary_browser_port": 9222,
        "secondary_browser_port": 9223,
        "standalone_startup_secs": 30,
        "secondary_browser_startup_secs": 5,
        "trace_file_size_limit": -1
    }

    _defaultAladdinBrowserType = AladdinBrowserType.STANDALONE_APP
    _defaultAladdinWebBrowserType = AladdinBrowserType.WEBAPP_LOCAL

    _initialized = False
    _defaultSection = "ALADDIN_AUTO"

    _fullConfigDictionary = {}

    @staticmethod
    def addCmdLineOptions(parser: pytest.Parser):
        """Add options to cmd line parser

        :param parser: parser object
        :meta private:
        """
        for option in Config._strOptions.keys():
            parser.addoption(f"--{option}", action="store", type=str)
        for option in Config._booleanOptions.keys():
            parser.addoption(f"--{option}", action=argparse.BooleanOptionalAction, type=bool)
        for option in Config._floatOptions.keys():
            parser.addoption(f"--{option}", action="store", type=float)
        for option in Config._intOptions.keys():
            parser.addoption(f"--{option}", action="store", type=int)
        parser.addoption("--default_browser_type", action="store", type=AladdinBrowserType, choices=list(AladdinBrowserType))
        parser.addoption("--web_browser_type", action="store", type=AladdinBrowserType, choices=list(AladdinBrowserType))

    @staticmethod
    def processCmdLineOptions(config: pytest.Config):
        """Update the config dictionaries with options from the command line

        :param config: pytest config object
        :meta private:
        """
        if not Config._initialized:
            Config._initializeConfig()
        for option in Config._strOptions.keys():
            value = config.getoption(f"--{option}", default=None)
            if value is not None:
                Config._strOptions[option] = value
        for option in Config._booleanOptions.keys():
            value = config.getoption(f"--{option}", default=None)
            if value is not None:
                Config._booleanOptions[option] = value
        for option in Config._floatOptions.keys():
            value = config.getoption(f"--{option}", default=None)
            if value is not None:
                Config._floatOptions[option] = value
        for option in Config._intOptions.keys():
            value = config.getoption(f"--{option}", default=None)
            if value is not None:
                Config._intOptions[option] = value
        defaultBrowserTypeBrowserValue = config.getoption("--default_browser_type", default=None)
        if defaultBrowserTypeBrowserValue is not None:
            Config._defaultAladdinBrowserType = defaultBrowserTypeBrowserValue
        webBrowserTypeBrowserValue = config.getoption("--web_browser_type", default=None)
        if webBrowserTypeBrowserValue is not None:
            Config._webAladdinBrowserType = webBrowserTypeBrowserValue
        Config._createFullConfigDictionary()

    @staticmethod
    def _findFileInCwd(filename: str):
        cwd = os.getcwd()
        for root, dirs, files in os.walk(cwd):
            if filename in files:
                return os.path.join(root, filename)
        return None

    @staticmethod
    def _setStrOption(configParser: ConfigParser, option: str):
        if not configParser.has_option(Config._defaultSection, option):
            return
        Config._strOptions[option] = configParser.get(Config._defaultSection, option)

    @staticmethod
    def _setBooleanOption(configParser: ConfigParser, option: str):
        if not configParser.has_option(Config._defaultSection, option):
            return
        Config._booleanOptions[option] = configParser.getboolean(Config._defaultSection, option, fallback=Config._booleanOptions[option])

    @staticmethod
    def _setFloatOption(configParser: ConfigParser, option: str):
        if not configParser.has_option(Config._defaultSection, option):
            return
        Config._floatOptions[option] = configParser.getfloat(Config._defaultSection, option, fallback=Config._floatOptions[option])

    @staticmethod
    def _setIntOption(configParser: ConfigParser, option: str):
        if not configParser.has_option(Config._defaultSection, option):
            return
        Config._intOptions[option] = configParser.getint(Config._defaultSection, option, fallback=Config._intOptions[option])

    @staticmethod
    def _getEnumOption(configParser: ConfigParser, enum: Type[Enum], option: str, default: Enum):
        if not configParser.has_option(Config._defaultSection, option):
            return default
        strValue = configParser.get(Config._defaultSection, option)
        return enum[strValue]

    @staticmethod
    def _createFullConfigDictionary():
        Config._fullConfigDictionary.update(Config._strOptions)
        Config._fullConfigDictionary.update(Config._booleanOptions)
        Config._fullConfigDictionary.update(Config._floatOptions)
        Config._fullConfigDictionary.update(Config._intOptions)
        Config._fullConfigDictionary["default_browser_type"] = Config._defaultAladdinBrowserType
        Config._fullConfigDictionary["web_browser_type"] = Config._defaultAladdinWebBrowserType

    @staticmethod
    def getFullConfigDictionary():
        """Gets the config dictionary with all options.

        :meta private:
        """
        return Config._fullConfigDictionary

    @staticmethod
    def _initializeConfig():
        # mark as initialized
        Config._initialized = True
        # find location of config file
        configName = "aladdin_config.ini"
        fullConfigPath = Config._findFileInCwd(configName)
        if fullConfigPath is None:
            configName = "aladdin_config_default.ini"
            fullConfigPath = Config._findFileInCwd(configName)

        if fullConfigPath is not None:
            configParser = ConfigParser()
            configParser.read(fullConfigPath)
            for option in Config._strOptions.keys():
                Config._setStrOption(configParser, option)
            for option in Config._booleanOptions.keys():
                Config._setBooleanOption(configParser, option)
            for option in Config._floatOptions.keys():
                Config._setFloatOption(configParser, option)
            for option in Config._intOptions.keys():
                Config._setIntOption(configParser, option)
            Config._defaultAladdinBrowserType = Config._getEnumOption(configParser, AladdinBrowserType, "default_browser_type", AladdinBrowserType.STANDALONE_APP)
            Config._defaultAladdinWebBrowserType = Config._getEnumOption(configParser, AladdinBrowserType, "web_browser_type", AladdinBrowserType.STANDALONE_APP)
        Config._createFullConfigDictionary()

    @staticmethod
    def aladdinStandalonePath() -> str:
        """
        Path to Aladdin standalone application.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["standalone_path"]

    @staticmethod
    def aladdinWebAppPath() -> str:
        """
        Path to index.html of Aladdin web application.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["webapp_path"]

    @staticmethod
    def dataFolderPath() -> str:
        """
        Path to assets/data folder of Aladdin application.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["data_folder_path"]

    @staticmethod
    def reportName() -> str:
        """
        Name of report. Leave blank if default timestamped report should be used.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["report_name"]

    @staticmethod
    def webUrl() -> str:
        """
        URL of Aladdin web application.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["web_url"]

    @staticmethod
    def traceFolderPath() -> str:
        """
        Path to folder where traces should be saved.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["trace_folder_path"]

    @staticmethod
    def reportFolderPath() -> str:
        """
        Path to folder where reports should be saved.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["report_folder_path"]

    @staticmethod
    def testerName() -> str:
        """
        Name of tester executing the test.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["tester_name"]

    @staticmethod
    def setTesterName(name: str):
        """
        Used for overriding the tester name option.
        """
        Config._strOptions["tester_name"] = name

    @staticmethod
    def headless() -> bool:
        """
        True to run in headless mode. Only applicable for web version of Aladdin.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._booleanOptions["headless"]

    @staticmethod
    def skipNotDefaultBrowser() -> bool:
        """
        If True, tests that require a browser other than the default specified in config.ini will be skipped.
        Otherwise, those tests will be run with the browser specified by that test.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._booleanOptions["skip_not_default_browser"]

    @staticmethod
    def contextTracing() -> bool:
        """
        If True, context tracing will be started before Aladdin page is opened.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._booleanOptions["context_tracing"]

    @staticmethod
    def skipContextTracingOnExpected() -> bool:
        """
        If True, context tracing will only be saved when test outcome is unexpected (if failed usually, unless test is marked as xfail). No effect if "context_tracing" is not True.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._booleanOptions["skip_context_tracing_on_expected"]

    @staticmethod
    def contextTracingScreenshots() -> bool:
        """
        Whether to capture screenshots during tracing. Screenshots are used to build a timeline preview.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._booleanOptions["context_tracing_screenshots"]

    @staticmethod
    def contextTracingSnapshots() -> bool:
        """
        If True, this option will capture DOM snapshot on every action (doesn't seem to display properly for Aladdin), and record network activity.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._booleanOptions["context_tracing_snapshots"]

    @staticmethod
    def contextTracingSources() -> bool:
        """
        Whether to include source files for trace actions.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._booleanOptions["context_tracing_sources"]

    @staticmethod
    def slowMo() -> float:
        """
        Slows down Playwright by the specified amount of milliseconds. Only applicable for web version of Aladdin.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._floatOptions["slow_mo"]

    @staticmethod
    def primaryBrowserPort() -> int:
        """
        Primary browser port for Aladdin Standalone Application. Should match value in Aladdin's config.properties file.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._intOptions["primary_browser_port"]

    @staticmethod
    def secondaryBrowserPort() -> int:
        """
        Secondary browser port for Aladdin Standalone Application. Should match value in Aladdin's config.properties file.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._intOptions["secondary_browser_port"]

    @staticmethod
    def standaloneStartupSecs() -> int:
        """
        Number of seconds to wait for Aladdin Standalone Application to startup.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._intOptions["standalone_startup_secs"]

    @staticmethod
    def secondaryBrowserStartupSecs() -> int:
        """
        Number of seconds to wait for Aladdin Standalone Application secondary browser to startup.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._intOptions["secondary_browser_startup_secs"]

    @staticmethod
    def traceFileSizeLimit() -> int:
        """
        Maximum file size of combined trace (zip) files in traces folder in KB. Any more than this will be deleted. Ignored if -1.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._intOptions["trace_file_size_limit"]
    
    @staticmethod
    def testLogsFolderPath() -> int:
        """
        Test logs folder path
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["test_log_folder_path"]
    
    @staticmethod
    def testScannerName() -> int:
        """
        Test logs folder path
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._strOptions["test_scanner_name"]

    @staticmethod
    def defaultAladdinBrowserType() -> AladdinBrowserType:
        """
        Default type of Aladdin browser to launch for tests.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._defaultAladdinBrowserType

    @staticmethod
    def defaultAladdinWebBrowserType() -> AladdinBrowserType:
        """
        Default type of Aladdin browser to launch for web only tests.
        """
        if not Config._initialized:
            Config._initializeConfig()
        return Config._defaultAladdinWebBrowserType
    
    