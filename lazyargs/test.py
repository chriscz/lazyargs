from . import *
from .api import W
import pytest

# --- checking functions
@lazyfunction
def equals(expected, value):
    assert expected == value, "expected `{}`, got`{}`".format(expected, value)

def check_number(i):
    try:
        float(i)
    except ValueError:
        raise ValueError("non-number {} not allowed".format(i))

def check_numbers(args):
    for i in args:
        check_number(i)

def check_contains(keyword_list, kwargs, check_reverse=False):
    if not check_reverse:
        for kw in keyword_list:
            assert kw in kwargs, '{} not in {}'.format(kw, kwargs)
    else:
        for kw in kwargs:
            assert kw in keyword_list, '{} not in {}'.format(kw, keyword_list)

@lazyfunction
def check_string(string, lower=False, upper=False, digit=False):
    ERROR = lambda x: ValueError('{} is not'.format(string, x))

    if lower and not string.islower():
        raise ERROR("lower")
    if upper and not string.isupper():
        raise ERROR("upper")
    if digit and not string.isdigit():
        raise ERROR("digit")

@lazyfunction
def check_name_against_request_user(url_name, request):
    if url_name != request['user']['username']:
        raise ValueError("user != username")

# --- example functions
def sum_numbers(*args):
    return sum(args)

def load_profile(request, name, age=20, email=None):
    return True

def runner(*args, **kwargs):
    return True

def index(request):
    return 'hello'

from collections import namedtuple
Person = namedtuple('Person', ['name', 'age'])
# --- actual tests
request =  {'method': 'GET',
            'user': {
                'username': 'chris',
                'friends': [Person('alex', 30)],
                'greetings': (lambda name: "Hello %s!" % name),
            },
            'query': {
                'scores':[1,2,3,[4,5]],
            },
}

def test_sum_numbers():
    d_sum_numbers = precondition(check_numbers, W['*args'])(sum_numbers)

    assert d_sum_numbers(10, 100) == 110
    assert d_sum_numbers(1, 3, 2.0, 5.0, 1e2) >= 111.0

    with pytest.raises(ValueError):
        d_sum_numbers(1, 3, 2.0, 5.0, "a")


def test_load_profile():
    d_load_profile = precondition(check_name_against_request_user(A.name, A.request))(load_profile)
    d_load_profile2 = precondition(check_name_against_request_user(A.name, A[0]))(load_profile)

    assert d_load_profile(request, "chris")
    assert d_load_profile2(request, "chris")

    with pytest.raises(ValueError):
        d_load_profile(request, "heinrich")

    with pytest.raises(ValueError):
        d_load_profile2(request, "heinrich")

def test_load_profile_weak_noarg_name_lookup():
    d_load_profile = precondition(check_name_against_request_user(W.name, W[0]))(load_profile)

    with pytest.raises(KeyError):
        d_load_profile(request, "chris")

def test_load_profile_weak():
    d_load_profile = precondition(check_name_against_request_user(W[1], W[0]))(load_profile)
    d_load_profile(request, "chris")

def test_bad_getitem():
    with pytest.raises(ValueError):
        precondition(check_name_against_request_user(W[1], W["lol"]))(load_profile)

def test_bad_numerical_getitem():
    with pytest.raises(ValueError):
        precondition(check_name_against_request_user(W[1], W[.53243]))(load_profile)


def test_load_profile_access_keyword_argument():
    d_load_profile = precondition(check_number, W.age)(load_profile)
    assert d_load_profile(request, "asdf")

def test_load_profile_pass_arguments():
    d_load_profile = precondition(check_name_against_request_user("alexis", W[0]))(load_profile)

    with pytest.raises(ValueError):
        d_load_profile(request, "heinrich")  # <-- will ignore heinrich

def test_fetch_kwargs():
    d_runner = precondition(check_contains, A['*args'], A['**kwargs'])(runner)

    assert d_runner('foo', 'bar', foo=1, bar=2)

    with pytest.raises(AssertionError):
        d_runner('foo', 'bar', foo=1)

def test_condition_function_kwargs():
    d_runner = precondition(check_contains, A['*args'], A['**kwargs'], check_reverse=True)(runner)

    assert d_runner('foo', 'bar', foo=1)

    with pytest.raises(AssertionError):
        d_runner('foo', 'bar', foo=1, baz='allo')

def index_equality(expected, equals):
    return precondition(equals(expected, equals))(index)(request)

def test_chaining_1():
    assert index_equality('chris', A.request['user']['username'])

def test_chaining_2():
    assert index_equality('alex', A.request['user']['friends'][0][0])

def test_chaining_3():
    assert index_equality('Hello Stranger!', A.request['user']['greetings']('Stranger'))

def test_chaining_4():
    assert index_equality('alex', A.request['user']['friends'].name)
