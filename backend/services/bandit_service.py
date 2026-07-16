import json
import subprocess

_BANDIT_SEVERITY_MAP = {
    "HIGH": "critical",
    "MEDIUM": "high",
    "LOW": "medium",
}


def run_bandit(file_path, relative_name=None):
    """
    Run bandit (security static analysis) on a single file and return
    normalized finding dicts.
    """
    findings = []
    try:
        result = subprocess.run(
            ["bandit", "-f", "json", file_path],
            capture_output=True,
            text=True,
            timeout=60,
        )
        # bandit exits non-zero when issues are found; that's expected.
        raw_output = result.stdout.strip()
        if not raw_output:
            return findings

        data = json.loads(raw_output)
        for issue in data.get("results", []):
            severity = _BANDIT_SEVERITY_MAP.get(issue.get("issue_severity", "LOW"), "medium")
            findings.append(
                {
                    "severity": severity,
                    "issue": f"{issue.get('test_id')} - {issue.get('test_name')}",
                    "explanation": issue.get("issue_text", ""),
                    "suggestion": _security_suggestion(issue.get("test_id", "")),
                    "file_name": relative_name or file_path,
                    "line_number": issue.get("line_number"),
                    "source": "bandit",
                }
            )
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as exc:
        findings.append(
            {
                "severity": "info",
                "issue": "bandit-execution-error",
                "explanation": str(exc),
                "suggestion": "Ensure bandit is installed and the file is valid Python.",
                "file_name": relative_name or file_path,
                "line_number": None,
                "source": "bandit",
            }
        )
    return findings


_SECURITY_SUGGESTIONS = {
    # --- hardcoded secrets ---
    "B105": "Avoid hardcoded passwords/secrets; load them from environment variables instead.",
    "B106": "Avoid hardcoded passwords in function calls/arguments; load them from environment variables instead.",
    "B107": "Avoid hardcoded passwords as default argument values; load them from environment variables instead.",

    # --- deserialization ---
    "B301": "Avoid pickle on untrusted data; use JSON or a safer serialization format.",
    "B302": "Avoid marshal on untrusted data; it isn't designed to be safe against malicious input.",
    "B307": "Avoid eval() on untrusted input; use ast.literal_eval() for parsing literals, or a proper parser for anything more complex.",
    "B321": "Avoid FTP for anything sensitive; it transmits credentials and data in plaintext — use SFTP/FTPS instead.",

    # --- weak crypto ---
    "B303": "Avoid weak hashing (MD5/SHA1) for security-sensitive data; use SHA-256, or bcrypt/argon2 for passwords specifically.",
    "B324": "Avoid weak hash functions for security purposes; use hashlib.sha256() or bcrypt for passwords.",

    # --- randomness ---
    "B311": "This is flagged because Python's 'random' module isn't cryptographically secure. If this is for non-security use (games, shuffling, sampling), it's safe to ignore. If it's for tokens, passwords, or session IDs, switch to the 'secrets' module instead (e.g. secrets.choice(), secrets.token_hex()).",

    # --- SQL / injection ---
    "B608": "Use parameterized queries (e.g. cursor.execute('... WHERE id = %s', (id,))) instead of building SQL via string formatting/concatenation.",
    "B610": "Avoid building Django queryset filters from raw string formatting; use the ORM's parameterized filter arguments instead.",

    # --- subprocess / shell ---
    "B602": "Avoid shell=True in subprocess calls; pass the command as a list of arguments to prevent shell injection.",
    "B603": "Verify this subprocess call only ever runs trusted, hardcoded commands — avoid passing any user-controlled input into it.",
    "B604": "Avoid passing shell=True (or equivalent) to a function that spawns a process; pass arguments as a list instead.",
    "B605": "Avoid os.system(); use the subprocess module with an argument list instead, which avoids shell injection risks.",
    "B607": "Avoid relying on the current PATH for the executable name; use a full, absolute path to the binary instead.",

    # --- network / SSL ---
    "B310": "Validate the URL scheme before opening it with urllib — restrict to http/https to avoid unexpected local file access.",
    "B501": "Avoid disabling SSL certificate verification (verify=False); this exposes you to man-in-the-middle attacks.",
    "B506": "Avoid yaml.load() on untrusted input; use yaml.safe_load() instead.",

    # --- misc ---
    "B404": "Importing 'subprocess' itself isn't dangerous — this is just a heads-up to review how it's used elsewhere in the file (avoid shell=True and untrusted input in the command).",
    "B108": "Avoid hardcoded temp file paths like /tmp/...; use the tempfile module to generate secure, unique temp paths.",
    "B110": "Avoid a bare 'except: pass' — at minimum log the exception so failures aren't silently swallowed.",
    "B112": "Avoid 'continue' inside a bare except block without logging — silent failures make debugging much harder later.",
}


def _security_suggestion(test_id):
    return _SECURITY_SUGGESTIONS.get(
        test_id, f"Review this flagged pattern ({test_id}) for potential security exposure."
    )