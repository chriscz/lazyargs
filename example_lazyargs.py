from lazyargs import A, precondition, lazyfunction

class User(object):
    def __init__(self, username, friends):
        self.username = username
        self.friends = friends

@lazyfunction
def is_authorized(user, allowed):
    """
    Raises an exception is user is not in allowed
    """
    if user not in allowed:
        raise RuntimeError("{} not authorized".format(user))

@precondition(is_authorized(A.frm.username, A.to.friends))
def send_message(frm, to, message):
    print "Send msg `{}` --> `{}`: {}".format(frm.username, to.username, message)

alice = User('alice', ['bob', 'malory'])
malory = User('malory', ['alice', 'frank', 'zack'])
bob = User('bob', ['alice'])

try:
    send_message(malory, bob, 'hello bob')
except RuntimeError as e:
    print e

send_message(alice, bob, 'hello bob')

