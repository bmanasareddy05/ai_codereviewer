from code_parser import CodeParser
from error_detector import AdvancedCodeAnalyzer
from ai_suggester import AISuggester


def main():
    print("Paste your Python code (type END to finish):")

    lines = []
    while True:
        line = input()
        if line.strip().upper() == "END":
            break
        lines.append(line)

    student_code = "\n".join(lines)
    parser = CodeParser(student_code)
    tree = parser.parse()

    if isinstance(tree, dict) and "error" in tree:
        print("\n--- Syntax Error ---")
        print(tree["error"])
        return

    print("\n--- AST Tree ---")
    print(parser.get_ast_dump())

    print("\n--- Formatted Code ---")
    formatted = parser.format_code()
    if formatted:
        print(formatted)

        
    analyzer = AdvancedCodeAnalyzer()
    analysis_results = analyzer.analyze(tree)

    print("\n--- Advanced Analysis Report ---")
    print(f"Unused Imports: {analysis_results['unused_imports']}")
    print(f"Unused Variables: {analysis_results['unused_variables']}")
    print(f"Short Name Issues: {analysis_results['short_name_violations']}")
    print(f"Infinite Loop Warnings: {analysis_results['infinite_loops']}")
    print(f"Unreachable Code: {analysis_results['unreachable_code']}")
    print(f"Estimated Complexity: {analysis_results['complexity_estimate']}")

    print("\n--- Code Score ---")
    print(f"Score: {analysis_results['score']}/100")

    if analysis_results["violations"]:
        print("\nViolations:")
        for v in analysis_results["violations"]:
            print("-", v)
    else:
        print("No major issues detected.")

    print("\n--- AI Technical Review ---")
    ai = AISuggester()
    review = ai.generate_review(student_code)
    print(review)


if __name__ == "__main__":
    main()