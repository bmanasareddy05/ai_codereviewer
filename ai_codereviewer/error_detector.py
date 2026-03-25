import ast

class AdvancedCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = {}
        self.defined_vars = set()
        self.used_vars = set()
        self.short_name_violations = []
        self.unreachable_code = []
        self.infinite_loops = []
        self.variable_values = {}

        self.score = 100
        self.violations = []

    # IMPORT TRACKING
    def visit_Import(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = alias.name
        self.generic_visit(node)

    def visit_ImportFrom(self, node):
        for alias in node.names:
            name = alias.asname if alias.asname else alias.name
            self.imports[name] = alias.name
        self.generic_visit(node)

    # VARIABLE TRACKING
    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_vars.add(node.id)

        elif isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)

            if len(node.id) < 3:
                self.short_name_violations.append(
                    f"Variable '{node.id}' name too short at line {node.lineno}"
                )

        self.generic_visit(node)

    # ASSIGNMENT TRACKING (FIXED)
    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_vars.add(target.id)

        self.generic_visit(node)

    # INFINITE LOOP DETECTION
    def visit_While(self, node):
        if isinstance(node.test, ast.Constant) and node.test.value == True:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.infinite_loops.append(
                    f"Infinite loop at line {node.lineno}"
                )
        self.generic_visit(node)

    # UNREACHABLE CODE
    def visit_FunctionDef(self, node):
        found_return = False

        for stmt in node.body:
            if found_return:
                self.unreachable_code.append(
                    f"Unreachable code at line {stmt.lineno}"
                )
            if isinstance(stmt, ast.Return):
                found_return = True

        self.generic_visit(node)

    # COMPLEXITY
    def estimate_complexity(self, tree):
        loop_count = 0
        nested = False

        for node in ast.walk(tree):
            if isinstance(node, (ast.For, ast.While)):
                loop_count += 1
                for child in ast.walk(node):
                    if isinstance(child, (ast.For, ast.While)) and child != node:
                        nested = True

        if nested:
            return "O(n^2)"
        elif loop_count == 1:
            return "O(n)"
        else:
            return "O(1)"

    # MAIN
    def analyze(self, tree):
        self.visit(tree)

        unused_imports = [
            name for name in self.imports
            if name not in self.used_vars
        ]

        unused_variables = [
            var for var in self.defined_vars
            if var not in self.used_vars
        ]

        for imp in unused_imports:
            self.violations.append(f"Unused import: {imp}")
            self.score -= 10

        for var in unused_variables:
            self.violations.append(f"Unused variable: {var}")
            self.score -= 5

        for msg in self.short_name_violations:
            self.violations.append(msg)
            self.score -= 3

        for msg in self.infinite_loops:
            self.violations.append(msg)
            self.score -= 15

        for msg in self.unreachable_code:
            self.violations.append(msg)
            self.score -= 10

        return {
            "unused_imports": unused_imports,
            "unused_variables": unused_variables,
            "short_name_violations": self.short_name_violations,
            "infinite_loops": self.infinite_loops,
            "unreachable_code": self.unreachable_code,
            "complexity_estimate": self.estimate_complexity(tree),
            "score": max(self.score, 0),
            "violations": self.violations
        }   