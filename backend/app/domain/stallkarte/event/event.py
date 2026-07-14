from typing import Any, ClassVar

from pydantic import BaseModel


class Event(BaseModel):
    """
    A generic event structure that encapsulates the type of the event and its
    associated data.
    """

    type: str
    data: BaseModel


class EventPayload(BaseModel):
    """
    Base class for all event payloads in the stallkarte domain. Each subclass must
    define a unique `event_type` that identifies the event type. This class provides
    methods to retrieve the event type and to create an `Event` instance encapsulating
    the payload.

    Usage:
    ```python
        class MyEvent(EventPayload, event_type="my_event_type"):
            field1: str
            field2: int
    ```
    """

    _event_type: ClassVar[str]

    def __init_subclass__(cls, event_type: str, **kwargs: Any) -> None:  # noqa: ANN401
        super().__init_subclass__(**kwargs)
        if not event_type:
            raise ValueError("event_type must be provided for EventPayload subclasses")

        cls._event_type = event_type

    @classmethod
    def type(cls) -> str:
        return cls._event_type

    def event(self) -> Event:
        return Event(
            type=self.type(),
            data=self,
        )
