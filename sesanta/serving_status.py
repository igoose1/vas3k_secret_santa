import enum


class ServingStatus(enum.StrEnum):
    COLLECTING_FORMS = "collecting"
    DRAWING_LOTS = "drawing"
    SENDING_GIFTS = "sending"
