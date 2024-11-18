from fastapi import APIRouter, File, UploadFile
import tempfile
import shutil

from user.service import UserService
from user.schema import UserSchema, UserProfileSchema, LoginSchema

router = APIRouter("user")
user_service = UserService()


@router.get("/create_user")
async def create_user(user_id: UserSchema):
    return user_service.create_user(
        user_id.email, user_id.password, user_id.firstName, user_id.lastName
    )


@router.post("/create-profile")
async def create_profile(profile: UserProfileSchema, pdf: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        shutil.copyfileobj(pdf.file, temp_file)
        temp_file_path = temp_file.name

    return user_service.update_user_profile(
        user_id=profile.userId,
        cv_file_path=temp_file_path,
        preferred_locations=profile.preferredLocations,
        job_preferences=profile.jobPreferences,
    )


@router.post("/login")
async def login(user_id: LoginSchema):
    return user_service.login(user_id.email, user_id.password)


# @router.get("/get-profile")
# async def get_profile(user_id: str):
#     user_service = UserService()
#     return user_service.get_profile(user_id)


# @router.put("/update-profile")
# async def update_profile(user_id: str, profile: UserProfileSchema):
#     user_service = UserService()
#     return user_service.update_profile(user_id, profile)


# @router.delete("/delete-profile")
# async def delete_profile(user_id: str):
#     user_service = UserService()
#     return user_service.delete_profile(user_id)
