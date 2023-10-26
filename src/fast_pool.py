'''
更改了`askOne`函数的逻辑，使其能够在API池中自动切换以进行加速。
'''

import time
import openai

from typing import Callable

from .main import doPrompt, SYSTEM_PROMPT_DEFAULT
from .utils import yieldLines, setApiKeyFromLine

apiKeyLines = list(yieldLines())
splitTime = 25 / len(apiKeyLines)

apiKeyCount = 0
def setApiKeyAuto():
    global apiKeyCount
    setApiKeyFromLine(apiKeyLines[apiKeyCount % len(apiKeyLines)])
    apiKeyCount += 1

def askOne(
    content: str, 
    promptFunc: Callable[[str], str] = doPrompt,
    systemPrompt: str = SYSTEM_PROMPT_DEFAULT,
    temperature: float = 0.,
):
    setApiKeyAuto()
    promptedContent = promptFunc(content)
    rsp = openai.ChatCompletion.create(
        model = "gpt-3.5-turbo",
        messages = [
            {"role": "system", "content": systemPrompt},
            {"role": "user", "content": promptedContent},
        ],
        temperature = temperature,
    )
    rsp['promptedContent'] = promptedContent
    time.sleep(splitTime)
    return rsp
