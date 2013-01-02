'''
Created on Jul 11, 2012

@author: kaining
'''

# all error codes should be larger than 0, 0 means ok
class LocalsErrorMessage:
    USERNAME_EXISTS = {"message": "username exists", "code": 1}
    EMAIL_EXISTS = {"message": "email exists", "code": 2}
    LOGIN_FAILED = {"message": "login failed", "code": 3}
    RELOGIN = {"message": "login failed", "code": 4}
    NO_PRIVILEGE = {"message": "no privilege", "code": 5}
    SERVER_ERROR = {"message": "server error", "code": 100}

class LocalsException(Exception):
    def __init__(self, obj):
        self.value = obj['message']
        self.code = obj['code']
        
    def __str__(self):
        return repr(str(self.code) + ":" + self.value)

class UsernameExistsException(LocalsException):
    def __init__(self):
        LocalsException.__init__(self, LocalsErrorMessage.USERNAME_EXISTS)

class EmailExistsException(LocalsException):
    def __init__(self):
        LocalsException.__init__(self, LocalsErrorMessage.EMAIL_EXISTS)

class LoginFailedException(LocalsException):
    def __init__(self):
        LocalsException.__init__(self, LocalsErrorMessage.LOGIN_FAILED)
        
class ReLoginException(LocalsException):
    def __init__(self):
        LocalsException.__init__(self, LocalsErrorMessage.RELOGIN)

class NoPrivilegeException(LocalsException):
    def __init__(self):
        LocalsException.__init__(self, LocalsErrorMessage.NO_PRIVILEGE)

class ServerErrorException(LocalsException):
    def __init__(self):
        LocalsException.__init__(self, LocalsErrorMessage.SERVER_ERROR)