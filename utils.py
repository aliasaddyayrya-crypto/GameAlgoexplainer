"""Utility functions for the CLI interface."""

BANNER = r"""
 ██████╗  █████╗ ███╗   ███╗███████╗     █████╗ ██╗      ██████╗  ██████╗
██╔════╝ ██╔══██╗████╗ ████║██╔════╝    ██╔══██╗██║     ██╔════╝ ██╔═══██╗
██║  ███╗███████║██╔████╔██║█████╗      ███████║██║     ██║  ███╗██║   ██║
██║   ██║██╔══██║██║╚██╔╝██║██╔══╝      ██╔══██║██║     ██║   ██║██║   ██║
╚██████╔╝██║  ██║██║ ╚═╝ ██║███████╗    ██║  ██║███████╗╚██████╔╝╚██████╔╝
 ╚═════╝ ╚═╝  ╚═╝╚═╝     ╚═╝╚══════╝    ╚═╝  ╚═╝╚══════╝ ╚═════╝  ╚═════╝
         ███████╗██╗  ██╗██████╗ ██╗      █████╗ ██╗███╗   ██╗███████╗██████╗
         ██╔════╝╚██╗██╔╝██╔══██╗██║     ██╔══██╗██║████╗  ██║██╔════╝██╔══██╗
         █████╗   ╚███╔╝ ██████╔╝██║     ███████║██║██╔██╗ ██║█████╗  ██████╔╝
         ██╔══╝   ██╔██╗ ██╔═══╝ ██║     ██╔══██║██║██║╚██╗██║██╔══╝  ██╔══██╗
         ███████╗██╔╝ ██╗██║     ███████╗██║  ██║██║██║ ╚████║███████╗██║  ██║
         ╚══════╝╚═╝  ╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝╚═╝╚═╝  ╚═══╝╚══════╝╚═╝  ╚═╝

  LLM-Based AI Agent for Game Algorithm Explanation
  University of Engineering and Technology, Taxila  |  AI Assignment-2  |  23-SE-76
"""

HELP_TEXT = """
SUPPORTED ALGORITHMS
─────────────────────────────────────────────────────────────────────────────
  • Minimax               • Alpha-Beta Pruning      • Monte Carlo Tree Search
  • A* Search             • Negamax                 • Expectimax

TASK TYPES (auto-detected from your query)
─────────────────────────────────────────────────────────────────────────────
  EXPLAIN      → "Explain Minimax"   "What is MCTS?"   "How does A* work?"
  PSEUDOCODE   → "Show me Alpha-Beta pseudocode"   "Write Minimax code"
  WALKTHROUGH  → "Walk me through Minimax"   "Step-by-step MCTS"
  COMPARE      → "Compare Minimax vs Alpha-Beta"   "Minimax vs MCTS difference"
  COMPLEXITY   → "What is the complexity of Alpha-Beta?"   "Derive Minimax Big-O"

EXPERTISE LEVELS (auto-detected)
─────────────────────────────────────────────────────────────────────────────
  Beginner    → include "simple", "like I'm 10", "beginner", "ELI5"
  Advanced    → include "derive", "proof", "formal", "research"
  Intermediate → (default)

EXAMPLE QUERIES
─────────────────────────────────────────────────────────────────────────────
  > Explain Minimax like I'm 10 years old
  > Show me Alpha-Beta pseudocode and explain why move ordering matters
  > Walk me through MCTS step by step
  > Compare Minimax vs Alpha-Beta Pruning
  > Derive the Big-O complexity of Alpha-Beta under optimal ordering
  > What is A* search and when should I use it?
  > Show Expectimax pseudocode
─────────────────────────────────────────────────────────────────────────────
"""


def print_banner():
    print(BANNER)


def print_help():
    print(HELP_TEXT)
