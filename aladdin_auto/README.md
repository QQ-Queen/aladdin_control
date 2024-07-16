## aladdin_auto

This repo contains the aladdin_auto Python plugin library (in the aladdin_auto/aladdin_auto folder) and a set of python test scripts that use this library (in the aladdin_auto/test_scripts folder).

The aladdin_auto library is a plugin library for Python's pytest testing framework. The purpose of the library is to provide fixtures and methods to assist with quickly setting up and writing tests for the Aladdin Web Application, the Aladdin Standalone Application, or both. In addition to the aladdin_auto library, these tests use the Playwright framework to automate control of the application.

## Aladdin

Aladdin can refer to the Aladdin Web Application and the Aladdin Standalone Application. The Aladdin Web Application is a static webpage created with Angular that is used for scanner configuration tasks that do not involve a connected scanner, like generating programming barcodes. The Aladdin Standalone Application is a Java application with all of the same features as the Web Application, but also includes additional features that involve direct communication with the scanner. The Standalone Application uses the Web Application as it's front end, launching and controlling the page with the jxbrowser library.

## How to Use

The library supports Python 3.9-3.11. Go to python.org to install Python.

How to use this repo to run Aladdin test cases:
1. Install requirements by running in the command line : 
    ```
    python -m pip install -r requirements.txt
    ```

2. Install Playwright libraries by running: 
    ```
    playwright install
    ```

3. [ThanhNT: Skip this step, because the ```config.ini``` file copied to ```config\aladdin```]

    "Copy aladdin_auto/test_scripts/config/config_default.ini and rename new file to aladdin_auto/test_scripts/config/config.ini.
    Update to desired settings in new config.ini file."
    

4. If testing the standalone application, the primary_browser_port/secondary_browser_port in the config.ini must match the PrimarySeleniumPort/SecondarySeleniumPort in the standalone application's config.properties file.
If defaults are kept, open 
    ```
    C:\ProgramData\Datalogic\Aladdin\config.properties 
    ```
    and add lines "SeleniumEnable=true", "PrimarySeleniumPort=9222" and "SecondarySeleniumPort=9223"

    ```
    SeleniumEnable=true
    PrimarySeleniumPort=9222
    SecondarySeleniumPort=9223
    ```

5. [ThanhNT: Skip this step because we need not to run pytest]
    
    "From the command line run "py -m pytest" to run all tests. 
    To run only a specific testset run the previous command followed by the name of the script, e.g. "py -m pytest test_scripts\test_Aladdin_Primary_Window.py".
    Any configuration options in config.ini can be overrun from the command line, for example, to set a tester name and avoid having to specify the tester name during the test execution, run "py -m pytest --tester_name examplename".
    To run multiple tests in parallel, add argument "--numprocesses n" where n is the number of processes. n can be anywhere from 2 to the number of CPUs on your machine. You can add "--numprocesses auto" to use as many processes as your computer has CPU cores."

6. [ThanhNT: Skip this step, added ```test_log_path = test_logs/aladdin/``` (default)]
    
    "Test report html will appear in the folder specified by config.ini (by default this will be in aladdin_auto/reports) after the test has completed."

7. [ThanhNT: Before run script, kindly setup ```config\aladdin\aladdin_config.ini```, for example:]
    ```
    ; Name of tester executing the test (leave blank if PC is shared and you will be prompted for this value).
    tester_name=ThanhNT

    ; Test log folder path
    test_log_folder_path=test_logs/aladdin/
    
    ; Test scanner name
    test_scanner_name=MO14
    ```