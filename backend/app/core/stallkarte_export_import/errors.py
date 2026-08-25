from dataclasses import dataclass


@dataclass
class StallkarteImportError(Exception):
    code: str
    message: str
    german_display_message: str

    def __str__(self) -> str:
        return self.message
