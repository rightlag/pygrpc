from functools import wraps


def method(cardinality=None):
    """Decorator to ensure that the RPC call matches the proper
    cardinality type."""
    def wrapper(fn):
        @wraps(fn)
        def wrapped(*args, **kwargs):
            kwargs['cardinality'] = cardinality
            return fn(*args, **kwargs)
        return wrapped
    return wrapper
