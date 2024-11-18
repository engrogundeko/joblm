from pydantic import BaseModel, EmailStr
from email_validator import validate_email, EmailNotValidError
from pydantic.validators import field_validator
from fastapi.exceptions import RequestValidationError
from typing import Optional, Dict, Any, List


class LoginSchema(BaseModel):
    email: EmailStr
    password: str


class UserSchema(BaseModel):
    email: EmailStr
    password: str
    firstName: str
    lastName: str

    @field_validator("email", mode="before")
    def validate_email(self):
        try:
            validate_email(self.email)
        except EmailNotValidError as e:
            raise RequestValidationError(detail=str(e))

    @field_validator("password", mode="before")
    def validate_password(self):
        if len(self.password) < 8:
            raise RequestValidationError(
                detail="Password must be at least 8 characters long"
            )
        return self.password


class UserProfileSchema(BaseModel):
    userId: str
    # phone: Optional[str] = None
    # cvFile: Optional[str] = None
    # cvText: Optional[str] = None
    preferredLocations: Optional[List[str]] = None
    jobPreferences: Optional[Dict[str, Any]] = None
