import ast

class CodeParser:
    def __init__(self, code: str):
        self.code = code
        self.tree = None

    def parse(self):
        try:
            self.tree = ast.parse(self.code)
            return self.tree
        except SyntaxError as e:
            return {"error": str(e), "status": "Syntax Error"}

    def get_ast_dump(self):
        if self.tree:
            return ast.dump(self.tree, indent=4)
        return None

    def format_code(self):
        try:
            if self.tree:
                return ast.unparse(self.tree)
            return self.code
        except Exception:
            return self.code