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
            pieces = [item.get("text") for item in reasoning_details if isinstance(item, dict) and item.get("text")]
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


def normalize_ai_response(data: Dict[str, Any], title: str, raw_text: str, persons: List[str]) -> Dict[str, Any]:
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

    return {
        "title": title or "AI Generated Meeting",
        "raw_text": raw_text,
        "summary": str(data.get("summary") or "").strip(),
        "decisions": [str(item).strip() for item in ensure_list(data.get("decisions", [])) if str(item).strip()],
        "action_items": action_items,
        "risks": [str(item).strip() for item in ensure_list(data.get("risks", [])) if str(item).strip()],
        "open_questions": [str(item).strip() for item in ensure_list(data.get("open_questions", [])) if str(item).strip()],
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
        "Do not state that the transcript is missing (for example, do NOT say 'No meeting transcript provided')."
    )


def extract_structured_meeting(raw_text: str, title: Optional[str] = None) -> Dict[str, Any]:
    # Short-transcript heuristic: if the transcript is present but very short,
    # avoid calling the AI and return the raw text as the summary to prevent
    # models from responding with misleading messages like 'No meeting transcript provided'.
    if raw_text and len(raw_text.strip()) < 40:
        pre = preprocess_transcript(raw_text)
        empty_data = {
            "summary": raw_text.strip(),
            "decisions": [],
            "action_items": [],
            "risks": [],
            "open_questions": [],
        }
        return normalize_ai_response(empty_data, title, raw_text, pre.get("persons", []))

    pre = preprocess_transcript(raw_text)
    prompt = build_prompt(raw_text, title, pre)
    raw_response = call_openai_with_retries(prompt)
    # Try a small number of reparsing attempts if the model output is not valid JSON.
    for attempt in range(2):
        try:
            data = extract_json_object(raw_response)
            break
        except Exception as e:
            logging.warning("AI JSON parse failed (attempt %s): %s", attempt + 1, str(e))
            logging.debug("Raw AI response (truncated): %s", (raw_response or '')[:2000])
            # Ask the model to return only a JSON object and retry
            raw_response = call_openai_with_retries(
                "The previous response was not valid JSON. Return ONLY a valid JSON object with keys: summary, decisions, action_items, risks, and open_questions. Do not include any surrounding text.")
    else:
        # Include the last raw response in the exception to aid debugging.
        truncated = (raw_response or "")[:2000]
        raise ValueError(f"AI did not return valid JSON. Last raw response (truncated to 2000 chars): {truncated}")

    return normalize_ai_response(data, title, raw_text, pre.get("persons", []))
