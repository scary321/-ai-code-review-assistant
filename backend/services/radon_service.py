import json
import subprocess


def _complexity_severity(rank):
    # radon ranks: A (best) .. F (worst)
    mapping = {
        "A": "info",
        "B": "info",
        "C": "low",
        "D": "medium",
        "E": "high",
        "F": "critical",
    }
    return mapping.get(rank, "low")


def run_radon(file_path, relative_name=None):
    """
    Run radon cyclomatic complexity (cc) and maintainability index (mi)
    checks on a single file, returning normalized finding dicts for any
    function/class that scores worse than rank A/B.
    """
    findings = []
    findings.extend(_run_cc(file_path, relative_name))
    findings.extend(_run_mi(file_path, relative_name))
    return findings


def _run_cc(file_path, relative_name):
    findings = []
    try:
        result = subprocess.run(
            ["radon", "cc", "-j", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        raw_output = result.stdout.strip()
        if not raw_output:
            return findings
        data = json.loads(raw_output)
        for _, blocks in data.items():
            for block in blocks:
                rank = block.get("rank", "A")
                if rank in ("A", "B"):
                    continue  # healthy complexity, no finding needed
                findings.append(
                    {
                        "severity": _complexity_severity(rank),
                        "issue": f"High cyclomatic complexity in '{block.get('name')}' (rank {rank})",
                        "explanation": (
                            f"Function/method '{block.get('name')}' has a cyclomatic "
                            f"complexity score of {block.get('complexity')}, rank {rank}."
                        ),
                        "suggestion": "Break this function into smaller helpers to reduce branching complexity.",
                        "file_name": relative_name or file_path,
                        "line_number": block.get("lineno"),
                        "source": "radon",
                    }
                )
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return findings


def _run_mi(file_path, relative_name):
    findings = []
    try:
        result = subprocess.run(
            ["radon", "mi", "-j", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        raw_output = result.stdout.strip()
        if not raw_output:
            return findings
        data = json.loads(raw_output)
        for fname, info in data.items():
            rank = info.get("rank", "A")
            if rank in ("A", "B"):
                continue
            findings.append(
                {
                    "severity": _complexity_severity(rank),
                    "issue": f"Low maintainability index (rank {rank})",
                    "explanation": (
                        f"File has a maintainability index of "
                        f"{round(info.get('mi', 0), 1)}, rank {rank}."
                    ),
                    "suggestion": "Consider refactoring: shorter functions, clearer naming, and reduced nesting.",
                    "file_name": relative_name or file_path,
                    "line_number": None,
                    "source": "radon",
                }
            )
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError):
        pass
    return findings
