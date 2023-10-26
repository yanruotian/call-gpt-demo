import os
import openai

SCRIPT_PATH = os.path.abspath(__file__)
API_KEYS_DIR = os.path.join(os.path.dirname(SCRIPT_PATH), 'api-keys')

def yieldLines(path: str = API_KEYS_DIR):
    if os.path.isdir(path):
        for fileName in os.listdir(path):
            for line in yieldLines(os.path.join(path, fileName)):
                yield str(line)
    elif os.path.isfile(path) and path.endswith('.txt'):
        with open(path, 'r') as file:
            for line in file:
                yield str(line)

def setApiKeyFromLine(line: str):
    openai.api_key = line.split('：')[-1].strip()
