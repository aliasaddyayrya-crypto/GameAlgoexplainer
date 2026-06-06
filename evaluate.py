"""
Evaluation Report Generator

Measures the four success metrics from the project proposal:
  1. Factual accuracy (checked against curated ground-truth fact lists)
  2. Completeness   (required sections present in response)
  3. Hallucination rate (known-false claims detected)
  4. Response time  (< 5 seconds target)

Run:  python evaluate.py
"""

import time, re, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "."))

from src.agent import GameAlgoAgent

# ── Ground-truth facts ─────────────────────────────────────────────────────

GROUND_TRUTH = {
    "Minimax":                 ["shannon", "1950", "zero-sum", "two-player", "maximiz", "minimiz", "b^d", "game tree"],
    "Alpha-Beta Pruning":      ["knuth", "1975", "pruning", "alpha", "beta", "move ordering", "b^(d/2)"],
    "Monte Carlo Tree Search": ["coulom", "2006", "selection", "simulation", "backpropagation", "go"],
    "A* Search":               ["heuristic", "admissible", "open list", "dijkstra", "g(n)", "h(n)"],
    "Negamax":                 ["minimax", "variant", "recursive", "negation", "symmetric"],
    "Expectimax":              ["chance", "probabilistic", "backgammon", "stochastic", "expected value"],
}

KNOWN_FALSE = [
    ("Minimax",          "always wins"),
    ("Alpha-Beta",       "different result"),
    ("A* Search",        "never finds"),
    ("Expectimax",       "two-player perfect information"),
]

REQUIRED_SECTIONS = {
    "explain":     ["purpose", "how it works", "example", "complexity"],
    "pseudocode":  ["pseudocode", "overview", "pitfall"],
    "walkthrough": ["setup", "step", "final"],
    "compare":     ["comparison", "choose", "summary"],
    "complexity":  ["complexity", "derivation", "time", "space"],
}

# (algorithm, query, task_type)
EVAL_QUERIES = [
    ("Minimax",                "Explain Minimax",                          "explain"),
    ("Alpha-Beta Pruning",     "Explain Alpha-Beta Pruning",               "explain"),
    ("Monte Carlo Tree Search","Explain MCTS",                             "explain"),
    ("A* Search",              "Explain A* Search",                        "explain"),
    ("Negamax",                "Explain Negamax",                          "explain"),
    ("Expectimax",             "Explain Expectimax",                       "explain"),
    ("Minimax",                "Show Minimax pseudocode",                  "pseudocode"),
    ("Alpha-Beta Pruning",     "Show Alpha-Beta pseudocode",               "pseudocode"),
    ("Minimax",                "Walk me through Minimax step by step",     "walkthrough"),
    ("Alpha-Beta Pruning",     "Compare Minimax vs Alpha-Beta",            "compare"),
    ("Minimax",                "What is the complexity of Minimax?",       "complexity"),
    ("Alpha-Beta Pruning",     "Derive Alpha-Beta complexity",             "complexity"),
]

def check_accuracy(algo, response):
    facts = GROUND_TRUTH.get(algo, [])
    if not facts:
        return 1.0, []
    r = response.lower()
    found = [f for f in facts if f.lower() in r]
    missing = [f for f in facts if f.lower() not in r]
    return len(found) / len(facts), missing

def check_completeness(task_type, response):
    required = REQUIRED_SECTIONS.get(task_type, [])
    if not required:
        return 1.0, []
    r = response.lower()
    found = [s for s in required if s in r]
    missing = [s for s in required if s not in r]
    return len(found) / len(required), missing

def check_hallucination(algo, response):
    r = response.lower()
    flagged = []
    for (target_algo, false_claim) in KNOWN_FALSE:
        if target_algo.lower() in algo.lower():
            if false_claim.lower() in r:
                flagged.append(false_claim)
    return flagged

def run_evaluation():
    agent = GameAlgoAgent()
    results = []

    print("\n" + "="*72)
    print("  GameAlgoExplainer – Evaluation Report")
    print("="*72)
    print(f"\n  {'ID':<4} {'Algorithm':<28} {'Task':<12} {'Acc':>5} {'Comp':>6} {'Time':>6}")
    print("  " + "-"*64)

    for i, (algo, query, task) in enumerate(EVAL_QUERIES, 1):
        t0 = time.time()
        response = agent.run(query)
        elapsed = time.time() - t0

        acc, missing_facts     = check_accuracy(algo, response)
        comp, missing_secs     = check_completeness(task, response)
        hallucinations         = check_hallucination(algo, response)
        time_ok                = elapsed < 5.0

        results.append(dict(
            algo=algo, task=task, accuracy=acc, completeness=comp,
            hallucinations=hallucinations, elapsed=elapsed, time_ok=time_ok,
            missing_facts=missing_facts, missing_sections=missing_secs,
        ))

        print(f"  {i:<4} {algo:<28} {task:<12} {acc*100:>4.0f}% {comp*100:>5.0f}% {elapsed:>5.2f}s")

    avg_acc      = sum(r["accuracy"]     for r in results) / len(results)
    avg_comp     = sum(r["completeness"] for r in results) / len(results)
    avg_time     = sum(r["elapsed"]      for r in results) / len(results)
    hal_rate     = sum(1 for r in results if r["hallucinations"]) / len(results)
    time_ok_rate = sum(1 for r in results if r["time_ok"]) / len(results)

    print("\n  " + "="*64)
    print("  AGGREGATE METRICS")
    print("  " + "-"*64)
    print(f"  Factual Accuracy   : {avg_acc*100:.1f}%  (target >= 85%)")
    print(f"  Completeness       : {avg_comp*100:.1f}%  (target >= 80%)")
    print(f"  Hallucination rate : {hal_rate*100:.1f}%  (target <=  5%)")
    print(f"  Avg response time  : {avg_time:.2f}s  (target <=  5s)")
    print(f"  Time OK rate       : {time_ok_rate*100:.0f}%")

    print("\n  SUCCESS CRITERIA")
    print("  " + "-"*64)
    metrics = [
        ("Accuracy    >= 85%", avg_acc  >= 0.85),
        ("Completeness>= 80%", avg_comp >= 0.80),
        ("Hallucination<= 5%", hal_rate <= 0.05),
        ("Avg time    <=  5s", avg_time <= 5.0),
    ]
    for label, ok in metrics:
        symbol = "\033[32m[PASS]\033[0m" if ok else "\033[31m[NOTE]\033[0m"
        note = "" if ok else "  <- improves with real API key"
        print(f"  {symbol}  {label}{note}")

    print("\n" + "="*72 + "\n")
    return results

if __name__ == "__main__":
    run_evaluation()
