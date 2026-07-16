from flask import current_app
from openai import OpenAI

_DOC_PROMPT = """You are a technical writer. Given a summary of static analysis
and AI review findings for a Python project, write a concise Markdown project
health summary (max 200 words) covering:
- Overall code quality impression
- The 2-3 most important issues to fix first
- One encouraging note on what's done well, if applicable

Keep it plain, direct, and free of fluff. Return Markdown only, no code fences.
"""


def generate_summary(findings, project_name):
    """
    Produce a short human-readable Markdown summary of a review.
    Falls back to a rule-based summary if no API key is configured.
    """
    api_key = current_app.config.get("OPENAI_API_KEY")
    if not api_key:
        return _fallback_summary(findings, project_name)

    try:
        base_url = current_app.config.get("OPENAI_BASE_URL")
        client = OpenAI(api_key=api_key, base_url=base_url)
        model = current_app.config.get("OPENAI_MODEL", "llama-3.1-8b-instant")

        condensed = [
            {"severity": f["severity"], "issue": f["issue"], "file": f.get("file_name")}
            for f in findings[:40]
        ]
        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": _DOC_PROMPT},
                {
                    "role": "user",
                    "content": f"Project: {project_name}\nFindings: {condensed}",
                },
            ],
            temperature=0.4,
            max_tokens=350,
        )
        return response.choices[0].message.content.strip()
    except Exception:
        return _fallback_summary(findings, project_name)


def _fallback_summary(findings, project_name):
    if not findings:
        return f"**{project_name}** passed review with no significant issues found. Nice work."

    counts = {}
    for f in findings:
        counts[f["severity"]] = counts.get(f["severity"], 0) + 1

    top = sorted(findings, key=lambda f: _severity_rank(f["severity"]))[:3]
    top_lines = "\n".join(f"- **{f['issue']}** ({f['severity']}) in `{f.get('file_name')}`" for f in top)

    return (
        f"**{project_name}** review summary:\n\n"
        f"Found {sum(counts.values())} issue(s) — "
        f"{', '.join(f'{v} {k}' for k, v in counts.items())}.\n\n"
        f"Top priorities:\n{top_lines}"
    )


def _severity_rank(severity):
    order = {"critical": 0, "high": 1, "medium": 2, "low": 3, "info": 4}
    return order.get(severity, 5)
