import ast
import logging

logger = logging.getLogger(__name__)


class _CodeFixer(ast.NodeTransformer):
    """
    Walks the AST and removes nodes flagged as unused by AdvancedCodeAnalyzer.
    Only removes things it is certain are safe to remove.
    """

    def __init__(self, unused_imports: list, unused_variables: list):
        self.unused_imports   = set(unused_imports)
        self.unused_variables = set(unused_variables)

    def visit_Import(self, node):
        """Drop individual aliases from  import os, sys  if unused."""
        kept = [
            alias for alias in node.names
            if (alias.asname or alias.name) not in self.unused_imports
        ]
        if not kept:
            return None         
        node.names = kept
        return node

    def visit_ImportFrom(self, node):
        """Drop individual aliases from  from x import y, z  if unused."""
        kept = [
            alias for alias in node.names
            if (alias.asname or alias.name) not in self.unused_imports
        ]
        if not kept:
            return None
        node.names = kept
        return node

    def visit_Assign(self, node):
        """
        Remove  x = <expr>  when x is unused.
        Only removes single-target, single-name assignments to stay safe
        (won't touch tuple unpacking or chained assignments).
        """
        if (
            len(node.targets) == 1
            and isinstance(node.targets[0], ast.Name)
            and node.targets[0].id in self.unused_variables
        ):
            return None
        return node


class CodeParser:
    def __init__(self, code: str):
        self.code  = code
        self.tree  = None
        self.error = None   

    def parse(self):
        try:
            self.tree  = ast.parse(self.code)
            self.error = None
            return self.tree
        except SyntaxError as e:
            self.error = str(e)
            return {"error": str(e), "status": "Syntax Error"}

    def has_error(self) -> bool:
        return self.error is not None

    def get_ast_dump(self):
        if self.has_error():
            logger.warning("get_ast_dump() called but parse failed: %s", self.error)
            return None
        return ast.dump(self.tree, indent=4) if self.tree else None

    def format_code(self):
        """Plain reformat via ast.unparse — normalises whitespace only."""
        if self.has_error():
            logger.warning("format_code() called but parse failed: %s", self.error)
            return self.code
        try:
            return ast.unparse(self.tree) if self.tree else self.code
        except Exception as e:
            logger.error("format_code() failed: %s", e)
            return self.code

    def fix_code(self, unused_imports: list, unused_variables: list) -> str:
        """
        Actually removes unused imports and unused variables from the AST,
        then unparses to produce corrected source code.

        This is what fills the 'Improved Code' tab — it genuinely fixes
        the issues that AdvancedCodeAnalyzer detected, unlike format_code()
        which only reformats whitespace.

        Falls back to format_code() if the fix transform fails.
        """
        if self.has_error() or not self.tree:
            return self.code
        try:
            fixer      = _CodeFixer(unused_imports, unused_variables)
            fixed_tree = fixer.visit(self.tree)
            ast.fix_missing_locations(fixed_tree)
            return ast.unparse(fixed_tree)
        except Exception as e:
            logger.error("fix_code() failed, falling back to format_code: %s", e)
            return self.format_code()