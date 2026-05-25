from typing import Dict, Any, List
import spacy
from spacy.lang.en import English
import dateparser

try:
    nlp = spacy.load("en_core_web_sm")
except Exception:
    # fallback to blank English model; entities won't be available
    nlp = English()


def preprocess_transcript(text: str) -> Dict[str, Any]:
    doc = nlp(text)
    persons: List[str] = []
    orgs: List[str] = []
    entities: Dict[str, List[str]] = {}
    for ent in getattr(doc, "ents", []):
        entities.setdefault(ent.label_, []).append(ent.text)
        if ent.label_ == "PERSON":
            persons.append(ent.text)
        if ent.label_ in ("ORG", "NORP"):
            orgs.append(ent.text)

    return {"persons": persons, "orgs": orgs, "entities": entities}


def parse_date(text: str):
    if not text:
        return None
    dt = dateparser.parse(text)
    return dt
