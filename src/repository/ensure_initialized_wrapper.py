from functools import wraps


def ensure_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self._directories_initialized:
            raise RuntimeError("Repository is not initialized. Use scm init first.")
        return func(self, *args, **kwargs)

    return wrapper
