from __future__ import annotations

from enum import Enum


class EventType(Enum):
    UNDEFINED = "undefined"


class EventSource(Enum):
    MANUAL = "manual"
    SQE = "sqe"
    IMPORT = "import"
    CATALOGO = "catalogo"
    API = "api"
    MIGRATION = "migration"


class EventStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    SUPERSEDED = "superseded"
    DELETED = "deleted"
