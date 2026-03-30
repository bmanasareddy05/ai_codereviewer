import reflex as rx
from ai_codereviewer.state import AppState
from ai_codereviewer.components.navbar import navbar
from ai_codereviewer.components.footer import footer
from ai_codereviewer.components.colors import (
    BG_DARK, BG_PANEL, BG_BORDER,
    GREEN, BLUE, RED, YELLOW, PURPLE,
    TEXT_MAIN, TEXT_MUTED, TEXT_DIM
)

# LEFT PANEL: Code Editor

def editor_title_bar() -> rx.Component:
    """Top bar of the code editor with traffic light dots and detected language badge."""
    return rx.hstack(
        rx.box(style={"width": "10px", "height": "10px", "border_radius": "50%", "background": "#ff5f57"}),
        rx.box(style={"width": "10px", "height": "10px", "border_radius": "50%", "background": "#febc2e"}),
        rx.box(style={"width": "10px", "height": "10px", "border_radius": "50%", "background": "#28c840"}),
        rx.spacer(),
        rx.text(
            AppState.detected_language,
            style={
                "color": GREEN,
                "font_size": "0.72rem",
                "font_family": "monospace",
                "background": f"{GREEN}15",
                "padding": "2px 8px",
                "border_radius": "6px",
                "border": f"1px solid {GREEN}33",
            }
        ),
        style={"padding": "0.7rem 1rem", "border_bottom": f"1px solid {BG_BORDER}"},
        align="center",
        width="100%",
    )

def code_textarea() -> rx.Component:
    """The actual textarea where users paste their code."""
    return rx.text_area(
        value=AppState.raw_code,
        on_change=AppState.set_raw_code,
        placeholder="# Paste your Python, C, C++, or Java code here...",
        style={
            "font_family": "monospace",
            "font_size": "0.83rem",
            "line_height": "1.8",
            "color": "#F8FAFC",
            "background": "transparent",
            "border": "none",
            "outline": "none",
            "resize": "none",
            "flex": "1",
            "padding": "1rem 1.2rem",
            "min_height": "360px",
            "width": "100%",
        },
        rows="20",
        width="100%",
    )

def editor_action_bar() -> rx.Component:
    """Bottom bar of the editor with Clear and Analyse buttons."""
    return rx.hstack(
        rx.button("Clear", on_click=AppState.clear_editor, variant="soft", color_scheme="gray"),
        rx.spacer(),
        rx.button(
            rx.cond(AppState.is_analyzing, "Analysing...", "⚡ Analyse Code"),
            on_click=AppState.analyze_code,
            disabled=AppState.is_analyzing,
            style={
                "background": f"linear-gradient(135deg, {GREEN}, {BLUE})",
                "color": "#0a0a0f",
                "font_family": "monospace",
                "font_weight": "700",
                "padding": "0.6rem 1.4rem",
                "border_radius": "8px",
            },
        ),
        width="100%",
        style={"padding": "0.8rem 1rem", "border_top": f"1px solid {BG_BORDER}"},
        align="center",
    )

def editor_panel() -> rx.Component:
    """Left panel: contains the code editor."""
    return rx.vstack(
        editor_title_bar(),
        rx.cond(
            AppState.analysis_error != "",
            rx.box(
                rx.hstack(
                    rx.text("⚠", style={"color": RED, "font_size": "0.85rem"}),
                    rx.text(
                        AppState.analysis_error,
                        style={"color": RED, "font_size": "0.82rem", "font_family": "monospace"},
                    ),
                    spacing="2",
                    align="center",
                ),
                style={
                    "padding": "0.7rem 1rem",
                    "background": f"{RED}10",
                    "border_bottom": f"1px solid {RED}33",
                    "width": "100%",
                },
            ),
            rx.box(),
        ),
        code_textarea(),
        editor_action_bar(),
        spacing="0",
        style={
            "background": BG_PANEL,
            "border": f"1px solid {BG_BORDER}",
            "border_radius": "14px",
            "overflow": "hidden",
        },
        width="100%",
    )

# RIGHT PANEL: Results

def diff_line_view(line: dict) -> rx.Component:
    """Renders one diff line: red for removed, green for added."""
    bg_color   = rx.cond(line["type"] == "added", f"{GREEN}22", rx.cond(line["type"] == "removed", f"{RED}22", "transparent"))
    prefix     = rx.cond(line["type"] == "added", "+", rx.cond(line["type"] == "removed", "-", " "))
    text_color = rx.cond(line["type"] == "added", GREEN, rx.cond(line["type"] == "removed", RED, "#CBD5E1"))

    return rx.hstack(
        rx.text(prefix, style={"width": "20px", "font_family": "monospace", "color": TEXT_DIM}),
        rx.text(line["text"], style={"font_family": "monospace", "font_size": "0.82rem", "flex": "1", "color": text_color}),
        style={"background": bg_color, "width": "100%", "padding_x": "0.5rem"},
    )

def complexity_row(fn: dict) -> rx.Component:
    """One row in the per-function complexity table."""
    risk_color = rx.cond(
        fn["risk"] == "low risk", GREEN,
        rx.cond(fn["risk"] == "moderate risk", YELLOW,
        rx.cond(fn["risk"] == "high risk", RED, RED))
    )
    return rx.hstack(
        rx.text(fn["function"], style={"font_family": "monospace", "font_size": "0.8rem", "color": TEXT_MAIN, "min_width": "120px"}),
        rx.text(f"L{fn['line']}", style={"font_size": "0.75rem", "color": TEXT_DIM, "font_family": "monospace", "min_width": "40px"}),
        rx.text(fn["time"],  style={"font_family": "monospace", "font_size": "0.8rem", "color": BLUE,  "min_width": "90px"}),
        rx.text(fn["space"], style={"font_family": "monospace", "font_size": "0.8rem", "color": PURPLE, "min_width": "70px"}),
        rx.text(fn["cyclomatic"], style={"font_family": "monospace", "font_size": "0.8rem", "color": risk_color, "min_width": "30px"}),
        rx.text(fn["risk"], style={"font_size": "0.72rem", "color": risk_color}),
        spacing="4",
        padding_y="0.4rem",
        width="100%",
        style={"border_bottom": f"1px solid {BG_BORDER}"},
    )

def tab_button(label: str, tab_name: str) -> rx.Component:
    """A tab button for switching results views."""
    is_active = AppState.active_tab == tab_name
    return rx.button(
        label,
        on_click=lambda: AppState.set_active_tab(tab_name),
        variant=rx.cond(is_active, "surface", "ghost"),
        color_scheme=rx.cond(is_active, "blue", "gray"),
        size="2",
        style={"font_family": "monospace", "letter_spacing": "0.05em"}
    )

def results_panel() -> rx.Component:
    """Right panel: AI review, stats bar, and tabbed results."""

    # Stats bar
    stats_header = rx.hstack(
        rx.vstack(
            rx.text("Score", style={"color": TEXT_DIM, "font_size": "0.7rem", "font_family": "monospace", "text_transform": "uppercase"}),
            rx.text(
                AppState.score,
                style={
                    "font_size": "1.3rem", "font_weight": "800", "font_family": "monospace",
                    "color": rx.cond(AppState.score >= 80, GREEN, rx.cond(AppState.score >= 50, YELLOW, RED)),
                }
            ),
            align="start", spacing="1",
        ),
        rx.divider(orientation="vertical", style={"height": "35px", "border_color": BG_BORDER}),
        rx.vstack(
            rx.text("Time", style={"color": TEXT_DIM, "font_size": "0.7rem", "font_family": "monospace", "text_transform": "uppercase"}),
            rx.text(AppState.complexity, style={"font_size": "1.1rem", "font_weight": "700", "color": BLUE, "font_family": "monospace"}),
            align="start", spacing="1",
        ),
        rx.divider(orientation="vertical", style={"height": "35px", "border_color": BG_BORDER}),
        rx.vstack(
            rx.text("Space", style={"color": TEXT_DIM, "font_size": "0.7rem", "font_family": "monospace", "text_transform": "uppercase"}),
            rx.text(AppState.space_complexity, style={"font_size": "1.1rem", "font_weight": "700", "color": PURPLE, "font_family": "monospace"}),
            align="start", spacing="1",
        ),
        rx.divider(orientation="vertical", style={"height": "35px", "border_color": BG_BORDER}),
        rx.vstack(
            rx.text("Issues", style={"color": TEXT_DIM, "font_size": "0.7rem", "font_family": "monospace", "text_transform": "uppercase"}),
            rx.text(AppState.violations.length(), style={"font_size": "1.1rem", "font_weight": "700", "color": RED, "font_family": "monospace"}),
            align="start", spacing="1",
        ),
        spacing="6",
        style={"padding": "1.2rem", "border_bottom": f"1px solid {BG_BORDER}"},
        width="100%",
    )

    # Complexity tab content — per-function table
    complexity_tab = rx.vstack(
        # Table header
        rx.hstack(
            rx.text("Function", style={"font_size": "0.7rem", "color": TEXT_DIM, "font_family": "monospace", "min_width": "120px"}),
            rx.text("Line",     style={"font_size": "0.7rem", "color": TEXT_DIM, "font_family": "monospace", "min_width": "40px"}),
            rx.text("Time",     style={"font_size": "0.7rem", "color": TEXT_DIM, "font_family": "monospace", "min_width": "90px"}),
            rx.text("Space",    style={"font_size": "0.7rem", "color": TEXT_DIM, "font_family": "monospace", "min_width": "70px"}),
            rx.text("CC",       style={"font_size": "0.7rem", "color": TEXT_DIM, "font_family": "monospace", "min_width": "30px"}),
            rx.text("Risk",     style={"font_size": "0.7rem", "color": TEXT_DIM, "font_family": "monospace"}),
            spacing="4",
            padding_y="0.4rem",
            style={"border_bottom": f"1px solid {BG_BORDER}"},
            width="100%",
        ),
        rx.cond(
            AppState.complexity_per_function.length() == 0,
            rx.text("No named functions found.", style={"color": TEXT_DIM, "font_size": "0.82rem", "font_family": "monospace", "padding": "1rem 0"}),
            rx.foreach(AppState.complexity_per_function, complexity_row),
        ),
        # Warnings
        rx.cond(
            AppState.complexity_warnings.length() > 0,
            rx.vstack(
                rx.text("Warnings", style={"color": YELLOW, "font_size": "0.7rem", "font_family": "monospace", "text_transform": "uppercase", "margin_top": "1rem"}),
                rx.foreach(
                    AppState.complexity_warnings,
                    lambda w: rx.hstack(
                        rx.box(style={"width": "6px", "height": "6px", "background": YELLOW, "border_radius": "50%", "margin_top": "6px"}),
                        rx.text(w, style={"color": "#CBD5E1", "font_family": "monospace", "font_size": "0.8rem"}),
                        align="start", spacing="3",
                    )
                ),
                align="start", spacing="2", width="100%",
            ),
            rx.box(),
        ),
        padding="1.2rem",
        align="start",
        width="100%",
    )

    loaded_state = rx.vstack(
        # AI Review box
        rx.box(
            rx.vstack(
                rx.text("🤖 AI TECHNICAL REVIEW", style={"font_family": "monospace", "font_size": "0.7rem", "font_weight": "800", "color": GREEN}),
                rx.markdown(AppState.ai_recommendation, style={"font_size": "0.85rem", "color": "#E2E8F0", "line_height": "1.6"}),
                align="start", spacing="2",
            ),
            style={"padding": "1.2rem", "margin": "12px", "background": "#111827", "border": f"1px solid {BLUE}33", "border_radius": "12px", "width": "calc(100% - 24px)"},
        ),

        stats_header,

        rx.hstack(
            tab_button("Violations", "violations"),
            tab_button("Improved Code", "improved"),
            tab_button("Diff", "diff"),
            tab_button("Complexity", "complexity"),
            style={"padding": "0.7rem 1.2rem", "border_bottom": f"1px solid {BG_BORDER}"},
            width="100%",
            spacing="3",
        ),

        # Active tab content
        rx.box(
            rx.cond(
                AppState.active_tab == "violations",
                rx.vstack(
                    rx.foreach(
                        AppState.violations,
                        lambda v: rx.hstack(
                            rx.box(style={"width": "6px", "height": "6px", "background": RED, "border_radius": "50%", "margin_top": "8px"}),
                            rx.text(v, color="#CBD5E1", font_family="monospace", font_size="0.82rem"),
                            align="start", spacing="3", padding_y="0.3rem"
                        )
                    ),
                    padding="1.2rem", align="start"
                ),
                rx.cond(
                    AppState.active_tab == "improved",
                    rx.scroll_area(
                        rx.text(
                            AppState.improved_code,
                            style={"white_space": "pre-wrap", "font_family": "monospace", "color": "#F8FAFC", "padding": "1.2rem", "font_size": "0.85rem", "line_height": "1.8"}
                        ),
                        style={"max_height": "400px"}
                    ),
                    rx.cond(
                        AppState.active_tab == "diff",
                        rx.scroll_area(
                            rx.vstack(rx.foreach(AppState.diff_lines, diff_line_view), spacing="0", width="100%"),
                            style={"max_height": "400px", "padding_y": "0.5rem"}
                        ),
                        # Complexity tab
                        rx.scroll_area(
                            complexity_tab,
                            style={"max_height": "400px"},
                        )
                    )
                )
            ),
            width="100%",
        ),
        width="100%",
        spacing="0",
    )

    empty_state = rx.center(
        rx.vstack(
            rx.text("⬡", style={"font_size": "3rem", "color": TEXT_DIM}),
            rx.text(
                "Paste code and click Analyse to begin.",
                color=TEXT_DIM, font_family="monospace", font_size="0.9rem"
            ),
            align="center", spacing="3"
        ),
        min_height="520px"
    )

    return rx.box(
        rx.cond(
            (AppState.score > 0) | (AppState.violations.length() > 0) | (AppState.ai_recommendation != ""),
            loaded_state,
            empty_state,
        ),
        style={
            "background": BG_PANEL,
            "border": f"1px solid {BG_BORDER}",
            "border_radius": "14px",
            "min_height": "520px",
            "overflow": "hidden",
        },
        width="100%",
    )

# MAIN PAGE

def analyser() -> rx.Component:
    """The complete analyser page layout."""
    return rx.box(
        navbar(),
        rx.box(
            rx.vstack(
                rx.vstack(
                    rx.text("ANALYSER", style={"font_family": "monospace", "font_size": "0.68rem", "letter_spacing": "0.25em", "color": GREEN}),
                    rx.heading("Paste. Analyse. Improve.", style={"font_family": "monospace", "font_size": "2rem", "font_weight": "800", "color": TEXT_MAIN}),
                    align="center", spacing="1", margin_bottom="2rem"
                ),
                rx.grid(
                    editor_panel(),
                    results_panel(),
                    columns="2",
                    spacing="6",
                    width="100%",
                    grid_template_columns="repeat(auto-fit, minmax(400px, 1fr))",
                ),
                width="100%",
                max_width="1400px",
                padding_x=["1rem", "2rem"],
                padding_y="3rem",
            ),
            style={"display": "flex", "justify_content": "center", "background": BG_DARK},
            width="100%",
        ),
        footer(),
        style={"min_height": "100vh", "background": BG_DARK, "display": "flex", "flex_direction": "column"},
    )