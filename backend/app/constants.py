from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"


class TreatmentStatus(str, Enum):
    PLANNED = "Planned"
    IN_PROGRESS = "In Progress"
    COMPLETED = "Completed"


class BillPaymentStatus(str, Enum):
    PENDING = "Pending"
    PAID = "Paid"
    OVERDUE = "Overdue"


STATUS_ALIASES = {
    "scheduled": "Scheduled",
    "completed": "Completed",
    "cancelled": "Cancelled",
    "planned": "Planned",
    "in progress": "In Progress",
    "inprogress": "In Progress",
    "pending": "Pending",
    "paid": "Paid",
    "overdue": "Overdue",
    "done": "Completed",
    "active": "In Progress",
}


def normalize_status(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    normalized = value.strip().lower()
    return STATUS_ALIASES.get(normalized, value.strip())
