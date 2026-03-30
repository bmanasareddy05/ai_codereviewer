import reflex as rx
import difflib
from datetime import datetime

from ai_codereviewer.code_parser import CodeParser
from ai_codereviewer.error_detector import AdvancedCodeAnalyzer
from ai_codereviewer.ai_suggester import AISuggester
from ai_codereviewer.language_router import (
    detect_language_from_code,
    needs_python_analysis,
    get_display_name,
)

# ─────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────

class HistoryEntry(rx.Base):
    entry_id:        str
    timestamp:       str
    code_snippet:    str
    score:           int
    violation_count: int
    complexity:      str
    language:        str


class ChatMessage(rx.Base):
    role:      str
    content:   str
    timestamp: str


# ─────────────────────────────────────────────────────────────────────────────
# APP STATE
# ─────────────────────────────────────────────────────────────────────────────

class AppState(rx.State):

    # Analyser page
    raw_code:          str  = ""
    improved_code:     str  = ""
    ai_recommendation: str  = ""
    analysis_error:    str  = ""
    is_analyzing:      bool = False
    active_tab:        str  = "violations"
    detected_language: str  = "python"

    # Results
    violations:  list[str]            = []
    score:       int                  = 0
    complexity:  str                  = ""
    space_complexity: str             = ""
    diff_lines:  list[dict[str, str]] = []

    # Complexity breakdown
    complexity_per_function: list[dict[str, str]] = []
    complexity_warnings:     list[str]            = []

    # History and Chat
    history:       list[HistoryEntry] = []
    chat_messages: list[ChatMessage]  = []
    chat_input:    str                = ""
    is_chatting:   bool               = False

    # ── Event Handlers ────────────────────────────────────────────────────────

    def set_raw_code(self, value: str):
        self.raw_code = value
        # Update language badge live as user types
        self.detected_language = (
            detect_language_from_code(value) if value.strip() else "python"
        )

    def set_active_tab(self, tab: str):
        self.active_tab = tab

    def set_chat_input(self, value: str):
        self.chat_input = value

    def clear_editor(self):
        self.raw_code                = ""
        self.improved_code           = ""
        self.ai_recommendation       = ""
        self.analysis_error          = ""
        self.violations              = []
        self.score                   = 0
        self.complexity              = ""
        self.space_complexity        = ""
        self.complexity_per_function = []
        self.complexity_warnings     = []
        self.diff_lines              = []
        self.detected_language       = "python"

    def clear_history(self):
        self.history       = []
        self.chat_messages = []

    async def send_chat(self):
        """AI Chat Assistant — History page."""
        if not self.chat_input.strip():
            return

        user_msg = ChatMessage(
            role="user",
            content=self.chat_input,
            timestamp=datetime.now().strftime("%H:%M")
        )
        self.chat_messages = self.chat_messages + [user_msg]
        user_text       = self.chat_input
        self.chat_input = ""
        self.is_chatting = True
        yield

        try:
            suggester = AISuggester()
            response  = suggester.generate_chat_response(
                user_question=user_text,
                code=self.raw_code if self.raw_code.strip() else "",
                language=self.detected_language,
            )
            self.chat_messages = self.chat_messages + [
                ChatMessage(
                    role="assistant",
                    content=response,
                    timestamp=datetime.now().strftime("%H:%M")
                )
            ]
        except Exception as e:
            self.chat_messages = self.chat_messages + [
                ChatMessage(role="assistant", content=f"Error: {str(e)}", timestamp="")
            ]
        finally:
            self.is_chatting = False

    async def analyze_code(self):
        """
        Main analysis — called when user clicks Analyse.

        PYTHON flow:
          1. ast.parse()         → catch syntax errors
          2. AdvancedCodeAnalyzer → detect all violations + full complexity
          3. parser.fix_code()   → actually remove unused imports/vars from AST
          4. ast.unparse()       → produce the fixed improved code
          5. difflib.ndiff()     → build side-by-side diff
          6. AISuggester.generate_review() → AI technical review text

        NON-PYTHON flow (C / C++ / Java / JS / TS):
          1. AISuggester.analyze_non_python() → structured JSON from AI:
               violations, score, complexity, improved_code, diff, per_function
          2. AISuggester.generate_review()    → AI technical review text
        """
        if not self.raw_code.strip():
            self.analysis_error = "Please paste some code."
            return

        self.is_analyzing        = True
        self.analysis_error      = ""
        self.violations          = []
        self.complexity_per_function = []
        self.complexity_warnings = []
        yield

        try:
            lang         = detect_language_from_code(self.raw_code)
            self.detected_language = lang
            lang_display = get_display_name(lang)
            suggester    = AISuggester()

            # ── PYTHON ───────────────────────────────────────────────────
            if needs_python_analysis(lang):

                # Step 1: Parse
                parser = CodeParser(self.raw_code)
                tree   = parser.parse()
                if isinstance(tree, dict) and "error" in tree:
                    self.analysis_error = f"Syntax Error: {tree['error']}"
                    return

                # Step 2: Full static analysis
                analyzer = AdvancedCodeAnalyzer()
                result   = analyzer.analyze(tree)

                self.violations = result["violations"]
                self.score      = result["score"]

                complexity_data          = result["complexity"]
                self.complexity          = complexity_data["overall_time_complexity"]
                self.space_complexity    = complexity_data["overall_space_complexity"]
                self.complexity_warnings = complexity_data["warnings"]
                self.complexity_per_function = [
                    {
                        "function":   fn["function"],
                        "line":       str(fn["line"]),
                        "time":       fn["time_complexity"],
                        "space":      fn["space_complexity"],
                        "cyclomatic": str(fn["cyclomatic_complexity"]),
                        "risk":       fn["cyclomatic_risk"],
                    }
                    for fn in complexity_data["per_function"]
                ]

                # Step 3 + 4: Fix code — parser.fix_code() removes
                # unused imports and unused variables from the AST,
                # then ast.unparse() produces the corrected source
                self.improved_code = parser.fix_code(
                    unused_imports=result["unused_imports"],
                    unused_variables=result["unused_variables"],
                )

                # Step 5: Diff original vs fixed
                diff = difflib.ndiff(
                    self.raw_code.splitlines(),
                    self.improved_code.splitlines()
                )
                self.diff_lines = []
                for line in diff:
                    if line.startswith("+ "):
                        self.diff_lines.append({"text": line[2:], "type": "added"})
                    elif line.startswith("- "):
                        self.diff_lines.append({"text": line[2:], "type": "removed"})
                    elif line.startswith("  "):
                        self.diff_lines.append({"text": line[2:], "type": "same"})

                # Step 6: AI review of original code
                self.ai_recommendation = suggester.generate_review(
                    code=self.raw_code,
                    language=lang,
                )

            # ── NON-PYTHON (C / C++ / Java / JS / TS) ────────────────────
            else:
                # AI does everything: violations, score, complexity,
                # improved code, diff, per-function breakdown
                ai_result = suggester.analyze_non_python(
                    code=self.raw_code,
                    language=lang,
                )

                self.violations              = ai_result["violations"]
                self.score                   = ai_result["score"]
                self.complexity              = ai_result["complexity"]
                self.space_complexity        = ai_result["space"]
                self.improved_code           = ai_result["improved_code"]
                self.diff_lines              = ai_result["diff_lines"]
                self.complexity_per_function = ai_result["per_function"]
                self.complexity_warnings     = ai_result["warnings"]

                # Separate plain-text AI review for the review box
                self.ai_recommendation = suggester.generate_review(
                    code=self.raw_code,
                    language=lang,
                )

            # ── Save to History ───────────────────────────────────────────
            self.history = [
                HistoryEntry(
                    entry_id=str(len(self.history) + 1),
                    timestamp=datetime.now().strftime("%b %d, %H:%M"),
                    code_snippet=self.raw_code[:50] + "...",
                    score=self.score,
                    violation_count=len(self.violations),
                    complexity=self.complexity,
                    language=lang_display,
                )
            ] + self.history

        except Exception as e:
            self.analysis_error = f"Analysis failed: {str(e)}"
        finally:
            self.is_analyzing = False