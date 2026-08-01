from functools import wraps

def ensure_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.find_repository_root().is_dir():
            raise RuntimeError("Repository is not initialized. Use rvn init first.")
        return func(self, *args, **kwargs)

    return wrapper
