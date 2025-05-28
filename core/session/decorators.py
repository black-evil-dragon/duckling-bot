from functools import wraps
from typing import Any, Callable, Optional

import time

def try_repeat_catch(
    max_attempts: int = 3,
    delay_seconds: float = 1.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
    on_failure: Optional[Callable[[int, Exception], Any]] = None,
):

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception = None
            
            for attempt in range(1, max_attempts + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    if attempt < max_attempts:
                        time.sleep(delay_seconds)
                        continue
                    
                    if on_failure is not None:
                        on_failure(attempt, e)
                    raise Exception(
                        f"Failed after {attempt} attempts. Last error: {str(e)}"
                    ) from e
            
            raise Exception("Unexpected error in try_repeat_catch")
        
        return wrapper
    return decorator