#import builtins
import logging

def print(*args, **kwargs):
    logging.debug(*args, **kwargs)
    #if __debug__:
    #    builtins.print(*args, **kwargs)
