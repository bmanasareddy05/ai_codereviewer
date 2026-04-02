# AI Code Reviewer

An AI-powered code review web application built with [Reflex](https://reflex.dev). Paste your code, get instant static analysis, a quality score, complexity breakdown, an improved version of your code, and an AI-powered technical review — all in one place.

---

## Features

- **Multi-language support** — Python, C, C++, Java, JavaScript, TypeScript
- **Automatic language detection** — detects the language as you type from code patterns, no file upload needed
- **Static analysis (Python)** — uses Python's built-in `ast` module to detect:
  - Unused imports and unused variables
  - Infinite loops
  - Unreachable code after return statements
  - Short/non-descriptive variable names
- **Full complexity analysis (Python)** — per-function breakdown of:
  - Time complexity (O(1) → O(n³))
  - Space complexity
  - Cyclomatic complexity with risk labels
  - Divide-and-conquer / recursion detection
- **Improved code (Python)** — actually fixes the code by removing unused imports and variables from the AST, then unparses to clean source
- **Side-by-side diff** — color-coded view of original vs improved code
- **AI technical review** — powered by Llama 3.1 via Groq, language-aware review covering bugs, complexity, quality, and specific improvements
- **AI static analysis (non-Python)** — for C/C++/Java/JS/TS, the AI detects violations, scores the code, produces improved code, and gives a full complexity breakdown
- **Quality score** — 0–100 score that deducts points per issue found
- **History page** — all past analyses saved in session with metadata
- **AI chat assistant** — ask follow-up questions about your code on the History page

---

## Tech Stack

| Layer | Technology |
|---|---|
| Framework | [Reflex](https://reflex.dev) (Python full-stack) |
| AI Model | Llama 3.1 8B Instant via [Groq](https://groq.com) |
| LLM Client | LangChain Groq (`langchain-groq`) |
| Static Analysis | Python `ast` module |
| Env Management | `python-dotenv` |

---

## Project Structure

```
AI_CODEREVIEWER/                    ← project root
│
├── main.py                         # Reflex main runner
├── .env                            # GROQ_API_KEY goes here (never commit this)
├── .gitignore
├── config.py                       # (legacy — replaced by os.getenv)
│
└── ai_codereviewer/                ← inner package folder
    ├── __init__.py
    ├── ai_codereviewer.py          # App entry point — registers all pages
    ├── state.py                    # Full app state + all event handlers
    ├── ai_suggester.py             # AI review, chat, and non-Python analysis
    ├── code_parser.py              # AST parse, fix (removes violations), unparse
    ├── error_detector.py           # Static analysis — violations + complexity engine
    ├── language_router.py          # Language detection from code content
    │
    ├── components/
    │   ├── colors.py               # Central theme/color constants
    │   ├── navbar.py               # Navigation bar
    │   ├── footer.py               # Footer
    │   └── hero.py                 # Hero section component
    │
    └── pages/
        ├── __init__.py
        ├── home.py                 # Landing page
        ├── analyzer.py             # Main analyser page
        └── history.py              # History + AI chat page
```

---

## How It Works

### Python Flow
```
Paste code
    ↓
ast.parse()           → catch syntax errors immediately
    ↓
AdvancedCodeAnalyzer  → detect unused imports, unused vars,
                        infinite loops, unreachable code,
                        short names, full complexity breakdown
    ↓
CodeParser.fix_code() → remove detected issues from AST nodes
    ↓
ast.unparse()         → produce the actually-fixed improved code
    ↓
difflib.ndiff()       → build side-by-side diff
    ↓
AISuggester           → language-aware AI technical review
```

### Non-Python Flow (C / C++ / Java / JS / TS)
```
Paste code
    ↓
AISuggester._get_violations_and_score()  → small JSON (violations + score)
    ↓
AISuggester._get_improved_code()         → plain text fixed code (no JSON)
    ↓
AISuggester._get_complexity()            → small JSON (complexity breakdown)
    ↓
difflib.ndiff()                          → build side-by-side diff
    ↓
AISuggester.generate_review()            → AI technical review text
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/bmanasareddy05/ai_codereviewer
cd AI_CODEREVIEWER
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install reflex langchain-groq python-dotenv
```

### 4. Get a Groq API key

Go to [console.groq.com](https://console.groq.com) → API Keys → Create Key.

### 5. Add your key to `.env`

Open the `.env` file in the project root and add:

```
GROQ_API_KEY=gsk_your_actual_key_here
```

> **Never commit `.env` to git.** It is already listed in `.gitignore`.

### 6. Run the app

```bash
reflex run
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

---

## Pages

| Route | Description |
|---|---|
| `/` | Landing page — features overview, stats, CTA |
| `/analyser` | Main page — paste code, run analysis, view results |
| `/history` | Past analyses + AI chat assistant |

---

## Analysis Output

| Tab | What it shows |
|---|---|
| Violations | List of all issues found with severity indicators |
| Improved Code | Fixed source code with violations resolved |
| Diff | Side-by-side color-coded original vs improved |
| Complexity | Per-function time/space/cyclomatic complexity table |

The stats bar shows **Score**, **Time complexity**, **Space complexity**, and **Issue count** at a glance.

---

## Complexity Levels Detected

| Level | When |
|---|---|
| O(1) | No loops, no recursion |
| O(log n) | Recursive with halving (binary search pattern) |
| O(n) | Single loop or linear recursion |
| O(n log n) | Recursive + input halving (merge sort / quicksort pattern) |
| O(n²) | Nested loops (2 levels) |
| O(n³) | Triple nested loops |

Cyclomatic complexity is also computed per function with risk labels: **low**, **moderate**, **high**, **very high**.

---

## Environment Variables

| Variable | Required | Description |
|---|---|---|
| `GROQ_API_KEY` | Yes | Your Groq API key for Llama 3.1 access |

---

## Supported Languages

| Language | Static Analysis | AI Review | Improved Code | Complexity |
|---|---|---|---|---|
| Python | AST-based | Yes | Yes (AST fix) | Full per-function |
| C | — | Yes | Yes (AI) | Yes (AI) |
| C++ | — | Yes | Yes (AI) | Yes (AI) |
| Java | — | Yes | Yes (AI) | Yes (AI) |
| JavaScript | — | Yes | Yes (AI) | Yes (AI) |
| TypeScript | — | Yes | Yes (AI) | Yes (AI) |

---

## Known Limitations

- History is session-only — it resets when the server restarts (no database persistence yet)
- Language detection is heuristic-based — very short snippets may default to Python
- Non-Python improved code quality depends on the AI model response

---

## License

MIT License — feel free to use, modify, and distribute.
