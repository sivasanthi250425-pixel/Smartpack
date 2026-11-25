from typing import List, Literal, Optional
from pydantic import BaseModel, Field

Condition = Literal["diabetes", "hypertension", "lactose_intolerance", "gluten_restriction"]
Lang = Literal["en", "ta"]


class HealthProfile(BaseModel):
    user_id: str = Field(..., min_length=1, max_length=64)
    conditions: List[Condition] = []
    allergies: List[str] = []          # e.g. ["peanut", "egg", "shellfish"]
    language: Lang = "en"


class Nutrition(BaseModel):
    """Values per 100 g. Use None when the scanner could not read a value."""
    sugar_g: Optional[float] = None
    carbohydrates_g: Optional[float] = None
    sodium_mg: Optional[float] = None
    serving_size_g: Optional[float] = None


class Product(BaseModel):
    name: Optional[str] = None
    ingredients: List[str] = []
    allergens_declared: List[str] = []   # "Contains: ..." on the label
    may_contain: List[str] = []          # "May contain: ..." on the label
    nutrition: Nutrition = Nutrition()


class AssessRequest(BaseModel):
    user_id: Optional[str] = None            # use saved profile
    profile: Optional[HealthProfile] = None  # or send profile inline (nothing is saved)
    product: Product
    language: Lang = "en"


class Source(BaseModel):
    name: str
    url: str


class AssessResponse(BaseModel):
    status: str
    result: str
    result_label: str          # result text in the requested language
    reasons: List[str]
    sources: List[Source]
    disclaimer: str


class AskRequest(BaseModel):
    question: str = Field(..., min_length=1, max_length=500)
    language: Lang = "en"
    user_id: Optional[str] = None
    product: Optional[Product] = None


class AskResponse(BaseModel):
    status: str
    answer: str
    sources: List[Source]
    disclaimer: str
