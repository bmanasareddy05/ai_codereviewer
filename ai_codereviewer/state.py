import reflex as rx
import ast
import difflib
from datetime import datetime
from ai_codereviewer.ai_suggester import AISuggester

# ─────────────────────────────────────────────────────────────────────────────
# BACKEND LOGIC: Parser and Analyzer
# ─────────────────────────────────────────────────────────────────────────────

class CodeParser:
    def __init__(self, code: str):
        self.code = code
        self.tree = None

    def parse(self):
        try:
            self.tree = ast.parse(self.code)
            return self.tree
        except SyntaxError as e:
            return {"error": str(e)}

    def format_code(self):
        try:
            if self.tree:
                return ast.unparse(self.tree)
            return self.code
        except Exception:
            return self.code

class AdvancedCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.used_vars = set()
        self.defined_vars = set()
        self.imports = set()
        self.violations = []
        self.score = 100

    def visit_Import(self, node):
        for alias in node.names:
            self.imports.add(alias.name)
        self.generic_visit(node)

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_vars.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
        self.generic_visit(node)

    def analyze(self, tree):
        self.visit(tree)
        unused_imports = [i for i in self.imports if i not in self.used_vars]
        unused_vars = [v for v in self.defined_vars if v not in self.used_vars]

        for i in unused_imports:
            self.violations.append(f"Unused import: {i}")
            self.score -= 10
        for v in unused_vars:
            self.violations.append(f"Unused variable: {v}")
            self.score -= 5

        # Logic for Complexity
        loop_count = sum(1 for n in ast.walk(tree) if isinstance(n, (ast.For, ast.While)))
        complexity = "O(n)" if loop_count > 0 else "O(1)"

        return {
            "violations": self.violations,
            "score": max(self.score, 0),
            "complexity": complexity
        }

# ─────────────────────────────────────────────────────────────────────────────
# DATA MODELS
# ─────────────────────────────────────────────────────────────────────────────

class HistoryEntry(rx.Base):
    entry_id: str
    timestamp: str
    code_snippet: str
    score: int
    violation_count: int
    complexity: str
    language: str

class ChatMessage(rx.Base):
    role: str
    content: str
    timestamp: str

# ─────────────────────────────────────────────────────────────────────────────
# APP STATE
# ─────────────────────────────────────────────────────────────────────────────

class AppState(rx.State):
    # --- Analyser page variables ---
    raw_code: str = ""
    improved_code: str = ""
    ai_recommendation: str = ""
    analysis_error: str = ""
    is_analyzing: bool = False
    active_tab: str = "violations"
    
    # Results
    violations: list[str] = []
    score: int = 0
    complexity: str = ""
    diff_lines: list[dict[str, str]] = [] # For the red/green side-by-side view
    
    # --- History and Chat variables (Required for history.py) ---
    history: list[HistoryEntry] = []
    chat_messages: list[ChatMessage] = []
    chat_input: str = ""
    is_chatting: bool = False

    # --- Event Handlers ---

    def set_raw_code(self, value: str):
        self.raw_code = value

    def set_active_tab(self, tab: str):
        self.active_tab = tab

    def set_chat_input(self, value: str):
        self.chat_input = value

    def clear_editor(self):
        """Resets all analysis results and clears the editor."""
        self.raw_code = ""
        self.improved_code = ""
        self.ai_recommendation = ""
        self.analysis_error = ""
        self.violations = []
        self.score = 0
        self.complexity = ""
        self.diff_lines = []

    def clear_history(self):
        """Deletes all saved history entries and chat."""
        self.history = []
        self.chat_messages = []

    async def send_chat(self):
        """Handles the AI Chat Assistant in history.py"""
        if not self.chat_input.strip():
            return

        # Add user message to UI
        user_msg = ChatMessage(
            role="user",
            content=self.chat_input,
            timestamp=datetime.now().strftime("%H:%M")
        )
        self.chat_messages = self.chat_messages + [user_msg]
        
        user_text = self.chat_input
        self.chat_input = ""
        self.is_chatting = True
        yield

        try:
            # Get response from AI using the Groq suggester
            suggester = AISuggester()
            context_prompt = f"The user is asking about their code: {self.raw_code}\n\nUser Question: {user_text}"
            response = suggester.generate_review(context_prompt)
            
            ai_msg = ChatMessage(
                role="assistant",
                content=response,
                timestamp=datetime.now().strftime("%H:%M")
            )
            self.chat_messages = self.chat_messages + [ai_msg]
        except Exception as e:
            error_msg = ChatMessage(role="assistant", content=f"Error: {str(e)}", timestamp="")
            self.chat_messages = self.chat_messages + [error_msg]
        finally:
            self.is_chatting = False

    async def analyze_code(self):
        """Main analysis function for analyzer.py"""
        if not self.raw_code.strip():
            self.analysis_error = "Please paste some code."
            return

        self.is_analyzing = True
        self.analysis_error = ""
        self.violations = []
        yield 

        try:
            # 1. AST Static Analysis
            parser = CodeParser(self.raw_code)
            tree = parser.parse()
            
            if isinstance(tree, dict) and "error" in tree:
                self.analysis_error = f"Syntax Error: {tree['error']}"
                return

            analyzer = AdvancedCodeAnalyzer()
            result = analyzer.analyze(tree)
            
            self.violations = result["violations"]
            self.score = result["score"]
            self.complexity = result["complexity"]
            self.improved_code = parser.format_code()

            # 2. Side-by-Side Diff Logic (ndiff creates + and - markers)
            diff = difflib.ndiff(
                self.raw_code.splitlines(), 
                self.improved_code.splitlines()
            )
            
            self.diff_lines = []
            for line in diff:
                if line.startswith('+ '):
                    self.diff_lines.append({"text": line[2:], "type": "added"})
                elif line.startswith('- '):
                    self.diff_lines.append({"text": line[2:], "type": "removed"})
                elif line.startswith('  '):
                    self.diff_lines.append({"text": line[2:], "type": "same"})

            # 3. AI Technical Review (Llama-3 via Groq)
            suggester = AISuggester()
            self.ai_recommendation = suggester.generate_review(self.raw_code)

            # 4. Save to History
            entry = HistoryEntry(
                entry_id=str(len(self.history) + 1),
                timestamp=datetime.now().strftime("%b %d, %H:%M"),
                code_snippet=self.raw_code[:50] + "...",
                score=self.score,
                violation_count=len(self.violations),
                complexity=self.complexity,
                language="Python"
            )
            self.history = [entry] + self.history

        except Exception as e:
            self.analysis_error = f"Analysis failed: {str(e)}"
        finally:
            self.is_analyzing = False