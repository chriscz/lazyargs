from .functions import mangle

class ArgumentResolver(object):
    """
    Simplify resolving lazy arguments

    """
    def __init__(self, callargs):
        """
        Parameters
        ----------
        callargs: lazyargs.functions.CallArguments
            the arguments with which a function was called,
            they are inspected to resolve this argument instance. 
        """
        self.callargs = callargs

    def resolve_value(self, value):
        """
        Resolve the given value if it is a ChainedArgument
        else return `value` unaltered.
        """
        if isinstance(value, ChainedArgument):
            resolve_funcname = mangle(value, '__resolve')
            return getattr(value, resolve_funcname)(self.callargs)
        else:
            return value

    def resolve(self, lazy_args, lazy_kwargs):
        """
        Resolve all `lazy_args` and `lazy_kwargs`

        Returns
        -------
        tuple:
            (resolved_args, resolved_kwargs)
        """
        resolved_args = []
        resolved_kwargs = {}

        for i in lazy_args:
            resolved_args.append(self.resolve_value(i))

        for k in lazy_kwargs:
            resolved_kwargs[k] = self.resolve_value(lazy_kwargs[k])

        return (resolved_args, resolved_kwargs)

class ChainedArgument(object):
    """
    A lazy argument that collects successive chainings of actions.

    To resolve the actual value, one must execute `__resolve`.
    But since it is a dunder method, a mangled access would 
    normally be necessary. So instead a `resolve` function is 
    provided to perform the call.
    
    `ArgumentResolver.resolve` is provided as part of this module to resolve it.
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
        self.__actions.append(('__getattribute__', args, kwargs))
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



