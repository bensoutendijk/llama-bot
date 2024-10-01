import time
from functools import wraps

def debounce(wait_ms):
    def decorator(fn):
        last_called = [0]
        @wraps(fn)
        def debounced(*args, **kwargs):
            now = time.time()
            if now - last_called[0] >= wait_ms / 1000:
                last_called[0] = now
                return fn(*args, **kwargs)
        return debounced
    return decorator
