from utility import BaseLogManager
import time

def timer(enable: bool = False, logManager: BaseLogManager | None = None):
    def decorator(func):
        def wrapper(*args, **kwargs):
            if enable and logManager is not None:
                start_time = time.time()
                result = func(*args, **kwargs)
                end_time = time.time()
                logManager.info(f"{func.__name__} elapsed time: {1000 * (end_time - start_time):.2f} ms")
                return result
            else:
                return func(*args, **kwargs)
        return wrapper
    return decorator