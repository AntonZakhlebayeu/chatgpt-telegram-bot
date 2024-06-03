class EmptyContentResponseError(Exception):
    """Custom exception for handling empty response from gpt provider"""

    def __init__(self, message, errors=[]):
        super().__init__(message)
        self.errors = errors


class ProviderRequestError(Exception):
    """Custom exception for handling errors during request to gpt provider"""

    def __init__(self, message, errors=[]):
        super().__init__(message)
        self.errors = errors
