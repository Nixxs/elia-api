BACKEND_FUNCTION_REGISTRY = {}

def register_backend_function(name):
    """
    Decorator to register a backend callable tool.
    """
    def decorator(func):
        BACKEND_FUNCTION_REGISTRY[name] = func
        return func
    return decorator
