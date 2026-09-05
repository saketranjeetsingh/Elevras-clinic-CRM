from app.schemas.organization import (
    OrganizationBase,
    OrganizationCreate,
    OrganizationUpdate,
    OrganizationResponse,
    OrganizationWithStats,
)
from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserResponse,
    UserWithRoles,
)
from app.schemas.role import (
    RoleBase,
    RoleCreate,
    RoleUpdate,
    RoleResponse,
    RoleWithPermissions,
    PermissionBase,
    PermissionCreate,
    PermissionResponse,
)
from app.schemas.doctor_profile import (
    DoctorProfileBase,
    DoctorProfileCreate,
    DoctorProfileUpdate,
    DoctorProfileResponse,
)
from app.schemas.patient import (
    PatientBase,
    PatientCreate,
    PatientUpdate,
    PatientResponse,
)
from app.schemas.appointment import (
    AppointmentBase,
    AppointmentCreate,
    AppointmentUpdate,
    AppointmentResponse,
)
from app.schemas.treatment import (
    TreatmentBase,
    TreatmentCreate,
    TreatmentUpdate,
    TreatmentResponse,
)
from app.schemas.bill import (
    BillBase,
    BillCreate,
    BillUpdate,
    BillResponse,
)
from app.schemas.attachment import (
    AttachmentBase,
    AttachmentCreate,
    AttachmentResponse,
)
from app.schemas.doctor import (
    DoctorSignup,
    DoctorLogin,
    DoctorResponse,
)
