class BaseException(Exception):
    """SmartFile Auth base Exception. """
    pass


class AuthException(BaseException):
    """ Exception for authentication errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(AuthException, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class NeedsAuthException(BaseException):
    """ Exception for network connection errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(NetConnectionException, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class NetConnectionException(BaseException):
    """ Exception for network connection errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(NetConnectionException, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail
