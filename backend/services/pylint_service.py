import json
import subprocess


# Pylint message-type -> our severity scale
_TYPE_SEVERITY = {
    "error": "high",
    "fatal": "critical",
    "warning": "medium",
    "refactor": "low",
    "convention": "info",
}


def run_pylint(file_path, relative_name=None):
    """
    Run pylint on a single file and return a list of normalized finding dicts.
    Uses --output-format=json so we don't have to regex-parse text output.
    """
    findings = []
    try:
        result = subprocess.run(
            [
                "pylint",
                "--output-format=json",
                "--disable=C0114,C0115,C0116",  # skip missing-docstring noise
                file_path,
            ],
            capture_output=True,
            text=True,
            timeout=60,
        )
        raw_output = result.stdout.strip()
        if not raw_output:
            return findings

        messages = json.loads(raw_output)
        for msg in messages:
            severity = _TYPE_SEVERITY.get(msg.get("type", "convention"), "info")
            findings.append(
                {
                    "severity": severity,
                    "issue": f"{msg.get('symbol', 'pylint-issue')} ({msg.get('message-id', '')})",
                    "explanation": msg.get("message", ""),
                    "suggestion": _suggest_fix(msg),
                    "file_name": relative_name or file_path,
                    "line_number": msg.get("line"),
                    "source": "pylint",
                }
            )
    except (subprocess.TimeoutExpired, json.JSONDecodeError, FileNotFoundError) as exc:
        findings.append(
            {
                "severity": "info",
                "issue": "pylint-execution-error",
                "explanation": str(exc),
                "suggestion": "Ensure pylint is installed and the file is valid Python.",
                "file_name": relative_name or file_path,
                "line_number": None,
                "source": "pylint",
            }
        )
    return findings


_SUGGESTIONS = {
    # --- imports ---
    "unused-import": "Remove the unused import to keep the module clean.",
    "wildcard-import": "Replace 'from module import *' with explicit imports (e.g. 'import tkinter as tk'), or import only the specific names you use.",
    "unused-wildcard-import": "Since you're not using most of what the wildcard pulls in, switch to explicit imports for just the names you actually reference.",
    "wrong-import-order": "Group imports as: standard library, then third-party, then local — with a blank line between each group.",
    "wrong-import-position": "Move this import to the top of the file, before any other code.",
    "ungrouped-imports": "Group all imports from the same module into a single import statement.",

    # --- naming / shadowing ---
    "redefined-builtin": "Rename this variable — it currently shadows a Python builtin (like 'input', 'id', or 'list'), which can cause confusing bugs later if you try to use the real builtin.",
    "invalid-name": "Rename to follow Python convention: snake_case for variables/functions, PascalCase for classes, UPPER_CASE for constants.",
    "redefined-outer-name": "Rename this local variable/parameter — it's shadowing a name from an outer scope, which can cause confusing bugs.",
    "non-ascii-name": "Use plain ASCII characters for this identifier to avoid encoding issues across environments.",

    # --- unused / dead code ---
    "unused-variable": "Remove or use the variable; prefix with '_' (e.g. '_unused') if it's intentionally unused.",
    "unused-argument": "Remove the unused parameter, or prefix it with '_' if it must stay for interface compatibility.",
    "pointless-statement": "This expression's result isn't used anywhere — remove it or assign it to a variable if it has a side effect you need.",
    "unreachable": "Remove this code — it can never execute because it comes after a return/raise/break/continue.",

    # --- style / formatting ---
    "line-too-long": "Wrap the line or refactor the expression to stay within the line-length limit.",
    "missing-final-newline": "Add a single newline character at the end of the file (most editors have a setting to do this automatically on save).",
    "trailing-whitespace": "Remove the trailing spaces/tabs at the end of this line.",
    "multiple-statements": "Split this into separate lines — one statement per line improves readability.",
    "bad-indentation": "Fix the indentation to use a consistent number of spaces (4 is the Python convention).",

    # --- control flow ---
    "broad-except": "Catch a specific exception type (e.g. 'except ValueError:') instead of a bare/broad except.",
    "no-else-return": "Remove the redundant 'else' after a return statement — just dedent the code that follows.",
    "no-else-raise": "Remove the redundant 'else' after a raise statement — just dedent the code that follows.",
    "too-many-branches": "Break this function into smaller helper functions — too many if/elif branches makes it hard to follow.",
    "too-many-nested-blocks": "Reduce nesting by using early returns ('guard clauses') instead of deeply nested if statements.",
    "inconsistent-return-statements": "Make sure every code path in this function returns a value, or none of them do.",

    # --- function/class design ---
    "too-many-arguments": "Group related parameters into a class or dict, or split this function into smaller ones.",
    "too-many-locals": "This function is doing too much — consider extracting parts of it into smaller helper functions.",
    "too-few-public-methods": "If this class only wraps a couple of values with no real behavior, consider a dataclass or namedtuple instead.",
    "missing-class-docstring": "Add a short docstring describing what this class represents.",
    "missing-function-docstring": "Add a short docstring describing what this function does, its parameters, and its return value.",

    # --- comparisons / logic ---
    "singleton-comparison": "Use 'is None' / 'is not None' instead of '== None' / '!= None'.",
    "use-implicit-booleaness-not-comparison": "Use 'if my_list:' instead of 'if my_list == []:' or 'if len(my_list) == 0:'.",
    "consider-using-in": "Use 'if x in (a, b, c):' instead of chaining multiple 'or' comparisons.",
    "simplifiable-if-statement": "Simplify this to a direct boolean expression, e.g. 'return x > 0' instead of an if/else returning True/False.",
}


def _suggest_fix(msg):
    symbol = msg.get("symbol", "")
    return _SUGGESTIONS.get(
        symbol,
        f"Review this pylint message ({msg.get('message-id', '')}) and adjust the code accordingly.",
    )