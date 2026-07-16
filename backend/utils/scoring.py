from flask import current_app


def calculate_review_score(findings):
    """
    Convert a list of finding dicts (each with a 'severity' key) into a
    0-100 review score. Starts at 100 and deducts weighted penalties,
    with diminishing returns so a single sloppy file doesn't zero out
    an otherwise decent project.
    """
    if not findings:
        return 100.0

    weights = current_app.config["SEVERITY_WEIGHTS"]
    total_penalty = 0.0

    for f in findings:
        severity = (f.get("severity") or "info").lower()
        weight = weights.get(severity, weights["info"])
        total_penalty += weight

    # Logarithmic-ish damping: diminishing penalty impact as issues stack up,
    # so 40 minor issues don't do more damage than 5 critical ones.
    import math

    damped_penalty = 100 * (1 - math.exp(-total_penalty / 120))
    score = max(0.0, 100.0 - damped_penalty)
    return round(score, 1)


def severity_breakdown(findings):
    """Return counts per severity level, useful for report summaries/charts."""
    counts = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
    for f in findings:
        sev = (f.get("severity") or "info").lower()
        if sev in counts:
            counts[sev] += 1
        else:
            counts["info"] += 1
    return counts
