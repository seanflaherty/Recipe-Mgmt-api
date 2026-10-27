"""Module for helper functions and custom decorators."""
from functools import wraps

# Custom Decorator
def log_recipe_action(action):
    """Custom decorator to log recipe actions."""
    def decorator(func):
        @wraps(func)
        # Note: we're using this decorator on instance methods,
        # so we need 'self' as the first argument
        def wrapper(self, *args, **kwargs):
            result = func(self, *args, **kwargs)
            recipe_name = args[0] or None
            print(f"[{action.upper()}] Recipe '{recipe_name}' in book '{self.name}'")
            return result

        return wrapper

    return decorator
