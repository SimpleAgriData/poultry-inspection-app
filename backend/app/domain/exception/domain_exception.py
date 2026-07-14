class DomainException(Exception):
    """Base class for domain exceptions."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.message = message
