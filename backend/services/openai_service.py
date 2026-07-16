import json
from flask import current_app
from openai import OpenAI

_SYSTEM_PROMPT = """You are a senior software engineer performing a code review.
You will be given the contents of a single Python file. Identify issues that
static analysis tools (pylint/bandit/radon) typically miss: unclear naming,
poor separation of concerns, missing error handling, logic bugs, weak test
coverage signals, and design smells.

Respond ONLY with a JSON array (no markdown fences, no preamble). Each
element must be an object with exactly these keys:
  "severity": one of "critical", "high", "medium", "low", "info"
  "issue": short title of the problem
  "explanation": 1-3 sentence explanation
  "suggestion": concrete, actionable fix
  "line_number": integer line number if identifiable, else null

Return at most 8 findings. If the code is genuinely clean, return an empty
JSON array: []
"""


def _get_client():
    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        return None
    base_url = current_app.config.get("OPENAI_BASE_URL")
    return OpenAI(api_key=api_key, base_url=base_url)

def run_ai_review(file_path, relative_name=None, max_chars=12000):
    """
    Send file contents to the configured LLM and return normalized
    finding dicts. Falls back to a single informational finding if no
    API key is configured or the call fails, so the pipeline never breaks.
    """
    findings = []
    client = _get_client()
    label = relative_name or file_path

    if client is None:
        findings.append(
            {
                "severity": "info",
                "issue": "AI review skipped",
                "explanation": "No OPENAI_API_KEY configured on the server.",
                "suggestion": "Set OPENAI_API_KEY in your environment to enable AI-powered review comments.",
                "file_name": label,
                "line_number": None,
                "source": "openai",
            }
        )
        return findings

    try:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            code = f.read()[:max_chars]

        model = current_app.config.get("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": f"File: {label}\n\n```python\n{code}\n```"},
            ],
            temperature=0.2,
            max_tokens=1200,
        )
        raw = response.choices[0].message.content.strip()
        raw = raw.removeprefix("```json").removeprefix("```").removesuffix("```").strip()
        parsed = json.loads(raw)

        for item in parsed:
            findings.append(
                {
                    "severity": item.get("severity", "info"),
                    "issue": item.get("issue", "AI-flagged issue"),
                    "explanation": item.get("explanation", ""),
                    "suggestion": item.get("suggestion", ""),
                    "file_name": label,
                    "line_number": item.get("line_number"),
                    "source": "openai",
                }
            )
    except Exception as exc:  # noqa: BLE001 - we never want the pipeline to crash
        findings.append(
            {
                "severity": "info",
                "issue": "AI review error",
                "explanation": f"Could not complete AI review: {exc}",
                "suggestion": "Retry the review; if this persists, check API key/quota.",
                "file_name": label,
                "line_number": None,
                "source": "openai",
            }
        )
    return findings
