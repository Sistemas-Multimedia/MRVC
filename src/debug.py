#import builtins
#from importlib import reload  # Not needed in Python 2
import logging

logging.basicConfig(
    level=logging.INFO,
    #format="%(name)s %(asctime)s [%(levelname)s] %(message)s",
    format="%(asctime)s p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s",
    #format=['%(asctime)s] p%(process)s {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s','%m-%d %H:%M:%S'],
    handlers=[
        #logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ]
)

#logger = logging.getLogger()
#reload(logging)
#root = logging.getLogger()
# NO root.addHandler(logging.StreamHandler())
# SI for handler in root.handlers[: ]:
#   root.removeHandler(handler)
   
#logger.setLevel(logging.DEBUG)
#logger.setLevel(logging.INFO)
#logger.setLevel(logging.ERROR)

#logging.basicConfig(format='%(name)s %(asctime)s %(levelname)s:%(message)s', datefmt='%I:%M:%S')

#Delete Jupyter notebook root logger handler
#logger = logging.getLogger()
#logger.handlers = []

#Create logger as usual
#logger = logging.getLogger(__name__)
#logging.basicConfig(format='%(name)s %(asctime)s %(levelname)s:%(message)s', level=logging.DEBUG, datefmt='%I:%M:%S')

def debug(*args, **kwargs):
    logging.debug(*args, **kwargs)
    #if __debug__:
    #    builtins.print(*args, **kwargs)

def info(*args, **kwargs):
    logging.info(*args, **kwargs)

def error(*args, **kwargs):
    logging.error(*args, **kwargs)
