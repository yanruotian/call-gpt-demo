import csv
import openai

from tqdm import tqdm

from .main import askOne, getRspContent
from .utils import API_KEYS_DIR, yieldLines

def test():
    with open('results.csv', 'w') as file:
        writer = csv.DictWriter(file, ['api-key', 'question', 'answer'], delimiter = ',')
        writer.writeheader()
        for i, line in tqdm(enumerate(yieldLines(API_KEYS_DIR))):
            openai.api_key = line.split('：')[-1].strip()
            print(f'api key = "{openai.api_key}"')
            question = f"What is 1 + {i}?"
            writer.writerow({
                'api-key': openai.api_key,
                'question': question,
                'answer': getRspContent(askOne(question)),
            })