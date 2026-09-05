from enum import Enum


class AppointmentStatus(str, Enum):
    SCHEDULED = "Scheduled"
    COMPLETED = "Completed"
    CANCELLED = "Cancelled"
    CONFIRMED = "Confirmed"
    CHECKED_IN = "Checked-in"
    IN_PROGRESS = "In Progress"
    NO_SHOW = "No-show"


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
    "confirmed": "Confirmed",
    "checked-in": "Checked-in",
    "in progress": "In Progress",
    "inprogress": "In Progress",
    "planned": "Planned",
    "pending": "Pending",
    "paid": "Paid",
    "overdue": "Overdue",
    "done": "Completed",
    "active": "In Progress",
    "no-show": "No-show",
    "noshow": "No-show",
}


def normalize_status(value):
    if value is None:
        return None
    if not isinstance(value, str):
        return value
    normalized = value.strip().lower()
    return STATUS_ALIASES.get(normalized, value.strip())


"""Permission codes for RBAC system."""

# Patient permissions
PATIENT_VIEW = "patient:view"
PATIENT_CREATE = "patient:create"
PATIENT_EDIT = "patient:edit"
PATIENT_DELETE = "patient:delete"
PATIENT_MERGE = "patient:merge"

# Appointment permissions
APPOINTMENT_VIEW = "appointment:view"
APPOINTMENT_CREATE = "appointment:create"
APPOINTMENT_EDIT = "appointment:edit"
APPOINTMENT_DELETE = "appointment:delete"
APPOINTMENT_CHECKIN = "appointment:checkin"

# Treatment permissions
TREATMENT_VIEW = "treatment:view"
TREATMENT_CREATE = "treatment:create"
TREATMENT_EDIT = "treatment:edit"
TREATMENT_DELETE = "treatment:delete"

# Bill permissions
BILL_VIEW = "bill:view"
BILL_CREATE = "bill:create"
BILL_EDIT = "bill:edit"
BILL_DELETE = "bill:delete"
BILL_REFUND = "bill:refund"

# Dashboard permissions
DASHBOARD_VIEW = "dashboard:view"

# Attachment permissions
ATTACHMENT_VIEW = "attachment:view"
ATTACHMENT_UPLOAD = "attachment:upload"
ATTACHMENT_DELETE = "attachment:delete"

# Admin permissions
ROLE_MANAGE = "role:manage"
USER_MANAGE = "user:manage"
ORG_MANAGE = "org:manage"

# All permissions list (for seeding)
ALL_PERMISSIONS = [
    (PATIENT_VIEW, "View patient records"),
    (PATIENT_CREATE, "Create patient records"),
    (PATIENT_EDIT, "Edit patient records"),
    (PATIENT_DELETE, "Delete patient records"),
    (PATIENT_MERGE, "Merge duplicate patients"),
    (APPOINTMENT_VIEW, "View appointments"),
    (APPOINTMENT_CREATE, "Create appointments"),
    (APPOINTMENT_EDIT, "Edit appointments"),
    (APPOINTMENT_DELETE, "Delete appointments"),
    (APPOINTMENT_CHECKIN, "Check-in patients"),
    (TREATMENT_VIEW, "View treatments"),
    (TREATMENT_CREATE, "Create treatments"),
    (TREATMENT_EDIT, "Edit treatments"),
    (TREATMENT_DELETE, "Delete treatments"),
    (BILL_VIEW, "View bills"),
    (BILL_CREATE, "Create bills"),
    (BILL_EDIT, "Edit bills"),
    (BILL_DELETE, "Delete bills"),
    (BILL_REFUND, "Process refunds"),
    (DASHBOARD_VIEW, "View dashboard"),
    (ATTACHMENT_VIEW, "View attachments"),
    (ATTACHMENT_UPLOAD, "Upload attachments"),
    (ATTACHMENT_DELETE, "Delete attachments"),
    (ROLE_MANAGE, "Manage roles and permissions"),
    (USER_MANAGE, "Manage users"),
    (ORG_MANAGE, "Manage organization settings"),
]

# Default role permission mappings
DEFAULT_ROLE_PERMISSIONS = {
    "admin": [code for code, _ in ALL_PERMISSIONS],
    "doctor": [
        PATIENT_VIEW, PATIENT_CREATE, PATIENT_EDIT,
        APPOINTMENT_VIEW, APPOINTMENT_CREATE, APPOINTMENT_EDIT, APPOINTMENT_CHECKIN,
        TREATMENT_VIEW, TREATMENT_CREATE, TREATMENT_EDIT,
        BILL_VIEW, BILL_CREATE, BILL_EDIT,
        DASHBOARD_VIEW,
        ATTACHMENT_VIEW, ATTACHMENT_UPLOAD, ATTACHMENT_DELETE,
    ],
    "receptionist": [
        PATIENT_VIEW, PATIENT_CREATE, PATIENT_EDIT,
        APPOINTMENT_VIEW, APPOINTMENT_CREATE, APPOINTMENT_EDIT, APPOINTMENT_CHECKIN,
        BILL_VIEW, BILL_CREATE, BILL_EDIT,
        DASHBOARD_VIEW,
        ATTACHMENT_VIEW, ATTACHMENT_UPLOAD,
    ],
}