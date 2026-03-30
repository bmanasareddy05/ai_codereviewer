import reflex as rx
from ai_codereviewer.components.navbar import navbar
from ai_codereviewer.components.footer import footer
from ai_codereviewer.components.hero import hero
from ai_codereviewer.components.colors import (
    BG_DARK, BG_SURFACE, BG_PANEL, BG_BORDER,
    GREEN, BLUE, PURPLE, YELLOW,
    TEXT_MAIN, TEXT_MUTED, TEXT_DIM
)

# HOMEPAGE
# Sections:
#   1. Navbar
#   2. Hero
#   3. Stats bar
#   4. Features section
#   5. CTA section
#   6. Footer

# ── Stats Bar
def single_stat(value: str, label: str) -> rx.Component:
    """One number + label combination in the stats bar."""
    return rx.vstack(
        rx.text(
            value,
            style={
                "font_family": "monospace",
                "font_size": "1.9rem",
                "font_weight": "800",
                # Gradient color on the number
                "background": f"linear-gradient(135deg, {GREEN}, {BLUE})",
                "background_clip": "text",
                "-webkit-background-clip": "text",
                "color": "transparent",
            },
        ),
        rx.text(
            label,
            style={
                "color": TEXT_MUTED,
                "font_size": "0.8rem",
                "text_align": "center",
            },
        ),
        align="center",
        spacing="1",
    )


def stats_bar() -> rx.Component:
    """
    A horizontal row of 4 key numbers about the app.
    Separated by vertical divider lines.
    """
    return rx.box(
        rx.hstack(
            single_stat("6+",   "Issue Types Detected"),
            rx.divider(
                orientation="vertical",
                style={"border_color": BG_BORDER, "height": "48px"},
            ),
            single_stat("O(n³)", "Max Complexity Flag"),
            rx.divider(
                orientation="vertical",
                style={"border_color": BG_BORDER, "height": "48px"},
            ),
            single_stat("100",  "Max Quality Score"),
            rx.divider(
                orientation="vertical",
                style={"border_color": BG_BORDER, "height": "48px"},
            ),
            single_stat("< 1s", "Analysis Time"),
            spacing="8",
            justify="center",
            flex_wrap="wrap",
            padding_y="3rem",
            max_width="800px",
            width="100%",
        ),
        style={
            "background": BG_DARK,
            "border_top": f"1px solid {BG_BORDER}",
            "border_bottom": f"1px solid {BG_BORDER}",
            "display": "flex",
            "justify_content": "center",
        },
        width="100%",
    )


# ── Features Section
FEATURES = [
    (
        "🔍",
        "Static Analysis",
        "Detects unused imports, unused variables, infinite loops, and unreachable code using Python's AST. C, C++, and Java are reviewed by AI.",
        GREEN,
    ),
    (
        "🤖",
        "AI Suggestions",
        "Get clear and simple improvement ideas from the built-in AI assistant. Ask follow-up questions in the History page.",
        BLUE,
    ),
    (
        "📊",
        "Quality Score",
        "Every analysis gives a score from 0 to 100. Each issue type reduces the score so you know what to fix first.",
        PURPLE,
    ),
    (
        "🔄",
        "Side-by-side Diff",
        "See the original code next to the improved version, color-coded so you can tell exactly what changed.",
        YELLOW,
    ),
    (
        "📜",
        "History & Chat",
        "All past reviews are saved on the History page. Chat with the AI assistant about any issue you don't understand.",
        GREEN,
    ),
    (
        "⚡",
        "Complexity Estimate",
        "Automatically estimates Big-O time and space complexity per function: O(1), O(log n), O(n), O(n log n), O(n²), or O(n³). Also computes cyclomatic complexity risk.",
        BLUE,
    ),
]


def feature_card(icon: str, title: str, description: str, color: str) -> rx.Component:
    """One feature card showing an icon, title, and description."""
    return rx.box(
        rx.vstack(
            # Icon box
            rx.box(
                rx.text(icon, style={"font_size": "1.4rem"}),
                style={
                    "width": "48px",
                    "height": "48px",
                    "border_radius": "12px",
                    "background": f"{color}14",
                    "border": f"1px solid {color}33",
                    "display": "flex",
                    "align_items": "center",
                    "justify_content": "center",
                },
            ),
            # Title
            rx.text(
                title,
                style={
                    "font_family": "monospace",
                    "font_weight": "700",
                    "font_size": "0.93rem",
                    "color": TEXT_MAIN,
                },
            ),
            # Description
            rx.text(
                description,
                style={
                    "color": TEXT_MUTED,
                    "font_size": "0.84rem",
                    "line_height": "1.65",
                },
            ),
            spacing="3",
            align="start",
        ),
        style={
            "padding": "1.5rem",
            "background": BG_PANEL,
            "border": f"1px solid {BG_BORDER}",
            "border_radius": "14px",
            "transition": "border-color 0.2s, transform 0.2s",
            "_hover": {
                "border_color": f"{color}55",
                "transform": "translateY(-3px)",
            },
        },
    )


def features_section() -> rx.Component:
    """
    Grid of 6 feature cards showing what the app does.
    Grid auto-adjusts columns based on screen width.
    """
    return rx.box(
        rx.vstack(
            # Section label
            rx.text(
                "WHAT IT DOES",
                style={
                    "font_family": "monospace",
                    "font_size": "0.68rem",
                    "letter_spacing": "0.2em",
                    "color": GREEN,
                    "text_transform": "uppercase",
                },
            ),
            # Section heading
            rx.heading(
                "Everything a code reviewer checks — done instantly.",
                style={
                    "font_family": "monospace",
                    "font_size": ["1.5rem", "1.9rem"],
                    "font_weight": "700",
                    "color": TEXT_MAIN,
                    "text_align": "center",
                    "line_height": "1.4",
                    "max_width": "600px",
                },
            ),
            # Feature cards grid
            rx.grid(
                *[
                    feature_card(icon, title, desc, color)
                    for icon, title, desc, color in FEATURES
                ],
                columns="3",
                spacing="4",
                width="100%",
                style={
                    "grid_template_columns": "repeat(auto-fill, minmax(260px, 1fr))",
                },
            ),
            spacing="6",
            align="center",
            max_width="1100px",
            width="100%",
            padding_x="2rem",
        ),
        style={
            "padding": "6rem 1rem",
            "background": BG_SURFACE,
            "display": "flex",
            "justify_content": "center",
        },
        width="100%",
    )


# ── CTA Section 
def cta_section() -> rx.Component:
    return rx.box(
        rx.vstack(
            rx.heading(
                "Ready to clean up your code?",
                style={
                    "font_family": "monospace",
                    "font_size": ["1.5rem", "1.9rem"],
                    "font_weight": "800",
                    "color": TEXT_MAIN,
                    "text_align": "center",
                },
            ),
            rx.text(
                "Paste your Python, C, C++, or Java code, hit Analyse, and get a full report in under a second.",
                style={
                    "color": TEXT_MUTED,
                    "font_size": "0.93rem",
                    "text_align": "center",
                },
            ),
            rx.link(
                "Open the Analyser →",
                href="/analyser",
                style={
                    "background": f"linear-gradient(135deg, {GREEN}, {BLUE})",
                    "color": "#0a0a0f",
                    "font_family": "monospace",
                    "font_weight": "700",
                    "font_size": "0.9rem",
                    "padding": "0.85rem 2rem",
                    "border_radius": "10px",
                    "text_decoration": "none",
                    "transition": "opacity 0.2s, transform 0.2s",
                    "_hover": {
                        "opacity": "0.88",
                        "transform": "translateY(-2px)",
                    },
                },
            ),
            spacing="5",
            align="center",
            padding_x="2rem",
        ),
        style={
            "padding": "6rem 1rem",
            # Subtle radial glow behind this section
            "background": f"radial-gradient(ellipse at center, {GREEN}0b 0%, {BG_DARK} 70%)",
            "display": "flex",
            "justify_content": "center",
        },
        width="100%",
    )


# ── Page 
def index() -> rx.Component:
    return rx.box(
        navbar(),
        hero(),
        stats_bar(),
        features_section(),
        cta_section(),
        footer(),
        style={
            "min_height": "100vh",
            "background": BG_DARK,
            "display": "flex",
            "flex_direction": "column",
        },
    )