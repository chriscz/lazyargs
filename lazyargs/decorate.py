import inspect
from errorhandler import ErrorHandlerMeta, excepts
import functions
import sys

__all__ = ['BaseDecorator', 'excepts']

# include the ErrorHandler Mixin
class BaseDecorator(object):
    """
    Override __init__(function, *args, **kwargs) to implement your decorator
    - to register error handlers use the excepts decorator
    """
    __metaclass__ = ErrorHandlerMeta

    def __init__(self, function, *args, **kwargs):
        self.function = function
        self.argspec = inspect.getargspec(function)
        self.prepare_decorator(function, *args, **kwargs)

    def prepare_decorator(self, function, *args, **kwargs):
        """
        Called when the decorator was applied, and may do some
        preprocessing. *args, and *kwargs are the arguments that
        were originally passed to the @mydecorator function, if any.

        Nothing needs to be returned from this method.
        """
        pass

    def before_call(self, call_arguments):
        """Executed right before the wrapped function is called"""
        pass

    def after_call(self, call_arguments, retval):
        """Executed if the function returns normally.
           The value returned by this function will be returned
           to the caller of the decorated function.
        """
        return retval

    def __call__(self, *args, **kwargs):
        callargs = functions.getcallargs(self.argspec, args, kwargs)
        self.before_call(callargs)
        # TODO implement function argument transformation
        try:
            retval = self.function(*args, **kwargs)
        except Exception:
            return self.handle_error(sys.exc_info())
        else:
            return self.after_call(callargs, retval)

    # The following was inspired by http://stackoverflow.com/questions/10294014/python-decorator-best-practice-using-a-class-vs-a-function

    @classmethod
    def decorator_noargs(cls, function):
        """
        Use this when decorators are supposed to support @mydecorator
        notation, without any arguments
        """
        return cls(function)

    @classmethod
    def decorator_args(cls, *args, **kwargs):
        """
        Convenience for decorator that supports arugments.
        """
        def wrap(function):
            return cls(function, *args, **kwargs)
        return wrap

    @classmethod
    def decorator_hybrid(cls, *args, **kwargs):
        """
        Support both args and noargs types. The classification works
        as follows
        - empty(args) and empty(kwargs) --> decorator_args [ex. @mydecorator()]
        - not callable(args[0]) --> decorator_args [ex. @mydecorator(1, 2)]
        - callable(args[0]) and empty(kwargs) and singleton(args) --> decorator_noargs [@mydecorator]
        """
        if len(args) == 1 and callable(args[0]) and not kwargs:
            return cls.decorator_noargs(args[0])
        else:
            return cls.decorator_args(*args, **kwargs)
