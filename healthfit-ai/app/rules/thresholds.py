"""Validated, rule-based thresholds (per 100 g). The AI never changes these.

sugar / sodium: UK FSA/NHS front-of-pack 'high' cut-offs for solid foods
(sugars > 22.5 g, salt > 1.5 g = sodium > 600 mg per 100 g).
carbs: NO official per-100g cut-off exists. The value below is a placeholder that your
team/mentor must review. It is flagged `needs_review`.
"""

THRESHOLDS = {
    "sugar_g_per_100g_high": {"value": 22.5, "sources": ["nhs_labels", "who_sugars"]},
    "sodium_mg_per_100g_high": {"value": 600.0, "sources": ["nhs_labels", "who_sodium"]},
    "carbs_g_per_100g_high": {"value": 60.0, "sources": ["who_diet"], "needs_review": True},
}

ALLERGEN_KEYWORDS = {
    "milk": ["milk", "whey", "casein", "caseinate", "lactose", "butter", "cream", "cheese",
             "yogurt", "yoghurt", "curd", "paneer", "ghee", "milk solids", "milk powder"],
    "gluten": ["wheat", "barley", "rye", "malt", "semolina", "maida", "atta", "spelt",
               "triticale", "gluten", "durum", "refined wheat flour", "wheat flour"],
    "peanut": ["peanut", "groundnut", "arachis"],
    "tree_nut": ["almond", "cashew", "walnut", "pistachio", "hazelnut", "pecan", "macadamia"],
    "soy": ["soy", "soya", "soybean", "soy lecithin"],
    "egg": ["egg", "albumen", "albumin", "mayonnaise"],
    "fish": ["fish", "anchovy", "tuna", "salmon", "cod"],
    "shellfish": ["shrimp", "prawn", "crab", "lobster", "shellfish", "crustacean"],
    "sesame": ["sesame", "gingelly", "tahini"],
    "mustard": ["mustard"],
}

CONDITION_TO_ALLERGEN = {"lactose_intolerance": "milk", "gluten_restriction": "gluten"}
ALLERGEN_ALIASES = {"nuts": "tree_nut", "tree nut": "tree_nut", "tree nuts": "tree_nut",
                    "dairy": "milk", "lactose": "milk", "peanuts": "peanut", "eggs": "egg",
                    "soya": "soy", "wheat": "gluten"}

ALLERGEN_NAMES_TA = {
    "milk": "பால்", "gluten": "குளூட்டன்", "peanut": "நிலக்கடலை", "tree_nut": "மரக் கொட்டைகள்",
    "soy": "சோயா", "egg": "முட்டை", "fish": "மீன்", "shellfish": "கடல் உணவு (ஓடுடையவை)",
    "sesame": "எள்", "mustard": "கடுகு",
}

CONDITIONS = ["diabetes", "hypertension", "lactose_intolerance", "gluten_restriction"]
