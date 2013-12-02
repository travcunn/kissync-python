class BaseException(Exception):
    """SmartFile Sync base Exception. """
    pass


class DownloadException(BaseException):
    """ Exception for general download errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(DownloadException, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class FileNameException(BaseException):
    """ Exception for files with invalid names. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(FileNameException, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class BadEventException(BaseException):
    """ Exception for general download errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(BadEventException, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class FileNotAvailableException(BaseException):
    """ Exception when files are not yet available for the upload worker. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(FileNotAvailableException, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail
