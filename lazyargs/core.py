import functools

import inspect

from functions import mangle

from decorate import BaseDecorator

__all__ = ['S', 'W', 'precondition', 'checkfunction']

# --- class definitions

class ChainedArgument(object):
    """
    """
    # TODO add more special methods
    def __init__(self, root_argument):
        self.__root = root_argument
        self.__actions = []

    def __resolve(self, call_arguments):
        value = self.__root(call_arguments)

        for (action, args, kwargs) in self.__actions:
            value = getattr(value, action)(*args, **kwargs)

        return value

    def __call__(self, *args, **kwargs):
        self.__actions.append(('__call__', args, kwargs))
        return self

    def __getitem__(self, *args, **kwargs):
        self.__actions.append(('__getitem__', args, kwargs))
        return self

    def __getattr__(self, *args, **kwargs):
        self.__actions.append(('__getattr__', args, kwargs))
        return self

class Argument(object):
    def __init__(self, key, key_type, kwarg_try_harder=False):
        self.key = key
        self.key_type = key_type
        self.try_harder = kwarg_try_harder

    def __call__(self, call_arguments):
        if self.key_type == 'arg':
            # TODO could try harder here , but *args of python3
            # comes in the way. How??
            return call_arguments.args[self.key]
        elif self.key_type == 'kwarg':
            if not self.try_harder:
                return call_arguments.kwargs[self.key]
            else:
                return call_arguments.kwargs.get(self.key,
                       call_arguments.argsdict.get(self.key))
        elif self.key_type == '**kwargs':
            return call_arguments.varkwargs
        elif self.key_type == '*args':
            return call_arguments.varargs
        raise RuntimeError("Invalid key type {}".format(self.key_type)) # pragma: no cover

class LazyArgs(object):
    def __init__(self, try_harder=False):
        self.__try_harder = try_harder

    def __create_argument(self, *args, **kwargs):
        return ChainedArgument(Argument(*args, **kwargs))

    def __getitem__(self, key):
            if key in {'*args', '**kwargs'}:
                return self.__create_argument(None, key, self.__try_harder)
            else:
                intkey = int(key)
                if key != intkey:
                    raise ValueError("Key is not an integer or *args or **kwargs")
                return self.__create_argument(intkey, 'arg', self.__try_harder)

    def __getattr__(self, key):
        return self.__create_argument(key, 'kwarg', self.__try_harder)

def resolve_chained(chained, call_arguments):
    return getattr(chained, mangle(chained, '__resolve'))(call_arguments)

def getvalue(value, call_arguments):
    if isinstance(value, ChainedArgument):
        return resolve_chained(value, call_arguments)
    else:
        return value

def resolve_lazy_args(call_arguments, lazy_args, lazy_kwargs):
    # --- resolve all lazy arguments
    processed_args = []
    processed_kwargs = {}

    for i in lazy_args:
        processed_args.append(getvalue(i, call_arguments))

    for k in lazy_kwargs:
        processed_kwargs[k] = getvalue(lazy_kwargs[k], call_arguments)

    return (processed_args, processed_kwargs)



# --- decorator functions
"""
def precondition(prefunction, *pre_args, **pre_kwargs):
    def wrap(function):
        argspec = inspect.getargspec(function)
        @functools.wraps(function)
        def wrapper(*fargs, **fkwargs):
            # --- build precondition arguments
            call_arguments = getcallargs(argspec, fargs, fkwargs)
            processed_pre_args = []
            processed_kwargs = {}

            for i in pre_args:
                processed_pre_args.append(getvalue(i, call_arguments))

            for k in pre_kwargs:
                processed_kwargs[k] = getvalue(pre_kwargs[k], call_arguments)

            prefunction(*processed_pre_args, **processed_kwargs)
            return function(*fargs, **fkwargs)
        return wrapper
    # handle the case where `checkfunction` was used
    if not callable(prefunction):
        # then we got output from and @checkfunction wrapped function
        (prefunction, pre_args, pre_kwargs) = prefunction
    return wrap
"""
def checkfunction(function):
    """
    Allows `function` to be called inside the decorator call, as an alternative
    to passing `function` as first first argument of the `precondition` decorator
    """
    @functools.wraps(function)
    def wrapper(*args, **kwargs):
        return (function, args, kwargs)
    return wrapper

class PreconditionDecorator(BaseDecorator):
    def prepare_decorator(self, function, prefunction, *pre_args, **pre_kwargs): 
        if not callable(prefunction):
            # this is a @checkfunction wrapped function
            (prefunction, pre_args, pre_kwargs) = prefunction
        self.prefunction = prefunction
        self.pre_args = pre_args
        self.pre_kwargs = pre_kwargs

    def before_call(self, callargs):
        args, kwargs = resolve_lazy_args(callargs, self.pre_args, self.pre_kwargs)
        self.prefunction(*args, **kwargs)

precondition = PreconditionDecorator.decorator_args

W = LazyArgs()
S = LazyArgs(try_harder=True)
