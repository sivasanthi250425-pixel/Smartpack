from fastapi import APIRouter, HTTPException
from app.models.schemas import HealthProfile, AssessRequest, AssessResponse
from app.database import db
from app.services.assessment import assess, DISCLAIMER

router = APIRouter(prefix="/api/health", tags=["health"])


@router.post("/profile")
def save_profile(profile: HealthProfile):
    db.save_profile(profile.model_dump())
    return {"status": "success", "message": "Profile saved.", "disclaimer": DISCLAIMER["en"]}


@router.get("/profile/{user_id}")
def read_profile(user_id: str):
    p = db.get_profile(user_id)
    if not p:
        raise HTTPException(404, "No profile found")
    return {"status": "success", "profile": p}


@router.delete("/profile/{user_id}")
def delete_profile(user_id: str):
    return {"status": "success", "deleted": db.delete_profile(user_id)}


def resolve_profile(user_id, inline):
    if inline:
        return inline.model_dump()
    if user_id:
        return db.get_profile(user_id) or {}
    return {}


@router.post("/assess", response_model=AssessResponse)
def assess_product(req: AssessRequest):
    profile = resolve_profile(req.user_id, req.profile)
    res = assess(req.product.model_dump(), profile)
    lang = req.language
    return AssessResponse(
        status="success", result=res["result"],
        result_label=res["result"] if lang == "en" else res["result_ta"],
        reasons=[r[lang] for r in res["reasons"]],
        sources=res["sources"], disclaimer=res["disclaimer"][lang])
