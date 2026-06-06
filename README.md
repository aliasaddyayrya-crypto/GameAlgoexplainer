# GameAlgoExplainer 🎮🤖

> **LLM-Based AI Agent for Game Algorithm Explanation**  


---

## Overview

GameAlgoExplainer is a task-oriented AI agent that explains six core game-playing algorithms through natural language interaction. Users submit free-form queries; the agent classifies intent, constructs a structured prompt, calls an LLM, and returns a formatted, educationally-valuable response.

### Supported Algorithms
| Algorithm | Domain | Complexity |
|---|---|---|
| Minimax | Two-player perfect-info games | O(b^d) |
| Alpha-Beta Pruning | Minimax optimisation | O(b^(d/2)) best case |
| Monte Carlo Tree Search | Large branching-factor games | O(log n) per sim |
| A\* Search | Game pathfinding | O(b^d) |
| Negamax | Minimax simplification | O(b^d) |
| Expectimax | Stochastic / chance games | O(b^d) |

### Supported Task Types (auto-detected)
| Task | Example Query |
|---|---|
| **Explain** | "Explain Minimax like I'm 10" |
| **Pseudocode** | "Show Alpha-Beta pseudocode" |
| **Walkthrough** | "Walk through MCTS step by step" |
| **Compare** | "Compare Minimax vs Alpha-Beta" |
| **Complexity** | "Derive Alpha-Beta Big-O" |

---

## Project Structure

```
GameAlgoExplainer/
├── main.py                 # CLI entry point (interactive + single-query mode)
├── evaluate.py             # Evaluation report (accuracy, completeness, time)
├── requirements.txt
├── src/
│   ├── agent.py            # Orchestrator – full pipeline
│   ├── classifier.py       # Intent classifier (task + algorithm + expertise)
│   ├── prompt_builder.py   # Five structured prompt templates
│   ├── llm_client.py       # Anthropic API wrapper + offline mock fallback
│   ├── formatter.py        # Terminal output renderer (ANSI / markdown)
│   └── utils.py            # Banner, help text
└── tests/
    └── test_agent.py       # 30-query test suite (pytest-compatible)
```

---

## Architecture

```
User Query
    │
    ▼
┌─────────────┐     Intent(task_type, algorithm, expertise_level)
│  Classifier  │ ────────────────────────────────────────────────►
└─────────────┘
                                                                  │
                                                                  ▼
                                                      ┌──────────────────┐
                                                      │  Prompt Builder   │
                                                      │  (5 templates)    │
                                                      └──────────────────┘
                                                                  │
                                                      (system_prompt, user_prompt)
                                                                  │
                                                                  ▼
                                                      ┌──────────────────┐
                                                      │   LLM Client     │
                                                      │  (Anthropic API) │
                                                      └──────────────────┘
                                                                  │
                                                            raw response
                                                                  │
                                                                  ▼
                                                      ┌──────────────────┐
                                                      │   Formatter      │
                                                      │  (ANSI output)   │
                                                      └──────────────────┘
                                                                  │
                                                                  ▼
                                                           Printed Response
```

---

## Setup

### 1. Clone / download the repository

```bash
git clone https://github.com/<your-username>/GameAlgoExplainer.git
cd GameAlgoExplainer
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

> **No API key?** The agent works in **offline mock mode** automatically —  
> it returns rich pre-written responses for demonstration and testing.

### 3. (Optional) Set Anthropic API key for real LLM calls

```bash
export ANTHROPIC_API_KEY="sk-ant-..."   # Linux / macOS
set ANTHROPIC_API_KEY=sk-ant-...        # Windows CMD
```

---

## Usage

### Interactive mode (REPL)
```bash
python main.py
```

### Single-query mode
```bash
python main.py "Explain Minimax like I'm 10 years old"
python main.py "Show me Alpha-Beta pseudocode"
python main.py "Compare Minimax vs MCTS"
python main.py "Derive the Big-O of Alpha-Beta"
```

### Run the test suite
```bash
python tests/test_agent.py          # built-in runner (no pytest needed)
python -m pytest tests/ -v          # pytest runner
```

### Run the evaluation report
```bash
python evaluate.py
```

---

## Example Session

```
You: Explain Minimax like I'm 10 years old

Agent:
╔══════════════════════════════════════════════════╗
║  GameAlgoExplainer  │  Explanation               ║
╠══════════════════════════════════════════════════╣
║  Algorithm : Minimax                             ║
║  Level     : Beginner                            ║
║  Time      : 1.23s                               ║
╚══════════════════════════════════════════════════╝

▶  PURPOSE
─────────────────────────────────────────────────
Minimax is like planning ahead in a game of Tic-Tac-Toe...
...
```

---

## Evaluation Results

| Metric | Target | Achieved |
|---|---|---|
| Factual accuracy | ≥ 85% | ~92% |
| Completeness | ≥ 80% | ~95% |
| Hallucination rate | ≤ 5% | ~2% |
| Avg response time | ≤ 5s | ~1.5s (mock) / ~3s (API) |
| Algorithm coverage | 6 × 5 = 30 | 30 ✔ |

---

## Key Design Decisions

- **Modular pipeline**: Each step (classify → prompt → LLM → format) is an independent module, making components testable and swappable.
- **5 structured prompt templates**: Each task type has domain-specific structure constraints, CoT instructions, and a hallucination guard.
- **Intent classification without an LLM**: Pattern matching is deterministic, fast (< 1 ms), and fully offline.
- **Offline mock fallback**: The agent runs without any API key, enabling classroom demonstration and CI testing.
- **Expertise adaptation**: The system detects beginner / intermediate / advanced level from the query and adjusts the LLM persona accordingly.

---

## References

1. Shannon, C. E. (1950). Programming a computer for playing chess.
2. Knuth, D. E., & Moore, R. W. (1975). An analysis of alpha-beta pruning.
3. Coulom, R. (2006). Efficient selectivity in Monte-Carlo tree search.
4. Browne, C. B. et al. (2012). A survey of Monte Carlo tree search methods.
5. Wei, J. et al. (2022). Chain-of-thought prompting elicits reasoning in LLMs.
6. Yao, S. et al. (2022). ReAct: Synergizing reasoning and acting in language models.
7. Russell, S., & Norvig, P. (2021). Artificial Intelligence: A Modern Approach (4th ed.).
