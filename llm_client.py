"""
LLM Client – calls the Anthropic Claude API.

Falls back to a rich offline mock if:
  • anthropic package is not installed, OR
  • ANTHROPIC_API_KEY env variable is not set.

This ensures the agent can be demonstrated without a key.
"""

import os
import time
from typing import Optional

# ── Try to import Anthropic SDK ──────────────────────────────────────────────
try:
    import anthropic as _anthropic
    _SDK_AVAILABLE = True
except ImportError:
    _SDK_AVAILABLE = False


# ── Offline mock responses (one per task type) ───────────────────────────────

_MOCK_RESPONSES: dict[str, str] = {
    "explain": """## Purpose
Minimax is a **decision-making algorithm** used in two-player, zero-sum games (games where one player's gain equals the other's loss). It was introduced by Claude Shannon in 1950 and finds the **optimal move** by assuming both players play perfectly.

## How It Works
1. **Build a game tree** – expand all possible moves up to a depth limit *d*.
2. **Label leaf nodes** with a heuristic score (positive = good for MAX player, negative = good for MIN player).
3. **Backpropagate scores** upward:
   - At MAX nodes: choose the child with the *highest* score.
   - At MIN nodes: choose the child with the *lowest* score.
4. **Return the move** leading to the root's best score.

## Concrete Example
```
          MAX (X to move)
         /       \\
       MIN        MIN
      /   \\      /   \\
    +3    -2   +1    +5
```
- Right MIN node returns min(+1, +5) = **+1**
- Left MIN node returns min(+3, -2) = **-2**
- MAX root returns max(-2, +1) = **+1** → choose *right* branch

## When to Use It
✔ Perfect-information, two-player, zero-sum games (Chess, Tic-Tac-Toe, Checkers)
✘ Games with hidden information (Poker) — use Expectimax instead
✘ Games with huge branching factors (Go) — use MCTS instead

## Time & Space Complexity
| | Complexity |
|---|---|
| Time | O(b^d) — explores every node in the tree |
| Space | O(b·d) — stores one path from root to leaf at a time |

Where *b* = branching factor, *d* = search depth.

## Key Takeaway
Minimax guarantees the **best worst-case outcome**: it plays as if the opponent is always perfectly adversarial.""",

    "pseudocode": """## Overview
The following pseudocode implements the Minimax algorithm. It takes a game `state`, a `depth` limit, and a boolean `is_maximizing` flag. It returns the optimal score for the current player.

## Pseudocode
```
function MINIMAX(state, depth, is_maximizing):
    if depth == 0 or TERMINAL(state):
        return EVALUATE(state)

    if is_maximizing:
        best = -INFINITY
        for each move in LEGAL_MOVES(state):
            child = APPLY_MOVE(state, move)
            score = MINIMAX(child, depth - 1, False)
            best = MAX(best, score)
        return best
    else:
        best = +INFINITY
        for each move in LEGAL_MOVES(state):
            child = APPLY_MOVE(state, move)
            score = MINIMAX(child, depth - 1, True)
            best = MIN(best, score)
        return best
```

## Line-by-Line Commentary
| Line | Explanation |
|---|---|
| `if depth == 0 or TERMINAL(state)` | Base case: stop at leaves or game-over states |
| `EVALUATE(state)` | Heuristic function — e.g., material score in Chess |
| `best = -INFINITY` | Worst possible start for a maximizer |
| `MINIMAX(child, depth-1, False)` | Recurse, flipping player role |
| `best = MAX(best, score)` | Keep the highest score seen so far |

## Common Implementation Pitfalls
1. **Forgetting to flip `is_maximizing`** — causes both players to optimise in the same direction.
2. **Using a mutable state object** without copying — move/unmove bugs are subtle.
3. **Off-by-one depth** — depth=0 should return the heuristic, not recurse.
4. **Missing terminal check** — can crash or loop on finished games.
5. **Slow `LEGAL_MOVES`** — precompute or cache when possible.

## Python Skeleton
```python
import math

def minimax(state, depth: int, is_maximizing: bool) -> float:
    \"\"\"
    Return the optimal minimax score for the current player.

    Args:
        state: Any object with .is_terminal(), .legal_moves(), .apply(move)
        depth: Remaining search depth (stops at 0)
        is_maximizing: True if it is the MAX player's turn
    Returns:
        float: Best achievable score
    \"\"\"
    if depth == 0 or state.is_terminal():
        return state.evaluate()

    if is_maximizing:
        best = -math.inf
        for move in state.legal_moves():
            child = state.apply(move)
            best = max(best, minimax(child, depth - 1, False))
        return best
    else:
        best = math.inf
        for move in state.legal_moves():
            child = state.apply(move)
            best = min(best, minimax(child, depth - 1, True))
        return best
```""",

    "walkthrough": """## Setup
**Game:** Tic-Tac-Toe  
**Position:** X has just played centre. It is O's turn (O = minimiser).

```
  1 | 2 | 3
  ---------
  4 | X | 6
  ---------
  7 | 8 | 9
```
Depth limit: 2. Scores: X wins → +10, O wins → -10, draw → 0.

## Step-by-Step Execution

**Step 1 – Root (O's turn, MIN node)**
O's legal moves: corners {1,3,7,9} and edges {2,4,6,8}. We expand all 8.

**Step 2 – Expand move O→corner 1**
```
  O | 2 | 3
  ---------
  4 | X | 6
  ---------
  7 | 8 | 9
```
Now X's turn (MAX node). X's best reply: centre-adjacent edges. Evaluate: score = 0 (draw likely).

**Step 3 – Expand move O→edge 2**
```
  1 | O | 3
  ---------
  4 | X | 6
  ---------
  7 | 8 | 9
```
X replies to corner 1. Heuristic score = 0.

**Step 4 – MIN node collects scores**
After evaluating all O moves at depth=2:
| O's move | Backed-up score |
|---|---|
| Corner 1 | 0 |
| Edge 2 | 0 |
| Corner 3 | 0 |
| … | … |

MIN picks the lowest → **0** (any corner is equally good for O here).

## Final Answer
The algorithm returns **score = 0** and recommends O plays any corner. No immediate winning move exists for either side at depth 2.

## What This Demonstrates
1. **MIN always counters MAX** – O picks the move that minimises X's advantage.
2. **Depth limits matter** – a deeper search (depth=9) would find the true game-theoretic draw.
3. **Backpropagation** – leaf scores bubble upward correctly through alternating MAX/MIN layers.""",

    "compare": """## Summary
Minimax and Alpha-Beta Pruning solve the *same* problem — finding the optimal move in a two-player zero-sum game — but Alpha-Beta does it **faster** by skipping branches that cannot affect the final decision. Alpha-Beta is not a separate algorithm; it is an optimisation of Minimax.

## Side-by-Side Comparison Table
| Property | Minimax | Alpha-Beta Pruning |
|---|---|---|
| Core idea | Exhaustive game-tree search | Minimax + branch pruning via α/β bounds |
| Invented by | Shannon, 1950 | Newell & Simon ~1958; proved by Knuth & Moore, 1975 |
| Time complexity | O(b^d) | O(b^(d/2)) best case, O(b^d) worst case |
| Space complexity | O(b·d) | O(b·d) |
| Nodes explored | All nodes | ~50% fewer under optimal move ordering |
| Result quality | Optimal | **Identical to Minimax** (same answer, fewer nodes) |
| Handles chance? | No | No |
| Implementation complexity | Simple | Moderate (α/β tracking) |
| Move ordering sensitivity | None | High — better ordering → more pruning |
| Typical use case | Teaching, very small games | Chess engines, Checkers, Othello |

## When to Choose Each
**Choose Minimax when:**
- You are learning adversarial search for the first time.
- The game tree is tiny (Tic-Tac-Toe with ≤ 9 ply).
- Code simplicity is more important than speed.

**Choose Alpha-Beta Pruning when:**
- The branching factor *b* > 5 (Chess: b≈35, Go: b≈250).
- You need to search deeper within a time budget.
- Move ordering can be improved (e.g., captures first in Chess).

## Key Insight
Alpha-Beta produces **exactly the same move** as Minimax but can do so with the square root of the work under perfect move ordering — making depths of 12+ ply feasible in Chess engines instead of depth 6.""",

    "complexity": """## Complexity Summary
| Metric | Minimax | Alpha-Beta (best) | Alpha-Beta (worst) |
|---|---|---|---|
| Time | O(b^d) | O(b^(d/2)) | O(b^d) |
| Space | O(b·d) | O(b·d) | O(b·d) |

## Definitions
- **b** = branching factor (average legal moves per position; Chess ≈ 35)
- **d** = search depth (plies / half-moves)
- **n** = total nodes in the tree ≈ b^d

## Time Complexity Derivation — Minimax
At depth 0: 1 node  
At depth 1: b nodes  
At depth 2: b² nodes  
…  
At depth d: b^d nodes  

Total nodes explored = 1 + b + b² + … + b^d = **O(b^d)** (geometric series, dominated by last term).

## Time Complexity Derivation — Alpha-Beta
Under **optimal move ordering** (best move always examined first):

- MAX nodes: only 1 child needs full expansion; remaining b-1 are pruned → contributes b^(d/2) nodes.
- MIN nodes: symmetric argument.

Knuth & Moore (1975) proved:
```
T_best(b, d) = 2·b^(d/2) - 1   (d even)
             ≈ O(b^(d/2))
```
Under **random move ordering** the expected savings are b^(3d/4), and in the **worst case** (reverse-optimal ordering) no pruning occurs → O(b^d).

## Space Complexity Derivation
Minimax is depth-first recursive. At any point it stores exactly one path from root to the current leaf.  
Path length = d nodes; each node stores at most b children's references → **O(b·d)** space.  
Alpha-Beta uses the same DFS → same space complexity.

## Best / Average / Worst Cases
| Scenario | Condition | Alpha-Beta Time |
|---|---|---|
| Best case | Optimal move ordering | O(b^(d/2)) |
| Average case | Random ordering | O(b^(3d/4)) |
| Worst case | Worst possible ordering | O(b^d) = same as Minimax |

## Practical Implications
For Chess (b ≈ 35):

| Depth | Minimax nodes | Alpha-Beta (best) nodes |
|---|---|---|
| 4 | 1,500,625 | 1,225 |
| 6 | 1.8 × 10⁹ | 42,875 |
| 8 | 2.25 × 10¹² | 1,500,625 |

This is why modern Chess engines (e.g., Stockfish) can search depth 20+ with Alpha-Beta + move ordering but Minimax alone becomes infeasible past depth 8.

## Historical Note
The optimality of Alpha-Beta pruning under best-case ordering was formally proved by **Knuth & Moore (1975)** in *"An Analysis of Alpha-Beta Pruning"*, Artificial Intelligence, 6(4), 293–326 — one of the most cited papers in game AI.""",
}


# ── Client class ─────────────────────────────────────────────────────────────

class LLMClient:
    """Thin wrapper around the Anthropic API with offline fallback."""

    MODEL = "claude-sonnet-4-20250514"
    MAX_TOKENS = 2048

    def __init__(self):
        api_key = os.getenv("ANTHROPIC_API_KEY", "")
        self._use_real_api = False

        if self._use_real_api:
            self._client = _anthropic.Anthropic(api_key=api_key)
        else:
            self._client = None

    def call(
        self,
        system_prompt: str,
        user_prompt: str,
        task_type: str = "explain",
    ) -> str:
        """Call the LLM and return the response text."""
        start = time.time()

        if self._use_real_api:
            response = self._client.messages.create(
                model=self.MODEL,
                max_tokens=self.MAX_TOKENS,
                system=system_prompt,
                messages=[{"role": "user", "content": user_prompt}],
            )
            text = response.content[0].text
        else:
            # Offline mock — pick the closest canned response
            text = _MOCK_RESPONSES.get(task_type, _MOCK_RESPONSES["explain"])
            time.sleep(0.3)  # simulate latency

        elapsed = time.time() - start
        return text, round(elapsed, 2)
