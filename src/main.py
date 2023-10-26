'''
尝试用chatgpt发布的api进行提问
'''

# Windows环境readline不可用
try: import readline
except: pass

import re
import json
import openai
import requests

from cmd import Cmd
from typing import Callable

SYSTEM_PROMPT_DEFAULT = 'You are a helpful assistant.'
SYSTEM_PROMPT_JIEBA = '你是一个强大的分词模型，对于用户输入句子，可以返回其以"/"隔开的分词结果。'

def get_api_key():
    '''
    写上自己的api-key
    '''
    return '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'

def doPrompt(content: str):
    '''
    可以加一些默认的prompt提示
    '''
    return content

openai.api_key = get_api_key()

def askOne(
    content: str, 
    promptFunc: Callable[[str], str] = doPrompt,
    systemPrompt: str = SYSTEM_PROMPT_DEFAULT,
    temperature: float = 0.,
):
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
    return rsp

def askOne4(
    content: str, 
    promptFunc: Callable[[str], str] = doPrompt,
    systemPrompt: str = SYSTEM_PROMPT_DEFAULT,
    temperature: float = 0.,
):
    promptedContent = promptFunc(content)
    rsp = requests.post("http://120.92.10.46:8080/chat", json = {
        "messages": [
            {'role': 'system', 'content': systemPrompt},
            {"role": "user", "content": promptedContent},
        ],
        "temperature": temperature,
        "top_p": 1,
        "max_tokens": 512,
        "presence_penalty": 0,
        "frequency_penalty": 0
    }).json()
    # print(f'rsp = {rsp}')
    rsp['promptedContent'] = promptedContent
    return rsp

def getRspContent(rsp) -> str:
    return rsp.get('choices')[0].get('message').get('content')

def transLine(line: str):
    def _multiLineCode(reResult):
        lines = reResult.group(1).split('\n')
        def _getLen(line: str):
            return sum(map(lambda char: (1 if 0x0020 <= ord(char) <= 0x7e else 2), line))
        maxLength = max(30, max(map(_getLen, lines)))
        def _dealLine(line: str):
            line += ''.join(' ' for _ in range(maxLength - _getLen(line)))
            return f'\033[0;33;40m {line} \033[0m'
        return '\n'.join(map(_dealLine, lines))
    line = re.sub(r'`([^`\n]+)`', lambda result: f'\033[0;30;47m {result.group(1)} \033[0m', line)
    # line = re.sub(r'\$([^\$\n]+)\$', lambda result: f'\033[0;34;47m {result.group(1)} \033[0m', line)
    line = re.sub(r'```[^\n]*\n(.+?)\n[^\S\n]*```', _multiLineCode, line, flags = re.S)
    return line

class MyCmd(Cmd):
    prompt = '> '
    def default(self, line: str):
        print(line)
    def precmd(self, line: str) -> str:
        if line.strip() == '.exit':
            print('Exiting...')
            exit()
        elif line.strip() == '.lines':
            line = ''
            while True:
                newLine = input(''.join(' ' for _ in range(len(self.prompt))))
                if newLine.strip() == '.end':
                    line = line[ : -1]
                    break
                line += newLine.replace('\n', '') + '\n'
        print('\033[0;34mquestion\033[0m:')
        print(transLine(line))
        try:
            rsp = askOne(line)
            result = rsp.get('choices')[0].get('message').get('content')
        except Exception as e:
            print('\033[1;37;41m error \033[0m:')
            return f'{e}'
        print('\033[0;34manswer\033[0m:')
        return transLine(result)

def main():
    print('Welcome to chatgpt prompt.')
    print('To exit, type ".exit".')
    myCmd = MyCmd()
    myCmd.cmdloop()

if __name__ == '__main__':
    main()
