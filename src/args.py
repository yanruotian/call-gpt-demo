from argparse import ArgumentParser

def getArgs():
    parser = ArgumentParser()
    parser.add_argument('--test', action = 'store_true') 
    return parser.parse_args()
