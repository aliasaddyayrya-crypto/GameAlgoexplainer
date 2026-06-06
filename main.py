"""
GameAlgoExplainer – LLM-Based AI Agent for Game Algorithm Explanation
University of Engineering and Technology, Taxila
AI Assignment-2 | 23-SE-76
"""

import sys
import os
from src.agent import GameAlgoAgent
from src.utils import print_banner, print_help


def main():
    print_banner()

    agent = GameAlgoAgent()

    if len(sys.argv) > 1:
        # Non-interactive: query passed as CLI argument
        query = " ".join(sys.argv[1:])
        result = agent.run(query)
        print(result)
        return

    # Interactive REPL mode
    print_help()
    print("\nType 'quit' or 'exit' to stop.\n")

    while True:
        try:
            user_input = input("You: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue

        if user_input.lower() in ("quit", "exit", "q"):
            print("Goodbye!")
            break

        if user_input.lower() in ("help", "?"):
            print_help()
            continue

        response = agent.run(user_input)
        print(f"\nAgent:\n{response}\n")
        print("-" * 60)


if __name__ == "__main__":
    main()
