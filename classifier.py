"""
Intent Classifier – determines WHAT the user wants and WHICH algorithm they're asking about.
Maps free-form queries to (task_type, algorithm) pairs used by the prompt builder.
"""

import re
from dataclasses import dataclass
from typing import Optional


# ── Supported algorithms ────────────────────────────────────────────────────

ALGORITHM_ALIASES: dict[str, str] = {
    # Minimax
    "minimax": "Minimax",
    "mini max": "Minimax",
    "min max": "Minimax",
    # Alpha-Beta
    "alpha beta": "Alpha-Beta Pruning",
    "alpha-beta": "Alpha-Beta Pruning",
    "alphabeta": "Alpha-Beta Pruning",
    "alpha beta pruning": "Alpha-Beta Pruning",
    # MCTS
    "mcts": "Monte Carlo Tree Search",
    "monte carlo": "Monte Carlo Tree Search",
    "monte carlo tree search": "Monte Carlo Tree Search",
    # A*
    "a*": "A* Search",
    "a star": "A* Search",
    "astar": "A* Search",
    "a-star": "A* Search",
    # Negamax
    "negamax": "Negamax",
    "nega max": "Negamax",
    # Expectimax
    "expectimax": "Expectimax",
    "expecti max": "Expectimax",
    "expectation max": "Expectimax",
}

SUPPORTED_ALGORITHMS = list(set(ALGORITHM_ALIASES.values()))


# ── Task types ───────────────────────────────────────────────────────────────

class TaskType:
    EXPLAIN    = "explain"       # plain-English explanation
    PSEUDOCODE = "pseudocode"    # pseudocode with commentary
    WALKTHROUGH = "walkthrough"  # step-by-step execution trace
    COMPARE    = "compare"       # side-by-side comparison
    COMPLEXITY = "complexity"    # Big-O derivation


TASK_PATTERNS: dict[str, list[str]] = {
    TaskType.PSEUDOCODE: [
        r"\bpseudo\s*code\b", r"\bcode\b", r"\bimplement\b", r"\bprogram\b",
        r"\bwrite\b.*\balgorithm\b", r"\bshow.*code\b",
    ],
    TaskType.WALKTHROUGH: [
        r"\bwalkthrough\b", r"\bwalk\s+through\b", r"\btrace\b", r"\bstep.by.step\b",
        r"\bstep\s+by\s+step\b", r"\bexecute\b", r"\brun\b.*\bexample\b",
        r"\bshow.*how.*works\b", r"\bdemonstrat\b",
    ],
    TaskType.COMPARE: [
        r"\bcompar\b", r"\bdifference(s)?\b", r"\bdiff\b", r"\bvs\b",
        r"\bversus\b", r"\bbetter\b", r"\bworse\b",
    ],
    TaskType.COMPLEXITY: [
        r"\bcomplexity\b", r"\bbig.o\b", r"\bo\(", r"\btime\s+complex\b",
        r"\bspace\s+complex\b", r"\bderive\b", r"\bproof\b",
    ],
    TaskType.EXPLAIN: [
        r"\bexplain\b", r"\bwhat\b", r"\bhow\b", r"\bdescribe\b",
        r"\btell\b", r"\bintroduce\b", r"\blearn\b", r"\bunderstand\b",
    ],
}


@dataclass
class Intent:
    task_type: str
    algorithm: Optional[str]
    raw_query: str
    expertise_level: str  # beginner / intermediate / advanced


def detect_expertise(query: str) -> str:
    q = query.lower()
    if any(k in q for k in ("like i'm 10", "eli5", "simple", "beginner", "basic", "kid")):
        return "beginner"
    if any(k in q for k in ("derive", "proof", "formal", "math", "advanced", "research")):
        return "advanced"
    return "intermediate"


def detect_algorithm(query: str) -> Optional[str]:
    q = query.lower()
    # Collect all matching algorithms
    matches: list[tuple[int, str]] = []
    for alias in ALGORITHM_ALIASES:
        if alias in q:
            algo = ALGORITHM_ALIASES[alias]
            pos = q.index(alias)
            matches.append((pos, algo))

    if not matches:
        return None

    if len(matches) == 1:
        return matches[0][1]

    # Multiple matches: return the one mentioned FIRST in the query
    # so "Implement Negamax with alpha-beta" → Negamax (pos 10 < pos 22)
    matches.sort(key=lambda x: x[0])
    return matches[0][1]


def detect_task(query: str) -> str:
    q = query.lower()
    # Priority order matters: pseudocode > walkthrough > compare > complexity > explain
    for task, patterns in TASK_PATTERNS.items():
        for pat in patterns:
            if re.search(pat, q):
                return task
    return TaskType.EXPLAIN


def classify(query: str) -> Intent:
    return Intent(
        task_type=detect_task(query),
        algorithm=detect_algorithm(query),
        raw_query=query,
        expertise_level=detect_expertise(query),
    )
