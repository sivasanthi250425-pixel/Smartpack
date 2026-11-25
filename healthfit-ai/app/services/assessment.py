"""Rule-based assessment. No AI involved: results come only from product data + rules."""
import re
from app.rules.thresholds import (THRESHOLDS, ALLERGEN_KEYWORDS, CONDITION_TO_ALLERGEN,
                                  ALLERGEN_ALIASES, ALLERGEN_NAMES_TA)
from app.rules.sources import get_sources

BETTER, CAUTION, AVOID, INSUFFICIENT = ("Better fit", "Use caution",
                                        "Avoid due to a confirmed incompatibility",
                                        "Insufficient information")
RESULT_TA = {BETTER: "சிறந்த பொருத்தம்", CAUTION: "கவனத்துடன் பயன்படுத்தவும்",
             AVOID: "உறுதிப்படுத்தப்பட்ட பொருத்தமின்மை – தவிர்க்கவும்",
             INSUFFICIENT: "போதுமான தகவல் இல்லை"}
DISCLAIMER = {"en": "This is informational guidance, not medical advice. SmartPack provides food information only.",
              "ta": "இது தகவல் சார்ந்த வழிகாட்டுதல் மட்டுமே, மருத்துவ ஆலோசனை அல்ல. SmartPack உணவு தகவல்களை மட்டுமே வழங்குகிறது."}


def _norm_allergen(a):
    a = a.strip().lower()
    if a in ALLERGEN_ALIASES:
        return ALLERGEN_ALIASES[a]
    key = a.replace(" ", "_")
    return key if key in ALLERGEN_KEYWORDS else a


def _find_in_ingredients(allergen, ingredients):
    text = " | ".join(i.lower() for i in ingredients)
    for kw in ALLERGEN_KEYWORDS.get(allergen, []):
        if re.search(r"(?<![a-z])" + re.escape(kw) + r"(?![a-z])", text):
            return kw
    return None


def _r(en, ta):
    return {"en": en, "ta": ta}


def _label(a):
    return a.replace("_", " ")


def assess(product, profile):
    """product: dict(name, ingredients[], allergens_declared[], may_contain[], nutrition{per 100 g})
    profile: dict(conditions[], allergies[])"""
    conditions = set(profile.get("conditions", []))
    allergens_needed = {_norm_allergen(a) for a in profile.get("allergies", [])}
    for c, al in CONDITION_TO_ALLERGEN.items():
        if c in conditions:
            allergens_needed.add(al)

    if not conditions and not allergens_needed:
        return _out(INSUFFICIENT, [_r("No health profile or dietary restriction was selected, so this product cannot be checked.",
                                      "சுகாதார விவரம் தேர்ந்தெடுக்கப்படவில்லை, எனவே இந்த பொருளை சரிபார்க்க முடியாது.")], [])

    ingredients = product.get("ingredients") or []
    declared = {_norm_allergen(a) for a in (product.get("allergens_declared") or [])}
    may = {_norm_allergen(a) for a in (product.get("may_contain") or [])}
    nutr = product.get("nutrition") or {}

    avoid, caution, missing, src_keys = [], [], [], []

    for al in sorted(allergens_needed):
        name_ta = ALLERGEN_NAMES_TA.get(al, al)
        hit = _find_in_ingredients(al, ingredients)
        if al in declared:
            avoid.append(_r(f"Confirmed: the product declares {_label(al)}, which you selected to avoid.",
                            f"உறுதி: இந்த பொருளில் {name_ta} உள்ளதாக அறிவிக்கப்பட்டுள்ளது."))
        elif hit:
            avoid.append(_r(f"Confirmed: the ingredient list includes '{hit}' ({_label(al)}), which you selected to avoid.",
                            f"உறுதி: பொருட்கள் பட்டியலில் '{hit}' ({name_ta}) உள்ளது."))
        elif al in may:
            caution.append(_r(f"Uncertain: the label says it may contain {_label(al)} (cross-contact). This is not a confirmed ingredient.",
                              f"உறுதியற்றது: {name_ta} கலந்திருக்கக்கூடும் என்று லேபிள் கூறுகிறது."))
        elif not ingredients and not declared:
            missing.append(_r(f"Ingredient/allergen data is missing, so {_label(al)} could not be checked.",
                              f"பொருட்கள்/ஒவ்வாமை தகவல் இல்லை; {name_ta} சரிபார்க்க முடியவில்லை."))

    def check(key, field, label_en, label_ta, unit_en, unit_ta):
        val = nutr.get(field)
        t = THRESHOLDS[key]
        if val is None:
            missing.append(_r(f"{label_en} data is missing.", f"{label_ta} தகவல் இல்லை."))
            return
        if val > t["value"]:
            caution.append(_r(f"High {label_en.lower()}: {val:g} {unit_en} per 100 g (high level is above {t['value']:g}).",
                              f"அதிக {label_ta}: 100 கிராமில் {val:g} {unit_ta} (அதிக அளவு {t['value']:g}-க்கு மேல்)."))
            src_keys.extend(t["sources"])

    if "diabetes" in conditions:
        check("sugar_g_per_100g_high", "sugar_g", "Sugar", "சர்க்கரை", "g", "கி")
        check("carbs_g_per_100g_high", "carbohydrates_g", "Carbohydrate", "கார்போஹைட்ரேட்", "g", "கி")
    if "hypertension" in conditions:
        check("sodium_mg_per_100g_high", "sodium_mg", "Sodium", "சோடியம்", "mg", "மி.கி")

    if avoid:
        res, reasons = AVOID, avoid + caution
        src_keys.append("fssai")
    elif caution:
        res, reasons = CAUTION, caution + missing
    elif missing:
        res, reasons = INSUFFICIENT, missing
    else:
        res = BETTER
        reasons = [_r("Based on the data provided, no issues were found for your selected conditions. This does not mean the product is medically safe.",
                      "வழங்கப்பட்ட தகவலின்படி, நீங்கள் தேர்ந்தெடுத்த நிலைகளுக்கு பிரச்சினை எதுவும் இல்லை. இது மருத்துவ ரீதியாக பாதுகாப்பானது என்று பொருள் அல்ல.")]
        src_keys.append("who_diet")
    return _out(res, reasons, src_keys)


def _out(result, reasons, src_keys):
    uniq = list(dict.fromkeys(src_keys))
    return {"result": result, "result_ta": RESULT_TA[result], "reasons": reasons,
            "sources": get_sources(uniq), "disclaimer": DISCLAIMER}
