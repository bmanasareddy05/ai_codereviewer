import os

EXTENSION_MAP = {
    ".py":   "python",
    ".c":    "c",
    ".cpp":  "cpp",
    ".cc":   "cpp",
    ".cxx":  "cpp",
    ".java": "java",
    ".js":   "javascript",
    ".ts":   "typescript",
}

PYTHON_STATIC = {"python"}

LLM_ONLY = {"c", "cpp", "java", "javascript", "typescript"}

# Display labels for UI
LANGUAGE_DISPLAY = {
    "python":     "Python",
    "c":          "C",
    "cpp":        "C++",
    "java":       "Java",
    "javascript": "JavaScript",
    "typescript": "TypeScript",
}


def detect_language_from_filename(filename: str) -> str:
    """Detect language from file extension. Returns 'unknown' if unsupported."""
    ext = os.path.splitext(filename)[-1].lower()
    return EXTENSION_MAP.get(ext, "unknown")


def detect_language_from_code(code: str) -> str:
    """
    Heuristic language detection from code content alone (no filename).
    Used when the user pastes code directly without a file name.
    Returns best guess — defaults to 'python'.
    """
    code_stripped = code.strip()

    if "public class " in code or "public static void main" in code or "System.out.println" in code:
        return "java"

    if "#include <iostream>" in code or "std::" in code or "cout <<" in code or "namespace " in code:
        return "cpp"

    if "#include <stdio.h>" in code or "#include <stdlib.h>" in code or "printf(" in code:
        return "c"

    if ": string" in code or ": number" in code or "interface " in code or ": boolean" in code:
        return "typescript"

    if "require(" in code or "console.log(" in code or "=>" in code:
        return "javascript"

    return "python"


def is_supported(language: str) -> bool:
    return language != "unknown"


def needs_python_analysis(language: str) -> bool:
    return language in PYTHON_STATIC


def get_display_name(language: str) -> str:
    return LANGUAGE_DISPLAY.get(language, language.capitalize())