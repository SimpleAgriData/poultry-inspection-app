from fastapi import APIRouter

router = APIRouter()


@router.get("/ping", name="Ping", description="Health check endpoint", tags=["Status"])
def get_info() -> dict:
    return {"message": "pong"}
