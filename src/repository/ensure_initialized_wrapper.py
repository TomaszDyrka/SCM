from functools import wraps

from errors.errors import RepositoryNotInitializedError
from repository.find_root import find_repository_root


def ensure_initialized(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not find_repository_root().is_dir():
            raise RepositoryNotInitializedError("Repository is not initialized. Use rvn init first.")
        return func(self, *args, **kwargs)

    return wrapper
