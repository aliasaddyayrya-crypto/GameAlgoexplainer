"""
Response Formatter – renders the LLM output to the terminal.

Applies:
  • Section header highlighting  (## → coloured ANSI)
  • Code block demarcation
  • Table alignment
  • Meta header (task type, algorithm, expertise level, elapsed time)
"""

import re
from src.classifier import Intent

# ── ANSI colours ─────────────────────────────────────────────────────────────

class C:
    RESET  = "\033[0m"
    BOLD   = "\033[1m"
    CYAN   = "\033[36m"
    GREEN  = "\033[32m"
    YELLOW = "\033[33m"
    BLUE   = "\033[34m"
    MAGENTA= "\033[35m"
    DIM    = "\033[2m"


def _supports_color() -> bool:
    import sys, os
    return hasattr(sys.stdout, "isatty") and sys.stdout.isatty()


USE_COLOR = _supports_color()


def _c(color: str, text: str) -> str:
    return f"{color}{text}{C.RESET}" if USE_COLOR else text


# ── Formatters ────────────────────────────────────────────────────────────────

def _render_markdown(text: str) -> str:
    """Minimal markdown → terminal rendering."""
    lines = text.split("\n")
    out = []
    in_code = False

    for line in lines:
        # Code fence
        if line.startswith("```"):
            in_code = not in_code
            if in_code:
                out.append(_c(C.DIM, "  ┌─ code ─────────────────────────────────────────"))
            else:
                out.append(_c(C.DIM, "  └────────────────────────────────────────────────"))
            continue

        if in_code:
            out.append("  " + _c(C.GREEN, line))
            continue

        # H2 heading
        if line.startswith("## "):
            heading = line[3:].strip()
            out.append("")
            out.append(_c(C.CYAN, C.BOLD + f"▶  {heading.upper()}"))
            out.append(_c(C.CYAN, "─" * (len(heading) + 5)))
            continue

        # H3 heading
        if line.startswith("### "):
            heading = line[4:].strip()
            out.append(_c(C.BLUE, f"  ◆ {heading}"))
            continue

        # Bold **...**
        line = re.sub(r"\*\*(.+?)\*\*", lambda m: _c(C.BOLD, m.group(1)), line)

        # Table row (basic)
        if line.startswith("|"):
            out.append("  " + _c(C.DIM, line))
            continue

        out.append(line)

    return "\n".join(out)


def _task_label(task_type: str) -> str:
    labels = {
        "explain":     "Explanation",
        "pseudocode":  "Pseudocode",
        "walkthrough": "Step-by-Step Walkthrough",
        "compare":     "Algorithm Comparison",
        "complexity":  "Complexity Analysis",
    }
    return labels.get(task_type, task_type.capitalize())


def format_response(intent: Intent, raw: str, elapsed: float) -> str:
    algo_str = intent.algorithm or "Detected from context"
    task_str = _task_label(intent.task_type)
    level_str = intent.expertise_level.capitalize()

    header = "\n".join([
        _c(C.MAGENTA, "╔══════════════════════════════════════════════════╗"),
        _c(C.MAGENTA, f"║  GameAlgoExplainer  │  {task_str:<26}║"),
        _c(C.MAGENTA, "╠══════════════════════════════════════════════════╣"),
        _c(C.MAGENTA, f"║  Algorithm : {algo_str:<37}║"),
        _c(C.MAGENTA, f"║  Level     : {level_str:<37}║"),
        _c(C.MAGENTA, f"║  Time      : {elapsed:.2f}s{'':<34}║"),
        _c(C.MAGENTA, "╚══════════════════════════════════════════════════╝"),
    ])

    body = _render_markdown(raw)
    return f"\n{header}\n\n{body}\n"
