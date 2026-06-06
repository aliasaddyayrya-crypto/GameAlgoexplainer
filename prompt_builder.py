"""
Prompt Builder – constructs structured, task-specific prompts for the LLM.

Five templates (Assignment requirement):
  1. EXPLAIN      – plain-English explanation
  2. PSEUDOCODE   – annotated pseudocode
  3. WALKTHROUGH  – step-by-step execution trace on a concrete game
  4. COMPARE      – structured comparison table + analysis
  5. COMPLEXITY   – Big-O derivation with reasoning

Each template embeds:
  • System role  (domain expert persona)
  • Chain-of-Thought instructions
  • Expertise-level adaptation
  • Output structure constraints
  • Hallucination-prevention guard
"""

from src.classifier import Intent, TaskType

# ── Shared fragments ─────────────────────────────────────────────────────────

_COT_INSTRUCTION = (
    "Think step-by-step before writing your final answer. "
    "Reason through the problem internally first, then produce the structured response."
)

_HALLUCINATION_GUARD = (
    "Important: Only state facts established in the algorithm literature. "
    "If you are uncertain about a claim, prefix it with 'To the best of my knowledge'. "
    "Do not invent algorithm variants or optimizations not documented in standard references."
)

_SYSTEM_ROLE = (
    "You are GameAlgoExplainer, a specialist AI tutor with deep expertise in game-playing "
    "algorithms: Minimax, Alpha-Beta Pruning, Monte Carlo Tree Search (MCTS), A* Search, "
    "Negamax, and Expectimax. You explain concepts clearly using concrete game examples "
    "(Tic-Tac-Toe, Chess, Go, Backgammon, pathfinding maps). "
    "You adapt your language and depth to the user's expertise level."
)

_EXPERTISE_PREAMBLE = {
    "beginner": (
        "The user is a beginner. Use simple language, avoid heavy math, "
        "and use relatable analogies (e.g., Tic-Tac-Toe, 'thinking like a player'). "
        "Keep sentences short and clear."
    ),
    "intermediate": (
        "The user has a solid programming background. You may use Big-O notation, "
        "pseudocode, and standard CS terminology. Include concrete examples."
    ),
    "advanced": (
        "The user is an advanced researcher or developer. Use formal notation, "
        "provide mathematical derivations where applicable, reference key papers "
        "(e.g., Knuth & Moore 1975 for Alpha-Beta), and discuss edge cases."
    ),
}

# ── Template builders ────────────────────────────────────────────────────────

def _algo_label(algorithm: str | None, query: str) -> str:
    return algorithm if algorithm else f"the algorithm mentioned in: \"{query}\""


def build_explain_prompt(intent: Intent) -> tuple[str, str]:
    algo = _algo_label(intent.algorithm, intent.raw_query)
    system = f"{_SYSTEM_ROLE}\n\n{_EXPERTISE_PREAMBLE[intent.expertise_level]}"
    user = f"""{_COT_INSTRUCTION}

Explain **{algo}** using the following REQUIRED structure. Use these exact headings:

## Purpose
What problem does {algo} solve? Why was it invented?

## How It Works
Describe the core mechanism step-by-step.

## Concrete Example
Walk through a small game example (e.g., a 3×3 Tic-Tac-Toe position or a tiny game tree with 3–4 nodes). Show the algorithm running on it.

## When to Use It
List the types of games / problems where {algo} is the best choice, and when it is NOT the right choice.

## Time & Space Complexity
State the complexity in Big-O notation with a one-sentence justification.

## Key Takeaway
One memorable sentence summarising the essence of {algo}.

{_HALLUCINATION_GUARD}

User's original question: {intent.raw_query}"""
    return system, user


def build_pseudocode_prompt(intent: Intent) -> tuple[str, str]:
    algo = _algo_label(intent.algorithm, intent.raw_query)
    system = f"{_SYSTEM_ROLE}\n\n{_EXPERTISE_PREAMBLE[intent.expertise_level]}"
    user = f"""{_COT_INSTRUCTION}

Generate annotated pseudocode for **{algo}** using the following REQUIRED structure:

## Overview
One paragraph: what the pseudocode implements and its inputs/outputs.

## Pseudocode
```
<pseudocode here – use indentation, not a specific language>
```

## Line-by-Line Commentary
For each key section of the pseudocode (not every line – focus on non-obvious parts), explain what it does and WHY it is written that way.

## Common Implementation Pitfalls
List 3–5 mistakes developers often make when coding {algo} and how to avoid them.

## Python Skeleton (optional but recommended)
A minimal Python function stub (signatures + docstring + key comments) that a developer could fill in.

{_HALLUCINATION_GUARD}

User's original question: {intent.raw_query}"""
    return system, user


def build_walkthrough_prompt(intent: Intent) -> tuple[str, str]:
    algo = _algo_label(intent.algorithm, intent.raw_query)
    system = f"{_SYSTEM_ROLE}\n\n{_EXPERTISE_PREAMBLE[intent.expertise_level]}"
    user = f"""{_COT_INSTRUCTION}

Produce a step-by-step execution walkthrough of **{algo}** using the following REQUIRED structure:

## Setup
Define the game/problem state used for this walkthrough (e.g., a specific Tic-Tac-Toe board, a small game tree, a grid map). Draw or describe the initial state clearly using ASCII art or a numbered list.

## Step-by-Step Execution
Number each step. For each step:
- State the current node / position.
- State what decision the algorithm makes.
- Show the updated state (pruned branches, updated scores, opened nodes, etc.).
Continue until the algorithm terminates.

## Final Answer
What does the algorithm return / decide, and why?

## What This Demonstrates
Two or three key insights a student should take away from this specific walkthrough.

{_HALLUCINATION_GUARD}

User's original question: {intent.raw_query}"""
    return system, user


def build_compare_prompt(intent: Intent) -> tuple[str, str]:
    system = f"{_SYSTEM_ROLE}\n\n{_EXPERTISE_PREAMBLE[intent.expertise_level]}"
    user = f"""{_COT_INSTRUCTION}

The user wants a comparison based on: "{intent.raw_query}"

Identify the two (or more) algorithms being compared and produce the following REQUIRED structure:

## Summary
One paragraph introducing both algorithms and framing the comparison.

## Side-by-Side Comparison Table
| Property | Algorithm A | Algorithm B |
|---|---|---|
| Core idea | ... | ... |
| Game type | ... | ... |
| Time complexity | ... | ... |
| Space complexity | ... | ... |
| Handles chance? | ... | ... |
| Handles large branching? | ... | ... |
| Interpretability | ... | ... |
| Typical use case | ... | ... |

(Add or remove rows as needed.)

## When to Choose Each
Describe the decision rule: "Choose Algorithm A when … Choose Algorithm B when …"

## Key Insight
The single most important conceptual difference between the two algorithms.

{_HALLUCINATION_GUARD}"""
    return system, user


def build_complexity_prompt(intent: Intent) -> tuple[str, str]:
    algo = _algo_label(intent.algorithm, intent.raw_query)
    system = f"{_SYSTEM_ROLE}\n\n{_EXPERTISE_PREAMBLE[intent.expertise_level]}"
    user = f"""{_COT_INSTRUCTION}

Derive and explain the time and space complexity of **{algo}** using the following REQUIRED structure:

## Complexity Summary
State the final Big-O results upfront (time and space) for quick reference.

## Definitions
Define the variables used (b = branching factor, d = depth, n = nodes, etc.) in the context of {algo}.

## Time Complexity Derivation
Derive the time complexity step-by-step. Explain the reasoning behind each step (not just the final formula). Use a small recurrence or counting argument where applicable.

## Space Complexity Derivation
Derive the space complexity. Explain what is stored and why.

## Best / Average / Worst Cases
If applicable, show how complexity changes under different conditions (e.g., Alpha-Beta with optimal vs. worst-case move ordering).

## Practical Implications
What does this complexity mean in practice? At what values of b and d does the algorithm become infeasible?

## Historical Note (if relevant)
Reference the key paper(s) that proved these bounds (e.g., Knuth & Moore, 1975 for Alpha-Beta).

{_HALLUCINATION_GUARD}

User's original question: {intent.raw_query}"""
    return system, user


# ── Public API ───────────────────────────────────────────────────────────────

def build_prompt(intent: Intent) -> tuple[str, str]:
    """Return (system_prompt, user_prompt) for the given intent."""
    builders = {
        TaskType.EXPLAIN:     build_explain_prompt,
        TaskType.PSEUDOCODE:  build_pseudocode_prompt,
        TaskType.WALKTHROUGH: build_walkthrough_prompt,
        TaskType.COMPARE:     build_compare_prompt,
        TaskType.COMPLEXITY:  build_complexity_prompt,
    }
    builder = builders.get(intent.task_type, build_explain_prompt)
    return builder(intent)
