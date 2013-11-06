
import flask
import functools

class cached_property(object):
    """Like @property, but caches the value."""

    def __init__(self, func):
        self.__name__ = func.__name__
        self.__module__ = func.__module__
        self.__doc__ = func.__doc__
        self._func = func

    def __get__(self, obj, cls):
        if obj is None:
            return self
        value = self._func(obj)
        obj.__dict__[self.__name__] = value
        return value

_NONE_PASSED = object()

def require_secure(func=_NONE_PASSED):
    """Requires that the user is viewing from localhost.

    Usage:

    @app.route('/')
    @require_secure
    def foo():

    Or use as a plain method

    def foo():
        require_secure()

    Args:
        func - Function to be wrapped. If it is none this was just called
            directly and should just check the assertion.
    """
    if func is _NONE_PASSED:
        if not flask.request.is_secure:
            flask.abort(403)
        return

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        require_secure()
        return func(*args, **kwargs)
    return wrapper
