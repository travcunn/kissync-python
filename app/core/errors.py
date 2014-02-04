class BaseError(Exception):
    """SmartFile Auth base Exception. """
    pass


class AuthError(BaseError):
    """ Exception for authentication errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(AuthError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class NoAuthError(BaseError):
    """ Exception for network connection errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(NoAuthError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class NetConnectionError(BaseError):
    """ Exception for network connection errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(NetConnectionError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail
