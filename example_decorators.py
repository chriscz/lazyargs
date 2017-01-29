from lazyargs import decorate

class Maybe(object):
    def __init__(self, result=None, error=None):
        self.result = result
        self.error = error

    @property
    def failed(self):
        return self.error is not None

    def __str__(self):
        context = dict(
            status='status={}'.format('failed' if self.failed else 'success'),
            error='error={}'.format(self.error),
            result='result={}'.format(self.result)
        )

        return '<Maybe {status}, {error}, {result}>'.format(**context)

# A simple task decorator
class Task(decorate.BaseDecorator):
    @decorate.excepts(Exception, KeyboardInterrupt)
    def process_error(self, exc_info, context):
        return Maybe(error=exc_info)
        # self.raise_exception(exc_info)
    def after_call(self, callargs, retval):
        return Maybe(result=retval)

task = Task.decorator_hybrid

@task
def add(a, b):
    return a + b

print add(1, 2)
print add('a', 'b')
print add('a', 1)


