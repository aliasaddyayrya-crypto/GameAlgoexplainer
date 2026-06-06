"""
GameAlgoAgent – the central orchestrator.

Pipeline:
  User query
      ↓
  Classifier  →  Intent(task_type, algorithm, expertise_level)
      ↓
  PromptBuilder  →  (system_prompt, user_prompt)
      ↓
  LLMClient  →  raw response text
      ↓
  ResponseFormatter  →  final printed output
"""

from src.classifier import classify, SUPPORTED_ALGORITHMS
from src.prompt_builder import build_prompt
from src.llm_client import LLMClient
from src.formatter import format_response


class GameAlgoAgent:
    """Task-oriented AI agent for game algorithm explanation."""

    def __init__(self):
        self._llm = LLMClient()
        self._history: list[dict] = []

    # ── Public entry point ───────────────────────────────────────────────────

    def run(self, query: str) -> str:
        """
        Process a user query end-to-end and return the formatted response.

        Steps:
          1. Classify intent
          2. Validate we can handle it
          3. Build task-specific prompt
          4. Call LLM
          5. Format and return
        """
        intent = classify(query)

        # Unsupported algorithm → helpful error
        if intent.algorithm is None and intent.task_type != "compare":
            # Try to recover by still sending the query to the LLM with a generic prompt
            pass  # proceed — LLM may infer algorithm from context

        system_prompt, user_prompt = build_prompt(intent)
        raw_response, elapsed = self._llm.call(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            task_type=intent.task_type,
        )

        # Log to history
        self._history.append({
            "query": query,
            "intent": intent,
            "response_length": len(raw_response),
            "elapsed_s": elapsed,
        })

        return format_response(intent, raw_response, elapsed)

    # ── Introspection helpers ────────────────────────────────────────────────

    def get_history(self) -> list[dict]:
        return list(self._history)

    def supported_algorithms(self) -> list[str]:
        return SUPPORTED_ALGORITHMS
