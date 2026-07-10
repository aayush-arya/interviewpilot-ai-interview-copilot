"""Tolerant JSON extraction for LLM output."""
import json
import re


def extract_json(text: str) -> dict:
    """Extract the first JSON object from model output.

    Handles: raw JSON, ```json fences, leading/trailing prose, and prefill
    responses that start mid-object (missing the opening brace).
    Raises ValueError if nothing parseable is found.
    """
    text = text.strip()

    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
    if fence:
        text = fence.group(1)

    candidates = [text]
    if not text.startswith("{"):
        # Prefill responses may arrive without the opening brace.
        candidates.append("{" + text)

    last_error: Exception | None = None
    for candidate in candidates:
        start = candidate.find("{")
        if start == -1:
            continue
        try:
            return _parse_balanced(candidate, start)
        except (ValueError, json.JSONDecodeError) as e:
            last_error = e
    raise ValueError(f"No JSON object found in model output ({last_error})")


def _parse_balanced(text: str, start: int) -> dict:
    """Parse from `start` to the matching closing brace (string-aware)."""
    depth = 0
    in_string = False
    escape = False
    for i in range(start, len(text)):
        ch = text[i]
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if ch == '"':
            in_string = not in_string
            continue
        if in_string:
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return json.loads(text[start : i + 1])
    raise ValueError("Unbalanced JSON object")
