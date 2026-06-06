"""
Test Suite – 30 algorithm queries covering all 6 algorithms × 5 task types.
Validates: intent detection, algorithm detection, expertise detection,
           response non-empty, response time < 10s.

Run with:  python -m pytest tests/test_agent.py -v
       or: python tests/test_agent.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from src.classifier import classify, TaskType
from src.agent import GameAlgoAgent


# ── Test cases ────────────────────────────────────────────────────────────────

TEST_QUERIES = [
    # ── EXPLAIN (6 queries, one per algorithm) ──────────────────────────────
    {
        "id": "T01", "query": "Explain Minimax like I'm 10 years old",
        "expected_task": TaskType.EXPLAIN,
        "expected_algo": "Minimax",
        "expected_level": "beginner",
    },
    {
        "id": "T02", "query": "What is Alpha-Beta Pruning?",
        "expected_task": TaskType.EXPLAIN,
        "expected_algo": "Alpha-Beta Pruning",
        "expected_level": "intermediate",
    },
    {
        "id": "T03", "query": "Explain Monte Carlo Tree Search to me",
        "expected_task": TaskType.EXPLAIN,
        "expected_algo": "Monte Carlo Tree Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T04", "query": "How does A* search work for game pathfinding?",
        "expected_task": TaskType.EXPLAIN,
        "expected_algo": "A* Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T05", "query": "Tell me about the Negamax algorithm",
        "expected_task": TaskType.EXPLAIN,
        "expected_algo": "Negamax",
        "expected_level": "intermediate",
    },
    {
        "id": "T06", "query": "Describe Expectimax for a beginner student",
        "expected_task": TaskType.EXPLAIN,
        "expected_algo": "Expectimax",
        "expected_level": "beginner",
    },

    # ── PSEUDOCODE (6 queries) ───────────────────────────────────────────────
    {
        "id": "T07", "query": "Show me Minimax pseudocode",
        "expected_task": TaskType.PSEUDOCODE,
        "expected_algo": "Minimax",
        "expected_level": "intermediate",
    },
    {
        "id": "T08", "query": "Show me Alpha-Beta pseudocode and explain why move ordering matters",
        "expected_task": TaskType.PSEUDOCODE,
        "expected_algo": "Alpha-Beta Pruning",
        "expected_level": "intermediate",
    },
    {
        "id": "T09", "query": "Write MCTS code with UCB1 selection",
        "expected_task": TaskType.PSEUDOCODE,
        "expected_algo": "Monte Carlo Tree Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T10", "query": "Show A* pseudocode with open/closed lists",
        "expected_task": TaskType.PSEUDOCODE,
        "expected_algo": "A* Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T11", "query": "Implement Negamax with alpha-beta",
        "expected_task": TaskType.PSEUDOCODE,
        "expected_algo": "Negamax",
        "expected_level": "intermediate",
    },
    {
        "id": "T12", "query": "Write Expectimax algorithm code",
        "expected_task": TaskType.PSEUDOCODE,
        "expected_algo": "Expectimax",
        "expected_level": "intermediate",
    },

    # ── WALKTHROUGH (6 queries) ──────────────────────────────────────────────
    {
        "id": "T13", "query": "Walk me through Minimax step by step on Tic-Tac-Toe",
        "expected_task": TaskType.WALKTHROUGH,
        "expected_algo": "Minimax",
        "expected_level": "intermediate",
    },
    {
        "id": "T14", "query": "Trace Alpha-Beta pruning on a small game tree",
        "expected_task": TaskType.WALKTHROUGH,
        "expected_algo": "Alpha-Beta Pruning",
        "expected_level": "intermediate",
    },
    {
        "id": "T15", "query": "Step-by-step MCTS on a Go-like position",
        "expected_task": TaskType.WALKTHROUGH,
        "expected_algo": "Monte Carlo Tree Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T16", "query": "Walk through A* on a grid map example",
        "expected_task": TaskType.WALKTHROUGH,
        "expected_algo": "A* Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T17", "query": "Trace Negamax execution on a game tree",
        "expected_task": TaskType.WALKTHROUGH,
        "expected_algo": "Negamax",
        "expected_level": "intermediate",
    },
    {
        "id": "T18", "query": "Walk through Expectimax on a Backgammon example",
        "expected_task": TaskType.WALKTHROUGH,
        "expected_algo": "Expectimax",
        "expected_level": "intermediate",
    },

    # ── COMPARE (6 queries) ──────────────────────────────────────────────────
    {
        "id": "T19", "query": "Compare Minimax vs Alpha-Beta Pruning",
        "expected_task": TaskType.COMPARE,
        "expected_algo": None,  # compare may not pin one algo
        "expected_level": "intermediate",
    },
    {
        "id": "T20", "query": "What is the difference between MCTS and Minimax?",
        "expected_task": TaskType.COMPARE,
        "expected_algo": None,
        "expected_level": "intermediate",
    },
    {
        "id": "T21", "query": "Minimax vs Negamax – which is better?",
        "expected_task": TaskType.COMPARE,
        "expected_algo": None,
        "expected_level": "intermediate",
    },
    {
        "id": "T22", "query": "Differences between A* and MCTS for pathfinding",
        "expected_task": TaskType.COMPARE,
        "expected_algo": None,
        "expected_level": "intermediate",
    },
    {
        "id": "T23", "query": "Compare Expectimax vs Minimax for stochastic games",
        "expected_task": TaskType.COMPARE,
        "expected_algo": None,
        "expected_level": "intermediate",
    },
    {
        "id": "T24", "query": "Alpha-Beta vs MCTS – formal comparison",
        "expected_task": TaskType.COMPARE,
        "expected_algo": None,
        "expected_level": "advanced",
    },

    # ── COMPLEXITY (6 queries) ───────────────────────────────────────────────
    {
        "id": "T25", "query": "What is the time complexity of Minimax?",
        "expected_task": TaskType.COMPLEXITY,
        "expected_algo": "Minimax",
        "expected_level": "intermediate",
    },
    {
        "id": "T26", "query": "Derive the branching factor reduction for Alpha-Beta under optimal ordering",
        "expected_task": TaskType.COMPLEXITY,
        "expected_algo": "Alpha-Beta Pruning",
        "expected_level": "advanced",
    },
    {
        "id": "T27", "query": "Big-O complexity of MCTS per simulation",
        "expected_task": TaskType.COMPLEXITY,
        "expected_algo": "Monte Carlo Tree Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T28", "query": "What is the space complexity of A* search?",
        "expected_task": TaskType.COMPLEXITY,
        "expected_algo": "A* Search",
        "expected_level": "intermediate",
    },
    {
        "id": "T29", "query": "Derive time complexity proof for Negamax",
        "expected_task": TaskType.COMPLEXITY,
        "expected_algo": "Negamax",
        "expected_level": "advanced",
    },
    {
        "id": "T30", "query": "O(b^d) analysis of Expectimax for stochastic games",
        "expected_task": TaskType.COMPLEXITY,
        "expected_algo": "Expectimax",
        "expected_level": "intermediate",
    },
]


# ── Test runner ───────────────────────────────────────────────────────────────

def run_tests(verbose: bool = True) -> dict:
    agent = GameAlgoAgent()
    results = {"passed": 0, "failed": 0, "errors": [], "details": []}

    print(f"\n{'='*70}")
    print("  GameAlgoExplainer – Test Suite (30 queries)")
    print(f"{'='*70}\n")

    for tc in TEST_QUERIES:
        qid = tc["id"]
        query = tc["query"]

        try:
            # --- Intent classification checks ---
            intent = classify(query)
            task_ok = intent.task_type == tc["expected_task"]
            level_ok = intent.expertise_level == tc["expected_level"]
            algo_ok = (
                tc["expected_algo"] is None or
                intent.algorithm == tc["expected_algo"]
            )

            # --- Agent response check ---
            t0 = time.time()
            response = agent.run(query)
            elapsed = time.time() - t0

            response_ok = len(response.strip()) > 50
            time_ok = elapsed < 10.0

            passed = task_ok and level_ok and algo_ok and response_ok and time_ok

            detail = {
                "id": qid,
                "query": query[:60],
                "passed": passed,
                "task_ok": task_ok,
                "algo_ok": algo_ok,
                "level_ok": level_ok,
                "response_ok": response_ok,
                "time_ok": time_ok,
                "elapsed": round(elapsed, 2),
                "detected_task": intent.task_type,
                "detected_algo": intent.algorithm,
                "detected_level": intent.expertise_level,
            }
            results["details"].append(detail)

            if passed:
                results["passed"] += 1
                status = "\033[32m✔ PASS\033[0m"
            else:
                results["failed"] += 1
                status = "\033[31m✘ FAIL\033[0m"
                results["errors"].append(detail)

            if verbose:
                print(f"  {status}  {qid}  [{elapsed:.2f}s]  {query[:55]}")
                if not passed:
                    if not task_ok:
                        print(f"         task: expected={tc['expected_task']} got={intent.task_type}")
                    if not algo_ok:
                        print(f"         algo: expected={tc['expected_algo']} got={intent.algorithm}")
                    if not level_ok:
                        print(f"         level: expected={tc['expected_level']} got={intent.expertise_level}")

        except Exception as exc:
            results["failed"] += 1
            results["errors"].append({"id": qid, "error": str(exc)})
            if verbose:
                print(f"  \033[31m✘ ERROR\033[0m  {qid}  {query[:50]}  →  {exc}")

    total = results["passed"] + results["failed"]
    pct = 100 * results["passed"] / total if total else 0

    print(f"\n{'='*70}")
    print(f"  Results: {results['passed']}/{total} passed  ({pct:.1f}%)")
    print(f"{'='*70}\n")

    return results


# ── pytest-compatible individual tests ────────────────────────────────────────

def _make_test(tc):
    def test_fn():
        intent = classify(tc["query"])
        assert intent.task_type == tc["expected_task"], (
            f"{tc['id']}: task {intent.task_type!r} != {tc['expected_task']!r}"
        )
        assert intent.expertise_level == tc["expected_level"], (
            f"{tc['id']}: level {intent.expertise_level!r} != {tc['expected_level']!r}"
        )
        if tc["expected_algo"] is not None:
            assert intent.algorithm == tc["expected_algo"], (
                f"{tc['id']}: algo {intent.algorithm!r} != {tc['expected_algo']!r}"
            )
    test_fn.__name__ = f"test_{tc['id'].lower()}"
    return test_fn


# Dynamically create pytest-compatible test functions at module level
for _tc in TEST_QUERIES:
    globals()[f"test_{_tc['id'].lower()}"] = _make_test(_tc)


if __name__ == "__main__":
    run_tests(verbose=True)
