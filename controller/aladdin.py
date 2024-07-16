"""
Init logging
"""
import logging
format = "%(asctime)s: %(message)s"
logging.basicConfig(format=format, level=logging.INFO, 
                    datefmt=r"%Y-%m-%d %H:%M:%S")


"""
Insert current work directory to system path
"""
import sys
import os
module_path = os.path.abspath(os.getcwd())
if module_path not in sys.path:
    sys.path.insert(0, module_path)
    paths = '\n'.join(sys.path)
    logging.info(f'System path: \n{paths}')

from typing import Union, Generator
from typing import TYPE_CHECKING
if TYPE_CHECKING:
    from playwright.sync_api._context_manager import PlaywrightContextManager
    from playwright.sync_api import Page
    from playwright._impl._locator import Locator 
    

import subprocess
from playwright.sync_api import sync_playwright
from aladdin_auto.aladdinbrowser import AladdinBrowser
from aladdin_auto.config import Config, AladdinBrowserType
from aladdin_auto.standaloneappbrowser import initPrimaryBrowser, connectPrimaryBrowser
from aladdin_auto.webbrowser import connectToWebBrowser
import time
from datetime import datetime
from threading import Timer

class AladdinController:
    _ELEMENT_XPATH_DICT = {
        "terminal_text" : '//*[@id="terminalText"]',
        "terminal_button" : '//*[@id="headTerminal"]/h5/button',
        "show_custom_buttons_toggle" : '//*[@id="show_custom_buttons_toggle"]',
        "terminal_clear_text" : '//*[@id="terminalClearText"]',
        "get_version_button" : '/html/body/app-root/app-product/div/main/div/div/div/div/section[2]/div[3]/div[1]/div[4]/div[2]/div/div/app-terminal/div[3]/div[2]/div/div[1]',
        "get_identification_button" : '/html/body/app-root/app-product/div/main/div/div/div/div/section[2]/div[3]/div[1]/div[4]/div[2]/div/div/app-terminal/div[3]/div[2]/div/div[2]',
        "get_enhanced_statistics_button" : '/html/body/app-root/app-product/div/main/div/div/div/div/section[2]/div[3]/div[1]/div[4]/div[2]/div/div/app-terminal/div[3]/div[2]/div/div[4]',
        "get_enhanced_events_button" : '/html/body/app-root/app-product/div/main/div/div/div/div/section[2]/div[3]/div[1]/div[4]/div[2]/div/div/app-terminal/div[3]/div[2]/div/div[5]',
    }

    _DEPENDENCES_DICT = {
        "terminal_text" : "terminal_button",
        "show_custom_buttons_toggle" : "terminal_button",
        "get_version_button" : "show_custom_buttons_toggle"
    }

    def __init__(self, timeout: float = 0.0) -> None:
        '''
        timeout : the period waiting for the next action (unit = min).
        '''
        self._timeout = timeout
        self._aladdin_process = None
        

    @property
    def all_infor(self) -> dict:
        try: 
            return self._all_infor
        except AttributeError:
            self._get_all_infor()
            return self._all_infor
    
    @property
    def aladdin_browser(self):
        try: 
            return self._aladdin_browser
        except AttributeError:
            self._connect_browser()
            return self._aladdin_browser
        
    @property
    def aladdin_process(self):
        return self._aladdin_process
        
    @property
    def playwright(self):
        try: 
            return self._playwright
        except AttributeError:
            self._init_playwright()
            return self._playwright
    
    @property
    def page(self):
        aladdin_browser = self.aladdin_browser
        return aladdin_browser.page

    @property
    def elements_dict(self) -> dict[str, "Locator"]:
        try:
            return self._elements_dict
        except AttributeError:
            self._inspect_page()
            return self._elements_dict

    @property
    def timeout(self) -> float:
        return self._timeout
    
    def element(self, name: str) -> Union["Locator", None]:
        elements_dict = self.elements_dict
        return elements_dict.get(name, None)
    
    def _inspect_page(self) -> None:
        xpath_dict = self._ELEMENT_XPATH_DICT
        page = self.page
        elements_dict = {}
        for name in xpath_dict.keys():
            element = self._locate_element(page, name)
            elements_dict.update({name : element})
        self._elements_dict = elements_dict


    def _locate_element(self, page: "Page", element_name: str) -> "Locator":
        xpath = f"xpath={self._ELEMENT_XPATH_DICT.get(element_name)}"
        return page.locator(xpath)

    def _init_playwright(self) -> None:
        logging.info(f"Initializing Playwright...")
        p = sync_playwright().start()
        self._playwright = p
        logging.info(f"Initialized Playwright: {p!r}")

    
    def _get_all_infor(self) -> None:
        # Show esential elements 
        # in case they are hiding
        self._show_elements("terminal_text")
        self._show_elements("get_version_button")
        
        # Click terminal buttons 
        # to get standard informations
        e_lst = [
            'terminal_clear_text',
            'get_version_button',
            'get_identification_button',
            'get_enhanced_statistics_button',
            'get_enhanced_events_button',
        ]
        self._click_elements(names_list=e_lst)
        
        # Send service port commands to get more information
        # ...

        # Capture text in terminal
        terminal_text = self.element('terminal_text')
        infor = terminal_text.inner_text()
        logging.info(f"inner text: {infor}\nType: {type(infor)}")
        self._all_infor = infor
        return infor

    def get_all_infor(self, save_infor: bool = True) -> str:
        all_infor = self._get_all_infor()
        
        if save_infor: 
            self._save_infor()
        
        # Run timer for the next action
        self._run_timer()
        
        return all_infor
    
    def _run_timer(self):
        timeout = self.timeout
        if not timeout:
            return
        self._terminate()
        interval = 60.0 * timeout
        f = self.get_all_infor
        t = Timer(interval, f, args=None, kwargs=None)
        t.start()
        self._t = t
        logging.info(f'Started timer: interval = {interval!r}, func: {f!r}')
            
        
    def _save_infor(self):
        all_infor = self.all_infor
        log_folder_path = Config.testLogsFolderPath()
        scanner_name = Config.testScannerName()
        scanner_log_path = f'{log_folder_path}/{scanner_name}'
        
        # Check the scanner log exist.
        # if not, create new one.
        if not os.path.exists(scanner_log_path):
            os.makedirs(scanner_log_path)
        file_name = f'{scanner_name}_Events_log_and_statistics'
        date_time = self._get_datetime()
        full_path = f'{scanner_log_path}/{file_name}_{date_time}.txt'
        
        with open(full_path, "w", encoding='utf-8') as f:
            f.write(all_infor)

    def _get_datetime(self) -> str:
        now = datetime.now()
        date_time = now.strftime(r"%Y%m%d_%H%M%S")
        return date_time

        
    def _click_elements(self, names_list: list[str]) -> None:
        elements_dict = self.elements_dict
        for name in names_list:
            e = elements_dict.get(name)
            e.click()
            logging.info(f"Element clicked: {name!r}")
            logging.info(f"Waiting 1 sec ...")
            time.sleep(1)

    def _show_elements(self, name: str) -> None:
        logging.info(f"Showing element: {name!r}")

        elements_dict = self.elements_dict
        logging.info(f'{elements_dict}')
        target_element = elements_dict.get(name)
        dependence_dict = self._DEPENDENCES_DICT
        
        cur_e, cur_name = target_element, name
        e_stack = []
        while not cur_e.is_visible():
            patron_name = dependence_dict[cur_name]
            patron_e = elements_dict.get(patron_name)
            logging.info(f'{patron_name}')
            e_stack.append(patron_name)
            cur_e, cur_name = patron_e, patron_name

        logging.info(f"Element stack: {e_stack!r}")
        
        # Reverse elements stack 
        name_lists = e_stack.copy()
        del e_stack
        name_lists.reverse()
        self._click_elements(names_list=name_lists)


    def _connect_browser(self, playwright: Union["PlaywrightContextManager", None] = None) -> Generator[AladdinBrowser, None, None]:
        """
        Connect to Aladdin browser
        """
        playwright = self.playwright
        page = None
        browser = None
        aladdinProcess = None

        if Config.defaultAladdinBrowserType() is AladdinBrowserType.STANDALONE_APP:
            try: 
                # Connect exsited browser
                browser, page = connectPrimaryBrowser(
                    playwright=playwright, 
                    port=Config.primaryBrowserPort(), 
                    pageURLEnding="")
            except:
                # Open new process
                aladdinProcess = subprocess.Popen([Config.aladdinStandalonePath(),"+d"])
                browser, page = initPrimaryBrowser(playwright,Config.primaryBrowserPort(),"home")
        elif Config.defaultAladdinBrowserType() is AladdinBrowserType.WEBAPP_URL:
            browser, page = connectToWebBrowser(playwright, Config.webUrl(), [])
        elif Config.defaultAladdinBrowserType() is AladdinBrowserType.WEBAPP_LOCAL:
            browser, page = connectToWebBrowser(playwright, "file://" + Config.aladdinWebAppPath(), ['--disable-web-security','--allow-file-access-from-files'])
        else:
            raise Exception(f"Unexpected default browser type: {Config.defaultAladdinBrowserType().name}")
        
        aladdin_browser = AladdinBrowser(browser=browser, page=page)

        self._aladdin_browser = aladdin_browser
        self._aladdin_process = aladdinProcess
        return aladdin_browser

    def _terminate_aladdin_process(self):
        aladdinProcess = self.aladdin_process
        if aladdinProcess is not None:
            aladdinProcess.terminate()
            self._aladdin_process = None

    def _terminate_playwright(self) -> None:
        try:
            p = self._playwright
            p.stop()
            del self._playwright
            logging.info(f"Terminated playwright")
        except AttributeError:
            logging.info('Playwright have not started yet')

    def _terminate(self) -> None:
        self._terminate_playwright()
        self._terminate_aladdin_process()
        del self._elements_dict
        del self._aladdin_browser


if __name__ == '__main__':
    aladdin_ctrl = AladdinController(timeout=30)
    aladdin_ctrl.get_all_infor(save_infor=True)