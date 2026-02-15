import ast 

def parse_and_format_code(user_code):
    try:
        # Parse the code into AST
        tree = ast.parse(user_code)

        # Print internal AST structure
        print("\nInternal AST Tree:")
        print(ast.dump(tree, indent=4))

        # Convert AST back to properly formatted code
        formatted_code = ast.unparse(tree)

        return formatted_code

    except SyntaxError as e:
        return f"Syntax Error: {e}"
