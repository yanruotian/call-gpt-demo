# 命令：python3 run-all.py -i extracted_data -o extracted_data-result

import os
import re
import json
import time

from tqdm import tqdm
from typing import Dict, Callable
from argparse import ArgumentParser

from src.main import getRspContent, SYSTEM_PROMPT_DEFAULT
from src.fast_pool import askOne
# from src.main import askOne4 as askOne

SYSTEM_PROMPT = '''
I want you to act as a deep learning model that can accurately perform sentiment analysis. I will enter a sentiment analysis task command, you will fully comply with the task requirements and judge the position on China in the sentence without any national sentiment position, I just want you to reply to one of the three sentiments: positive, negative and neutral, without writing any explanation.
'''

# SYSTEM_PROMPT = SYSTEM_PROMPT_DEFAULT

PROMPT = '''
### Given a sentence, the task is to determine the author's sentiment towards Chinese technology. Categorize sentiments as Positive, Neutral, or Negative reflecting the author's attitude towards Chinese technology in the text. ###
Select Positive if the sentence expresses a positive view towards chinese technology or praises its quality or skills. Select Neutral if the sentence expresses no clear view towards chinese technology or has equal amounts of positive and negative statements or expressing some fact/quote by someone else. Select Negative if the sentence expresses a negative view towards like harsh remarks, criticizing chinese technology action/decision etc.
Remember! If the facts stated in the text are about a breakthrough or success in Chinese technology, choose positive. If the attitude being identified applies to the entire passage and not specifically to Chinese technology, choose Neutral. Please provide a continuous value between -1 and 1, with two decimal places reserved for the result, to indicate the extent of the author's attitude toward Chinese technology in this sentence, with -1 indicating negative and 1 indicating positive.
###When making sentiment determinations, adhere strictly to the rules outlined above.###
Input sentence: "{{ sentence }}".
#Please do the task above for the input sentence, adhere strictly to the rules outlined above. Return the result as: [judgment result, sentiment score].#
'''

PROMPT = '''
### Given a sentence, the task is to determine the author's sentiment towards China. Categorize sentiments as Positive, Neutral, or Negative reflecting the author's attitude towards China in the text. ###
Select Positive if the sentence expresses a positive view towards China or praises its quality or skills. Select Neutral if the sentence expresses no clear view towards China or has equal amounts of positive and negative statements or expressing some fact/quote by someone else. Select Negative if the sentence expresses a negative view towards like harsh remarks, criticizing China action/decision etc.
Remember! If the facts stated in the text are about a breakthrough or success in China, choose positive. If the attitude being identified applies to the entire passage and not specifically to China, choose Neutral. 
Input sentence: "{{ sentence }}".
#Please do the task above for the input sentence, adhere strictly to the rules outlined above. Return the result as: [judgment result].#
'''

PROMPT = 'Input sentence: "{{ sentence }}". What sentiment is shown towards "china"?'

PROMPT = '''
### Given a sentence, the task is to determine the author's sentiment towards China. Categorize sentiments as Positive, Neutral, or Negative reflecting the author's attitude towards China in the text. ###
Select Positive if the sentence expresses a positive view towards China or praises its quality or skills. Select Neutral if the sentence expresses no clear view towards China or has equal amounts of positive and negative statements or expressing some fact/quote by someone else. Select Negative if the sentence expresses a negative view towards like harsh remarks, criticizing China action/decision etc.
Remember! If the facts stated in the text are about a breakthrough or success in China, choose positive. If the attitude being identified applies to the entire passage and not specifically to China, choose Neutral. 
Input sentence: "{{ sentence }}".
#Please do the task above for the input sentence, adhere strictly to the rules outlined above. Return the result as: [judgment result].#
'''

PROMPT = '{{ sentence }}'

def funcTillSucceed(
    maxTryTime: int = 5, 
    callback: Callable[[], None] = lambda: time.sleep(10),
):
    def _wrapper(func: Callable[..., None]):
        def _func(*a, **w):
            for i in range(maxTryTime):
                try:
                    return func(*a, **w)
                except Exception as e:
                    print(f'error exec function {func} (time {i})')
                    print(f'    args = {a}')
                    print(f'    wargs = {w}')
                    print(f'    err: {e.__class__} = {e}')
                    callback()
        return _func
    return _wrapper

def renderPrompt(sentence: str, keyword = None):
    result = PROMPT.replace('{{ sentence }}', sentence)
    if keyword is not None:
        result = result.replace('{{ keyword }}', keyword)
    return result

def dealContent(text: str) -> str:
    text = re.sub(r"(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]", "HTTPURL", text)  # url
    text = re.sub(r"@\S+", "@USER", text)  # username
    text = re.sub(r"RT @USER ", "RT @USER: ", text)  # rt username, 冒号
    return text

def getContent(line: Dict[str, str]):
    line['content_mask'] = dealContent(line.get('rawContent'))
    return line.get('content_mask')

def getKeyword(line: Dict[str, str]):
    keyword = line.get('keyword', '')
    keyword = re.sub(r'since:\w+', '', keyword)
    keyword = re.sub(r'until:\w+', '', keyword)
    keyword = re.sub(r'lang:\w+', '', keyword)
    keyword = re.sub(r'\s+', ' ', keyword)
    return keyword.strip()

def getResult(promptedContent: str):
    return getRspContent(askOne(promptedContent, systemPrompt = SYSTEM_PROMPT))

@funcTillSucceed(maxTryTime = 5)
def dealLine(line: Dict[str, str]):
    content = getContent(line)
    keyword = getKeyword(line)
    promptedContent = renderPrompt(content, keyword = keyword)
    result = getResult(promptedContent)
    line['system-prompt'] = SYSTEM_PROMPT
    line['prompted-content'] = promptedContent
    line['chatgpt-result'] = result

def oneLine(line: str):
    obj = json.loads(line)
    dealLine(obj)
    return json.dumps(obj, ensure_ascii = False)

def getArgs():
    parser = ArgumentParser()
    parser.add_argument('-i', type = str, required = True)
    parser.add_argument('-o', type = str, default = '')
    return parser.parse_args()

ARGS = getArgs()
INPUT_DIR = str(ARGS.i).strip('/\\ \t\n\f')
OUTPUT_DIR = str(ARGS.o or f'{INPUT_DIR}-result')
os.makedirs(OUTPUT_DIR, exist_ok = True)

def deal(relativePath: str):
    inputPath = os.path.join(INPUT_DIR, relativePath)
    outputPath = os.path.join(OUTPUT_DIR, relativePath)
    if os.path.isdir(inputPath):
        os.makedirs(outputPath, exist_ok = True)
        for fileName in sorted(os.listdir(inputPath)):
            deal(os.path.join(relativePath, fileName))
    elif os.path.isfile(inputPath) and inputPath.endswith('.jsonl'):
        if not os.path.exists(outputPath):
            with open(inputPath, 'r', encoding = 'utf-8') as inputFile:
                with open(outputPath, 'w', encoding = 'utf-8') as outputFile:
                    for line in tqdm(inputFile, relativePath):
                        outputFile.write(oneLine(line) + '\n')
        else:
            print(f'quick exit for file "{relativePath}"')

if __name__ == '__main__':
    print(f'{INPUT_DIR = }, {OUTPUT_DIR = }')
    deal('')
    
