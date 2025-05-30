from fastapi import APIRouter

router = APIRouter()

@router.get("/profile/{user_id}")
async def get_user_profile(user_id: str):
    # Dummy example
    return {
        "user_id": user_id,
        "name": "Placeholder",
        "status": "active"
    }