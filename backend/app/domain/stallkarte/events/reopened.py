from app.domain.stallkarte.event import EventPayload


class Reopened(EventPayload, event_type="stallkarte.reopened"):
    pass
