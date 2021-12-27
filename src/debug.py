#import builtins
import logging
logger = logging.getLogger()
#logger.setLevel(logging.DEBUG)
logger.setLevel(logging.ERROR)

def debug(*args, **kwargs):
    logging.debug(*args, **kwargs)
    #if __debug__:
    #    builtins.print(*args, **kwargs)

def info(*args, **kwargs):
    logging.info(*args, **kwargs)

def error(*args, **kwargs):
    logging.error(*args, **kwargs)
