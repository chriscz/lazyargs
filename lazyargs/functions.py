from collections import namedtuple, OrderedDict
# all fields are dictionaries, except varargs and args
CallArguments = namedtuple('CallArguments', ['args', 'argsdict', 'kwargs', 'varargs', 'varkwargs'])
# args --> args as a list (includes defaults)
# argsdict --> map variable name to value
# kwargs --> dict[argname -> value]
# varargs --> *args
# varkwargs --> **kwargs

def getcallargs(argspec, args, kwargs):
    """Returns a CallArguments instance."""
    kwarguments_rlen = -len(argspec.defaults) if argspec.defaults else None

    positional_names = argspec.args[:kwarguments_rlen]
    positionals = args[:len(positional_names)]

    assert len(positionals) == len(positional_names)

    astar = args[len(positionals):]

    kwarguments_keywords = argspec.args[len(positionals):]
    kwarguments = OrderedDict()

    kstar = dict(kwargs)

    for i, kw in enumerate(kwarguments_keywords):
        kwarguments[kw] = kstar.pop(kw, argspec.defaults[i])

    return CallArguments(positionals, OrderedDict(zip(positional_names, positionals)), kwarguments, astar, kstar)

def mangle(obj, name):
    """Perform python name mangling for dunder functions"""
    return '_' + type(obj).__name__ + name


