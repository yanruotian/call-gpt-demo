from .args import getArgs
from .main import main
from .test import test

if __name__ == '__main__':
    args = getArgs()
    if args.test:
        test()
    else:
        main()
    