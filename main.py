from parser import parse_and_format_code

print("Enter your Python code (end with an empty line):")

lines = []
while True:
    line = input()
    if line == "":
        break
    lines.append(line)

user_code = "\n".join(lines)

result = parse_and_format_code(user_code)

print("\nFormatted Code:")
print(result)
