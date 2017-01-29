import functools

from decorate import BaseDecorator
from args import ArgumentResolver, LazyArgs


__all__ = ['S', 'W', 'precondition', 'lazyfunction']

# --- decorators
def lazyfunction(function):
    """
    Allows `function` to be called inside other lazy_args
    decorators (such as `precondition`), as an alternative
    to passing `function` as first first argument of the `precondition` decorator.

    Example
    -------
    >>> @lazyfunction
    >>> def foo(a, b): pass
    >>> # allows you to use @precondition(foo(S[0], S[1]))
    >>> # instead of @precondition(foo, S[0], S[1])
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        return (function, args, kwargs)
    return wrapper

class PreconditionDecorator(BaseDecorator):
    def prepare_decorator(self, function, prefunction, *pre_args, **pre_kwargs):
        if not callable(prefunction):
            # this is a @lazyfunction wrapped function
            (prefunction, pre_args, pre_kwargs) = prefunction

        self.prefunction = prefunction
        self.pre_args = pre_args
        self.pre_kwargs = pre_kwargs

    def before_call(self, callargs):
        resolve = ArgumentResolver(callargs).resolve
        args, kwargs = resolve(self.pre_args, self.pre_kwargs)
        self.prefunction(*args, **kwargs)

precondition = PreconditionDecorator.decorator_args

W = LazyArgs()
S = LazyArgs(try_harder=True)
