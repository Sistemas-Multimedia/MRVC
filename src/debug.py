import builtins

def print(*args, **kwargs):
    if __debug__:
        builtins.print(*args, **kwargs)
