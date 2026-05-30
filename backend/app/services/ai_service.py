"""ai_service.py — AI extraction with validation.

If the AI cannot extract meaningful content from the transcript,
ExtractionError is raised BEFORE anything is saved to the database.
"""
import os
import time
import json
import re
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI

from app.config import AI_API_KEY, AI_API_BASE, AI_MODEL
from app.utils.nlp import preprocess_transcript, parse_date

if AI_API_KEY and AI_API_BASE:
    client = OpenAI(api_key=AI_API_KEY, base_url=AI_API_BASE)
elif AI_API_KEY:
    client = OpenAI(api_key=AI_API_KEY)
else:
    client = OpenAI()

DEFAULT_PROMPT = (
    "You are an assistant that extracts structured meeting minutes from a raw meeting transcript.\n"
    "Return ONLY valid JSON with these keys:\n"
    "summary: string, decisions: [string], action_items: [{task:string, owner:string|null, due_date:string|null, status:string}], risks: [string], open_questions: [string]\n"
    "Use ISO-8601 date formats when possible. Use null for missing owner or due_date.\n"
    "If the transcript is empty or extremely short, return an empty string for `summary` or the verbatim transcript as the `summary` — do NOT return an error phrase like 'No meeting transcript provided'.\n"
    "Do not include any explanation outside the JSON object."
)

# Phrases that indicate the AI refused or got nothing useful.
# If the summary contains any of these the extraction is considered failed.
_REFUSAL_PHRASES = [
    "no meeting transcript",
    "no transcript provided",
    "i cannot",
    "unable to extract",
    "no content provided",
    "empty transcript",
    "please provide",
    "transcript is empty",
    "no text provided",
    "no information provided",
    "not provided",
    "cannot extract",
    "no meeting content",
]

# Minimum number of words in the summary to be considered a real extraction.
_MIN_SUMMARY_WORDS = 5


class ExtractionError(ValueError):
    """Raised when the transcript cannot yield a meaningful extraction."""
    pass


def _validate_extraction(structured: Dict[str, Any]) -> None:
    """Raise ExtractionError if the extraction result is empty or junk.

    This is called BEFORE saving to the database, so no broken records
    are ever persisted.
    """
    summary = (structured.get("summary") or "").strip()
    decisions = structured.get("decisions") or []
    action_items = structured.get("action_items") or []
    risks = structured.get("risks") or []
    open_questions = structured.get("open_questions") or []

    has_any_content = bool(
        summary or decisions or action_items or risks or open_questions
    )

    # 1. Completely empty result
    if not has_any_content:
        raise ExtractionError(
            "No meaningful content could be extracted from the transcript. "
            "Please upload a valid meeting transcript with discussions, decisions, or action items."
        )

    # 2. AI returned a refusal / error phrase instead of real content
    summary_lower = summary.lower()
    for phrase in _REFUSAL_PHRASES:
        if phrase in summary_lower:
            raise ExtractionError(
                "The transcript does not appear to contain meeting content. "
                "Please provide an actual meeting transcript."
            )

    # 3. Summary exists but is suspiciously short (likely just the raw junk text echoed back)
    #    Only enforce this when there are also no structured items extracted.
    word_count = len(summary.split())
    has_structured = bool(decisions or action_items or risks or open_questions)
    if word_count < _MIN_SUMMARY_WORDS and not has_structured:
        raise ExtractionError(
            f"The extracted summary is too short ({word_count} word(s)) to be a real meeting transcript. "
            "Please provide a more detailed transcript."
        )


def extract_message_content(message: Any) -> str:
    if isinstance(message, dict):
        content = message.get("content")
        if content:
            return content
        reasoning = message.get("reasoning")
        if reasoning:
            return reasoning
        reasoning_details = message.get("reasoning_details")
    else:
        content = getattr(message, "content", None)
        if content:
            return content
        reasoning = getattr(message, "reasoning", None)
        if reasoning:
            return reasoning
        reasoning_details = getattr(message, "reasoning_details", None)

    if reasoning_details:
        if isinstance(reasoning_details, str):
            return reasoning_details
        if isinstance(reasoning_details, list):
            pieces = [
                item.get("text")
                for item in reasoning_details
                if isinstance(item, dict) and item.get("text")
            ]
            if pieces:
                return " ".join(pieces)
    return ""


def call_openai_with_retries(prompt: str, max_retries: int = 3, backoff: float = 1.0) -> str:
    last_exc = None
    for attempt in range(1, max_retries + 1):
        try:
            resp = client.chat.completions.create(
                model=AI_MODEL,
                messages=[
                    {"role": "system", "content": DEFAULT_PROMPT},
                    {"role": "user", "content": prompt},
                ],
                temperature=0.2,
                max_tokens=1200,
            )
            message = resp.choices[0].message
            return extract_message_content(message)
        except Exception as e:
            last_exc = e
            time.sleep(backoff * attempt)
    raise last_exc


def extract_json_object(raw_text: str) -> Dict[str, Any]:
    try:
        return json.loads(raw_text)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", raw_text, flags=re.S)
        if match:
            return json.loads(match.group(0))
    raise ValueError("AI did not return valid JSON")


def normalize_ai_response(
    data: Dict[str, Any],
    title: str,
    raw_text: str,
    persons: List[str],
) -> Dict[str, Any]:
    def ensure_list(value):
        if value is None:
            return []
        if isinstance(value, list):
            return value
        return [value]

    action_items = []
    for item in ensure_list(data.get("action_items", [])):
        if not isinstance(item, dict):
            continue
        due_date = item.get("due_date")
        parsed_due = parse_date(due_date) if isinstance(due_date, str) else due_date
        owner = item.get("owner") or (persons[0] if persons else None)
        action_items.append({
            "task": str(item.get("task", "")).strip(),
            "owner": owner,
            "due_date": parsed_due.isoformat() if parsed_due else None,
            "status": str(item.get("status", "pending") or "pending").strip().lower(),
        })

    # User-supplied title always wins — never replaced by AI output.
    final_title = (title or "").strip() or "Untitled Meeting"

    return {
        "title": final_title,
        "raw_text": raw_text,
        "summary": str(data.get("summary") or "").strip(),
        "decisions": [
            str(item).strip()
            for item in ensure_list(data.get("decisions", []))
            if str(item).strip()
        ],
        "action_items": action_items,
        "risks": [
            str(item).strip()
            for item in ensure_list(data.get("risks", []))
            if str(item).strip()
        ],
        "open_questions": [
            str(item).strip()
            for item in ensure_list(data.get("open_questions", []))
            if str(item).strip()
        ],
    }


def build_prompt(raw_text: str, title: Optional[str], preprocessed: Dict[str, Any]) -> str:
    persons = preprocessed.get("persons", [])
    orgs = preprocessed.get("orgs", [])
    entities = preprocessed.get("entities", {})
    return (
        f"Title: {title or 'Untitled Meeting'}\n"
        f"Transcript:\n{raw_text}\n\n"
        f"Detected People: {persons}\n"
        f"Detected Organizations: {orgs}\n"
        f"Detected Entities: {json.dumps(entities)}\n\n"
        "Extract an executive summary, decisions, action items, risks, and open questions. "
        "Return ONLY valid JSON without any surrounding markdown or commentary. "
        "If a field is empty, return an empty list or an empty string as appropriate. "
        "Do not state that the transcript is missing."
    )


def extract_structured_meeting(raw_text: str, title: Optional[str] = None) -> Dict[str, Any]:
    """Extract structured meeting data and validate it has real content.

    Raises ExtractionError (before any DB write) if the transcript is
    empty, too short, or the AI cannot produce a meaningful summary.
    """
    # ── Pre-flight: validate raw input ───────────────────────────────────
    if not raw_text or not raw_text.strip():
        raise ExtractionError(
            "The transcript is empty. Please paste your meeting notes or upload a non-empty file."
        )

    stripped = raw_text.strip()
    word_count = len(stripped.split())

    if word_count < 10:
        raise ExtractionError(
            f"The transcript is too short ({word_count} word(s)). "
            "A valid meeting transcript should contain at least a few sentences of discussion."
        )

    # ── Short-transcript heuristic (10–39 chars edge case) ───────────────
    if len(stripped) < 40:
        pre = preprocess_transcript(raw_text)
        empty_data: Dict[str, Any] = {
            "summary": stripped,
            "decisions": [],
            "action_items": [],
            "risks": [],
            "open_questions": [],
        }
        result = normalize_ai_response(empty_data, title, raw_text, pre.get("persons", []))
        _validate_extraction(result)
        return result

    # ── Full AI extraction ────────────────────────────────────────────────
    pre = preprocess_transcript(raw_text)
    prompt = build_prompt(raw_text, title, pre)
    raw_response = call_openai_with_retries(prompt)

    for attempt in range(2):
        try:
            data = extract_json_object(raw_response)
            break
        except Exception as e:
            logging.warning("AI JSON parse failed (attempt %s): %s", attempt + 1, str(e))
            logging.debug("Raw AI response (truncated): %s", (raw_response or "")[:2000])
            raw_response = call_openai_with_retries(
                "The previous response was not valid JSON. "
                "Return ONLY a valid JSON object with keys: "
                "summary, decisions, action_items, risks, and open_questions. "
                "Do not include any surrounding text."
            )
    else:
        truncated = (raw_response or "")[:2000]
        raise ExtractionError(
            "The AI could not produce a structured response for this transcript. "
            "Please check that your transcript contains clear meeting content and try again. "
            f"(Debug: last AI response truncated — {truncated})"
        )

    result = normalize_ai_response(data, title, raw_text, pre.get("persons", []))

    # ── Post-extraction validation: reject before saving ─────────────────
    _validate_extraction(result)

    return result