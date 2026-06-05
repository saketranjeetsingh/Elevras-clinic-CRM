from pydantic import BaseModel


class DoctorSignup(BaseModel):

    name: str

    email: str

    password: str

    clinic_name: str


class DoctorLogin(BaseModel):

    email: str

    password: str