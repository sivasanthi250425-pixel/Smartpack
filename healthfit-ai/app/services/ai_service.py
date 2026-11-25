"""AI explanation layer. The AI explains rule results; it never decides them and
never supplies sources (sources always come from app/rules/sources.py)."""
import os
import httpx
from app.rules.sources import get_sources

SYSTEM_PROMPT = """You are SmartPack's food-label assistant.
Rules you must follow:
- Answer ONLY using the CONTEXT provided. If the context does not contain the answer, say you do not have enough information.
- Never invent medical facts, numbers, studies or sources. Never mention a source that is not in the context.
- Never diagnose, recommend treatments or medication, or say a product is medically safe.
- Do not change the assessment result you are given. Clearly separate confirmed facts from uncertain information.
- Use simple, short sentences. Reply in {lang}."""

LANG_NAME = {"en": "English", "ta": "Tamil (தமிழ்)"}


def pick_sources(question: str, assessment_sources=None):
    if assessment_sources:
        return assessment_sources
    q = question.lower()
    keys = []
    if any(w in q for w in ["sodium", "salt", "blood pressure", "hypertension"]):
        keys += ["who_sodium", "nhs_labels"]
    if any(w in q for w in ["sugar", "diabet", "carb"]):
        keys += ["who_sugars", "nhs_labels"]
    return get_sources(list(dict.fromkeys(keys or ["who_diet"])))


def build_context(assessment, product, lang):
    lines = []
    if product:
        lines.append(f"Product data: {product}")
    if assessment:
        lines.append(f"Assessment result (fixed, do not change): {assessment['result']}")
        lines.append("Reasons: " + " | ".join(r[lang] for r in assessment["reasons"]))
    lines.append("Approved sources: " + "; ".join(s["name"] for s in pick_sources("", assessment and assessment["sources"])))
    return "\n".join(lines)


async def ask_ai(question, lang, assessment, product):
    key = os.getenv("GEMINI_API_KEY")
    fallback = " ".join(r[lang] for r in assessment["reasons"]) if assessment else (
        "I do not have enough information to answer this." if lang == "en"
        else "இதற்கு பதிலளிக்க என்னிடம் போதுமான தகவல் இல்லை.")
    if not key:
        return fallback
    model = os.getenv("GEMINI_MODEL", "gemini-2.0-flash")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent"
    body = {
        "system_instruction": {"parts": [{"text": SYSTEM_PROMPT.format(lang=LANG_NAME[lang])}]},
        "contents": [{"role": "user", "parts": [{"text": f"CONTEXT:\n{build_context(assessment, product, lang)}\n\nQUESTION: {question}"}]}],
        "generationConfig": {"temperature": 0.2, "maxOutputTokens": 400},
    }
    try:
        async with httpx.AsyncClient(timeout=20) as client:
            r = await client.post(url, json=body, headers={"x-goog-api-key": key})
            r.raise_for_status()
            return r.json()["candidates"][0]["content"]["parts"][0]["text"].strip()
    except Exception:
        return fallback   # never expose errors/keys; fall back to rule-based text
