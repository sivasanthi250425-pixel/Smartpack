from fastapi import APIRouter
from app.models.schemas import AskRequest, AskResponse
from app.routes.health import resolve_profile
from app.services.assessment import assess, DISCLAIMER
from app.services.ai_service import ask_ai, pick_sources

router = APIRouter(prefix="/api/assistant", tags=["assistant"])


@router.post("/ask", response_model=AskResponse)
async def ask(req: AskRequest):
    assessment = None
    product = req.product.model_dump() if req.product else None
    if product:
        assessment = assess(product, resolve_profile(req.user_id, None))
    answer = await ask_ai(req.question, req.language, assessment, product)
    return AskResponse(status="success", answer=answer,
                       sources=pick_sources(req.question, assessment["sources"] if assessment else None),
                       disclaimer=DISCLAIMER[req.language])
