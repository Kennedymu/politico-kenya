from pydantic import BaseModel, EmailStr


class UserRegistration(BaseModel):
    national_id: str
    full_name: str
    email: EmailStr
    phone: str
    password: str
    county_id: int
    constituency_id: int
    ward_id: int
    polling_station: str

class UserLogin(BaseModel):
    national_id: str
    password: str