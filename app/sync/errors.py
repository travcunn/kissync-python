class BaseError(Exception):
    """SmartFile Sync base Exception. """
    pass


class UploadError(BaseError):
    """ Exception for general upload errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(UploadError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class DownloadError(BaseError):
    """ Exception for general download errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(DownloadError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class MaxTriesError(BaseError):
    """ Exception for failed network connection attempts. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(MaxTriesError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class FileNameError(BaseError):
    """ Exception for files with invalid names. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(FileNameError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class BadEventError(BaseError):
    """ Exception for general download errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(BadEventError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class FileNotAvailableError(BaseError):
    """ Exception when files are not yet available for the upload worker. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(FileNotAvailableError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail


class FileDeletedError(BaseError):
    """ Exception for general download errors. """
    def __init__(self, exc, *args, **kwargs):
        self.exc = exc
        self.detail = str(exc)
        super(FileDeletedError, self).__init__(*args, **kwargs)

        def __str__(self):
            return self.detail
