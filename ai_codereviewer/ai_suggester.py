import os
import re
import time
import json
import logging
import difflib
from langchain_groq import ChatGroq

logger = logging.getLogger(__name__)

LANGUAGE_LABELS = {
    "python":     "Python",
    "c":          "C",
    "cpp":        "C++",
    "java":       "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
}

LANGUAGE_NOTES = {
    "python":     "Check for Pythonic patterns, proper exception handling, and type hints.",
    "c":          "Pay attention to memory management, pointer safety, and buffer overflows.",
    "cpp":        "Pay attention to memory management, RAII, smart pointers, and undefined behaviour.",
    "java":       "Look for null safety, resource leaks, and proper exception handling.",
    "javascript": "Look for async/await correctness, type coercion issues, and scope problems.",
    "typescript": "Check type safety, proper use of generics, and avoid 'any' type.",
}


class AISuggester:
    def __init__(self):
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError(
                "GROQ_API_KEY environment variable not set. "
                "Run: export GROQ_API_KEY=your_key_here"
            )
        self.model = ChatGroq(
            model_name="llama-3.1-8b-instant",
            groq_api_key=api_key
        )

    def _invoke(self, messages: list, timeout: int = 45, retries: int = 2) -> str:
        """Shared retry wrapper for all model calls."""
        for attempt in range(1, retries + 1):
            try:
                response = self.model.invoke(messages, timeout=timeout)
                return response.content.strip()
            except Exception as e:
                logger.warning("Model call attempt %d/%d failed: %s", attempt, retries, e)
                if attempt < retries:
                    time.sleep(2 * attempt)
                else:
                    raise

    def generate_review(self, code: str, language: str = "python") -> str:
        lang_label = LANGUAGE_LABELS.get(language, language.capitalize())
        lang_note  = LANGUAGE_NOTES.get(language, "")
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a strict {lang_label} code reviewer. {lang_note}\n"
                    "Give a concise review covering:\n"
                    "1. Bugs and logical errors\n"
                    "2. Time and space complexity\n"
                    "3. Code quality issues\n"
                    "4. Specific improvements with examples\n"
                    "Be accurate and specific to the language."
                )
            },
            {"role": "user", "content": code}
        ]
        try:
            return self._invoke(messages)
        except Exception as e:
            return f"AI Review Failed: {str(e)}"

    def analyze_non_python(self, code: str, language: str) -> dict:
        """
        For C / C++ / Java / JS / TS.
        Makes three small focused calls instead of one giant JSON call:
          Call A → violations list + score  (simple JSON, no code inside)
          Call B → improved / fixed code    (plain text, no JSON wrapping)
          Call C → complexity info          (small JSON, no code inside)
        Then builds diff_lines from A+B results.
        """
        lang_label = LANGUAGE_LABELS.get(language, language.capitalize())

        violations, score       = self._get_violations_and_score(code, lang_label)
        improved_code           = self._get_improved_code(code, lang_label, violations)
        complexity, space, per_function, warnings = self._get_complexity(code, lang_label)
        diff_lines              = self._build_diff(code, improved_code)

        return {
            "violations":    violations,
            "score":         score,
            "complexity":    complexity,
            "space":         space,
            "improved_code": improved_code,
            "diff_lines":    diff_lines,
            "per_function":  per_function,
            "warnings":      warnings,
        }

    def _get_violations_and_score(self, code: str, lang_label: str):
        """
        Returns a list of violation strings and an int score.
        JSON is small here — no code inside — so it's reliable.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a strict {lang_label} static analyser.\n"
                    "Analyse the code for issues and respond with ONLY this JSON "
                    "(no markdown fences, no extra text):\n"
                    '{"violations": ["issue 1", "issue 2"], "score": <int 0-100>}\n\n'
                    "Each violation must be a short specific string like:\n"
                    "- 'Memory leak: ptr never freed'\n"
                    "- 'Unreachable code after return at line 12'\n"
                    "- 'Unused variable: result'\n"
                    "- 'Null pointer dereference risk at line 8'\n"
                    "Score 100 = perfect, deduct points per issue found."
                )
            },
            {"role": "user", "content": code}
        ]
        try:
            raw = self._invoke(messages)
            raw = self._strip_fences(raw)
            data = json.loads(raw)
            violations = [str(v) for v in data.get("violations", [])]
            score = int(data.get("score", 50))
            return violations, score
        except Exception as e:
            logger.warning("_get_violations_and_score failed: %s", e)
            return [f"Could not parse violations: {str(e)}"], 50

    def _get_improved_code(self, code: str, lang_label: str, violations: list) -> str:
        """
        Asks AI to return ONLY the fixed source code — plain text, no JSON.
        No JSON wrapping means no JSON escaping issues.
        """
        violations_text = "\n".join(f"- {v}" for v in violations) if violations else "None"
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are an expert {lang_label} developer.\n"
                    "The user will give you code with known issues.\n"
                    "Return ONLY the corrected source code — no explanation, "
                    "no markdown fences, no comments about what changed. "
                    "Just the raw fixed code exactly as it should be saved to a file."
                )
            },
            {
                "role": "user",
                "content": (
                    f"Fix all these issues in the code:\n{violations_text}\n\n"
                    f"Code:\n{code}"
                )
            }
        ]
        try:
            result = self._invoke(messages)
            return self._strip_fences(result)
        except Exception as e:
            logger.warning("_get_improved_code failed: %s", e)
            return code  # fallback: return original

    def _get_complexity(self, code: str, lang_label: str):
        """
        Returns overall time/space complexity, per-function breakdown, and warnings.
        JSON is small here — no code inside — so it's reliable.
        """
        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a {lang_label} complexity analyser.\n"
                    "Analyse the code complexity and respond with ONLY this JSON "
                    "(no markdown fences, no extra text):\n"
                    "{\n"
                    '  "time_complexity": "<Big-O>",\n'
                    '  "space_complexity": "<Big-O>",\n'
                    '  "per_function": [\n'
                    '    {"function": "<name>", "line": <int>, '
                    '"time_complexity": "<Big-O>", "space_complexity": "<Big-O>", '
                    '"cyclomatic_complexity": <int>, '
                    '"cyclomatic_risk": "<low risk|moderate risk|high risk|very high risk>"}\n'
                    "  ],\n"
                    '  "warnings": ["warning string if O(n^2) or higher"]\n'
                    "}"
                )
            },
            {"role": "user", "content": code}
        ]
        try:
            raw  = self._invoke(messages)
            raw  = self._strip_fences(raw)
            data = json.loads(raw)

            per_function = [
                {
                    "function":   str(fn.get("function", "unknown")),
                    "line":       str(fn.get("line", "?")),
                    "time":       str(fn.get("time_complexity", "O(n)")),
                    "space":      str(fn.get("space_complexity", "O(1)")),
                    "cyclomatic": str(fn.get("cyclomatic_complexity", "1")),
                    "risk":       str(fn.get("cyclomatic_risk", "low risk")),
                }
                for fn in data.get("per_function", [])
            ]
            warnings = [str(w) for w in data.get("warnings", [])]

            return (
                str(data.get("time_complexity",  "O(n)")),
                str(data.get("space_complexity", "O(1)")),
                per_function,
                warnings,
            )
        except Exception as e:
            logger.warning("_get_complexity failed: %s", e)
            return "O(n)", "O(1)", [], []

    def _strip_fences(self, text: str) -> str:
        """Remove markdown code fences if the model adds them."""
        text = text.strip()
        if text.startswith("```"):
            text = re.sub(r"^```[a-zA-Z]*\n?", "", text)
            text = re.sub(r"\n?```$",          "", text)
        return text.strip()

    def _build_diff(self, original: str, improved: str) -> list:
        """Build diff_lines list from original vs improved code."""
        diff_lines = []
        for line in difflib.ndiff(original.splitlines(), improved.splitlines()):
            if line.startswith("+ "):
                diff_lines.append({"text": line[2:], "type": "added"})
            elif line.startswith("- "):
                diff_lines.append({"text": line[2:], "type": "removed"})
            elif line.startswith("  "):
                diff_lines.append({"text": line[2:], "type": "same"})
        return diff_lines

    def generate_chat_response(
        self, user_question: str, code: str = "", language: str = "python"
    ) -> str:
        lang_label   = LANGUAGE_LABELS.get(language, language.capitalize())
        user_content = (
            f"Here is the {lang_label} code being discussed:\n"
            f"```{language}\n{code}\n```\n\nUser question: {user_question}"
        ) if code.strip() else user_question

        messages = [
            {
                "role": "system",
                "content": (
                    f"You are a helpful {lang_label} code assistant. "
                    "Answer questions about code clearly and concisely. "
                    "Use proper code formatting when showing examples."
                )
            },
            {"role": "user", "content": user_content}
        ]
        try:
            return self._invoke(messages)
        except Exception as e:
            return f"Error: {str(e)}"