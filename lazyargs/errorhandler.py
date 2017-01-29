import inspect
import sys
"""
NOTES ON METACLASSES
- __new__ is called for each class X that uses the __metaclass__,
  including subclasses of X. __new__ is executed before the actual class
  has been created. __new__ always originates from the `metaclass`. 
  new is actually a static method of ErrorHandler.
- __init__ is called after __new__,

"""

def excepts(*exceptions):
    """
    Decorate a function as being an error handler. To
    be used in conjunction with ErrorHandlerMeta
    """
    def wrap(function):
        function._handles_errors = exceptions
        return function
    return wrap

class ErrorHandlerMixin(object):
    _error_handlers = {}

    def raise_exception(self, exc_info):
        raise exc_info[0], exc_info[1], exc_info[2]

    def handle_error(self, exc_info=None, context=None): 
        """
        Call the error handler registered to handle `type(exp)` or any
        of its subclasses.

        exc_info[0] --> type
        exc_info[1] --> value
        exc_info[2] --> traceback
        """
        if exc_info is None:
            exc_info = sys.exc_info()

        (etype, evalue, etb) = exc_info

        for c in inspect.getmro(etype):
            if c in self._error_handlers:
                # NOTE pass self explicitly, because we capture the 
                # functions when they are unbound
                return self._error_handlers[c](self, exc_info, context)

        return self.handle_unhandled_error(exc_info)

    def handle_unhandled_error(self, error):
        """
        Default behaviour is to raise the error
        """
        self.raise_exception(error)

class ErrorHandlerMeta(type):
    def __new__(meta, name, bases, dct):
        if not any(map(lambda x: issubclass(x, ErrorHandlerMixin), bases)):
            bases = [ErrorHandlerMixin] + list(bases)
        return super(ErrorHandlerMeta, meta).__new__(meta, name, tuple(bases), dct)

    def __init__(cls, name, bases, dct):
        super(ErrorHandlerMeta, cls).__init__(name, bases, dct)

        # register all the handlers
        for name in dct:
            entry = dct[name]
            if callable(entry) and hasattr(entry, '_handles_errors'):
                for err in entry._handles_errors:
                    cls._error_handlers[err] = entry
                # remove unnecessary property
                del entry._handles_errors
