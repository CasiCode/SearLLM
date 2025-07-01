class LocalAPIException(Exception):
    def __init__(self, details: str):
        self.status_code = 503
        self.details = details


class ExternalAPIException(Exception):
    def __init__(self, details: str):
        self.status_code = 421
        self.details = details
