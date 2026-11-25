"""Approved reference sources. The AI may ONLY cite sources from this list.
Verify every URL is still live before release."""

SOURCES = {
    "who_sodium": {
        "name": "WHO – Salt reduction fact sheet",
        "url": "https://www.who.int/news-room/fact-sheets/detail/salt-reduction",
    },
    "who_sugars": {
        "name": "WHO – Guideline: Sugars intake for adults and children",
        "url": "https://www.who.int/publications/i/item/9789241549028",
    },
    "who_diet": {
        "name": "WHO – Healthy diet fact sheet",
        "url": "https://www.who.int/news-room/fact-sheets/detail/healthy-diet",
    },
    "nhs_labels": {
        "name": "NHS – How to read food labels (traffic-light thresholds)",
        "url": "https://www.nhs.uk/live-well/eat-well/food-guidelines-and-food-labels/how-to-read-food-labels/",
    },
    "fssai": {
        "name": "FSSAI – Food Safety and Standards Authority of India",
        "url": "https://www.fssai.gov.in",
    },
}


def get_sources(keys):
    return [dict(SOURCES[k]) for k in keys if k in SOURCES]
