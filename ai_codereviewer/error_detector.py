import ast

BUILTINS = {
    "os", "re", "io", "id", "db", "i", "j", "k", "x", "y", "z",
    "n", "f", "e", "t", "v", "q", "fn", "ex", "ok", "up", "to",
    "df", "ax", "fig", "dt", "ts", "fp", "fd", "ip", "ui", "pk",
}


class AdvancedCodeAnalyzer(ast.NodeVisitor):
    def __init__(self):
        self.imports = {}
        self.defined_vars = set()
        self.used_vars = set()
        self.short_name_violations = []
        self.unreachable_code = []
        self.infinite_loops = []

        self.score = 100
        self.violations = []

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

    # ── VARIABLE TRACKING ────────────────────────────────────────────────────

    def visit_Name(self, node):
        if isinstance(node.ctx, ast.Store):
            self.defined_vars.add(node.id)
        elif isinstance(node.ctx, ast.Load):
            self.used_vars.add(node.id)
            # FIX: skip builtins to avoid false positives
            if len(node.id) < 3 and node.id not in BUILTINS:
                self.short_name_violations.append(
                    f"Variable '{node.id}' name too short at line {node.lineno}"
                )
        self.generic_visit(node)

    def visit_Assign(self, node):
        for target in node.targets:
            if isinstance(target, ast.Name):
                self.defined_vars.add(target.id)
            # FIX: handle tuple unpacking e.g. a, b = func()
            elif isinstance(target, ast.Tuple):
                for elt in target.elts:
                    if isinstance(elt, ast.Name):
                        self.defined_vars.add(elt.id)
        self.generic_visit(node)

    def visit_AugAssign(self, node):
        if isinstance(node.target, ast.Name):
            self.defined_vars.add(node.target.id)
            self.used_vars.add(node.target.id)
        self.generic_visit(node)

    def visit_While(self, node):
        if isinstance(node.test, ast.Constant) and node.test.value is True:
            has_break = any(isinstance(n, ast.Break) for n in ast.walk(node))
            if not has_break:
                self.infinite_loops.append(
                    f"Infinite loop at line {node.lineno}"
                )
        self.generic_visit(node)

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

    def _max_loop_nesting_depth(self, node, current_depth=0):
        """Recursively find the deepest loop nesting level inside a node."""
        max_depth = current_depth
        body = getattr(node, "body", [])
        for child in body:
            for n in ast.walk(child):
                if isinstance(n, (ast.For, ast.While)):
                    depth = self._max_loop_nesting_depth(n, current_depth + 1)
                    max_depth = max(max_depth, depth)
                    break
        return max_depth

    def _has_recursive_call(self, func_node):
        """Detect direct recursion — function calling itself."""
        func_name = func_node.name
        for node in ast.walk(func_node):
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name) and node.func.id == func_name:
                    return True
        return False

    def _detect_divide_and_conquer(self, func_node):
        """
        Heuristic for O(n log n): recursive AND halves input
        (slice like arr[mid:] or floor division like n // 2).
        """
        if not self._has_recursive_call(func_node):
            return False
        for node in ast.walk(func_node):
            if isinstance(node, ast.Subscript):
                if isinstance(node.slice, ast.Slice):
                    return True
            if isinstance(node, ast.BinOp) and isinstance(node.op, ast.FloorDiv):
                return True
        return False

    def _time_complexity_for_function(self, func_node):
        """
        Estimate time complexity for one function.
        Priority: O(n^3) > O(n^2) > O(n log n) > O(n) > O(log n) > O(1)
        """
        max_depth = self._max_loop_nesting_depth(func_node)

        if max_depth >= 3:
            return "O(n^3)"
        if max_depth == 2:
            return "O(n^2)"
        if self._detect_divide_and_conquer(func_node):
            return "O(n log n)"
        if max_depth == 1:
            if self._has_recursive_call(func_node):
                return "O(n log n)"
            return "O(n)"
        if self._has_recursive_call(func_node):
            for node in ast.walk(func_node):
                if isinstance(node, ast.BinOp) and isinstance(node.op, ast.FloorDiv):
                    return "O(log n)"
            return "O(n)"
        return "O(1)"

    def _space_complexity_for_function(self, func_node):
        """
        Estimate space complexity.
        Checks for growing collections, list comprehensions, and recursion.
        """
        creates_collection = False
        appends_in_loop = False
        has_recursion = self._has_recursive_call(func_node)

        for node in ast.walk(func_node):
            if isinstance(node, (ast.List, ast.Dict, ast.Set, ast.ListComp)):
                creates_collection = True

        for node in ast.walk(func_node):
            if isinstance(node, (ast.For, ast.While)):
                for child in ast.walk(node):
                    if isinstance(child, ast.Call):
                        if isinstance(child.func, ast.Attribute):
                            if child.func.attr in ("append", "extend", "add", "update"):
                                appends_in_loop = True

        if has_recursion or appends_in_loop or creates_collection:
            return "O(n)"
        return "O(1)"

    def _cyclomatic_complexity(self, func_node):
        """
        McCabe cyclomatic complexity = decision points + 1.
        Decision points: if, elif, for, while, except, with, assert, and/or.
        """
        decision_nodes = (
            ast.If, ast.For, ast.While,
            ast.ExceptHandler, ast.With,
            ast.Assert, ast.comprehension,
        )
        count = 1
        for node in ast.walk(func_node):
            if isinstance(node, decision_nodes):
                count += 1
            if isinstance(node, ast.BoolOp):
                count += len(node.values) - 1
        return count

    def _cyclomatic_label(self, score):
        if score <= 5:
            return "low risk"
        elif score <= 10:
            return "moderate risk"
        elif score <= 20:
            return "high risk"
        else:
            return "very high risk — consider splitting"

    def estimate_complexity(self, tree):
        """
        Full complexity report per function + overall worst-case.
        Returns time, space, cyclomatic per function plus overall summary.
        """
        COMPLEXITY_RANK = {
            "O(1)": 0, "O(log n)": 1, "O(n)": 2,
            "O(n log n)": 3, "O(n^2)": 4, "O(n^3)": 5,
        }

        functions = [
            n for n in ast.walk(tree)
            if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef))
        ]

        per_function = []
        worst_time  = "O(1)"
        worst_space = "O(1)"
        warnings    = []

        for func in functions:
            time_c  = self._time_complexity_for_function(func)
            space_c = self._space_complexity_for_function(func)
            cyclo   = self._cyclomatic_complexity(func)
            label   = self._cyclomatic_label(cyclo)

            per_function.append({
                "function":              func.name,
                "line":                  func.lineno,
                "time_complexity":       time_c,
                "space_complexity":      space_c,
                "cyclomatic_complexity": cyclo,
                "cyclomatic_risk":       label,
            })

            if COMPLEXITY_RANK.get(time_c, 0) > COMPLEXITY_RANK.get(worst_time, 0):
                worst_time = time_c
            if COMPLEXITY_RANK.get(space_c, 0) > COMPLEXITY_RANK.get(worst_space, 0):
                worst_space = space_c

            if time_c in ("O(n^2)", "O(n^3)"):
                warnings.append(
                    f"'{func.name}' (line {func.lineno}): {time_c} time — consider optimisation"
                )
            if cyclo > 10:
                warnings.append(
                    f"'{func.name}' (line {func.lineno}): cyclomatic complexity {cyclo} "
                    f"({label}) — consider splitting"
                )
            if self._has_recursive_call(func):
                warnings.append(
                    f"'{func.name}' (line {func.lineno}): recursive — "
                    f"ensure base case exists"
                )

        if not functions:
            depth = self._max_loop_nesting_depth(tree)
            if depth >= 3:
                worst_time = "O(n^3)"
            elif depth == 2:
                worst_time = "O(n^2)"
            elif depth == 1:
                worst_time = "O(n)"

        return {
            "overall_time_complexity":  worst_time,
            "overall_space_complexity": worst_space,
            "per_function":             per_function,
            "warnings":                 warnings,
        }

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
            self.score = max(self.score - 10, 0)

        for var in unused_variables:
            self.violations.append(f"Unused variable: {var}")
            self.score = max(self.score - 5, 0)

        for msg in self.short_name_violations:
            self.violations.append(msg)
            self.score = max(self.score - 3, 0)

        for msg in self.infinite_loops:
            self.violations.append(msg)
            self.score = max(self.score - 15, 0)

        for msg in self.unreachable_code:
            self.violations.append(msg)
            self.score = max(self.score - 10, 0)

        complexity = self.estimate_complexity(tree)

        for w in complexity["warnings"]:
            if "O(n^3)" in w:
                self.score = max(self.score - 20, 0)
            elif "O(n^2)" in w:
                self.score = max(self.score - 10, 0)
            elif "cyclomatic" in w:
                self.score = max(self.score - 8, 0)
            elif "recursive" in w:
                self.score = max(self.score - 3, 0)
            self.violations.append(w)

        return {
            "unused_imports":        unused_imports,
            "unused_variables":      unused_variables,
            "short_name_violations": self.short_name_violations,
            "infinite_loops":        self.infinite_loops,
            "unreachable_code":      self.unreachable_code,
            "complexity":            complexity,
            "score":                 self.score,
            "violations":            self.violations,
        }