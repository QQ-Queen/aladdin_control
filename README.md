> What is 'Aladdin Control'?

'Aladdin Control' is a set of scripts to control Aladdin browser automatically.

## Installation
### 1. Initialize virtual environment (venv)
1. Enter in command line:

    ```
    python -m venv .venv
    ```

2. Activate virtual envirnoment

    ```
    .\.venv\Scripts\activate
    ```
    - In case need permission to run scripts

        ```
        Set-ExecutionPolicy -ExecutionPolicy Unrestricted -Scope CurrentUser
        ```

3. Upgrade pip

    ```
    python -m pip install --upgrade pip
    ```


### 2. Aladdin auto
- Follow instructions at ```aladdin_auto\README.md```


## Some useful commands line:
- Install packages in requirements.txt

    ```
    python -m pip install -r .\requirements.txt
    ```

- Freeze current packages:
    ```
    python -m pip freeze > requirements.txt
    ```

## Git commands:

- Pull code from Github
    ```
    git pull
    ```

- Push committed code to Github
    ```
    git push origin main
    ```
    - Can replace ```main``` to the branch name