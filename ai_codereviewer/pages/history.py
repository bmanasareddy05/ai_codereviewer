import reflex as rx
from ai_codereviewer.state import AppState, HistoryEntry, ChatMessage
from ai_codereviewer.components.navbar import navbar
from ai_codereviewer.components.footer import footer
from ai_codereviewer.components.colors import (
    BG_DARK, BG_PANEL, BG_BORDER,
    GREEN, BLUE, YELLOW, RED,
    TEXT_MAIN, TEXT_MUTED, TEXT_DIM
)

def score_badge(score: int) -> rx.Component:
    return rx.box(
        rx.text(
            score,
            style={
                "font_family": "monospace",
                "font_size": "1rem",
                "font_weight": "700",
                "color": rx.cond(
                    score >= 80,
                    GREEN,
                    rx.cond(score >= 50, YELLOW, RED),
                ),
            },
        ),
        style={
            "padding": "0.25rem 0.7rem",
            "border_radius": "7px",
            "border": rx.cond(
                score >= 80,
                f"1px solid {GREEN}55",
                rx.cond(score >= 50, f"1px solid {YELLOW}55", f"1px solid {RED}55"),
            ),
            "background": rx.cond(
                score >= 80,
                f"{GREEN}0d",
                rx.cond(score >= 50, f"{YELLOW}0d", f"{RED}0d"),
            ),
        },
    )


def history_card(entry: HistoryEntry) -> rx.Component:
    return rx.box(
        rx.vstack(
            # Top row: code snippet + score badge
            rx.hstack(
                rx.vstack(
                    rx.text(
                        entry.timestamp,
                        style={
                            "font_family": "monospace",
                            "font_size": "0.7rem",
                            "color": TEXT_DIM,
                        },
                    ),
                    rx.text(
                        entry.code_snippet,
                        style={
                            "font_family": "monospace",
                            "font_size": "0.8rem",
                            "color": TEXT_MUTED,
                            "white_space": "nowrap",
                            "overflow": "hidden",
                            "text_overflow": "ellipsis",
                            "max_width": "320px",
                        },
                    ),
                    spacing="1",
                    align="start",
                    flex="1",
                ),
                rx.spacer(),
                score_badge(entry.score),
                align="start",
                width="100%",
            ),

            # Bottom row: metadata tags
            rx.hstack(
                # Language tag
                rx.hstack(
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": BLUE,
                        },
                    ),
                    rx.text(
                        entry.language,
                        style={
                            "font_size": "0.72rem",
                            "color": TEXT_MUTED,
                            "font_family": "monospace",
                        },
                    ),
                    spacing="2",
                    align="center",
                ),
                # Complexity tag
                rx.hstack(
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": GREEN,
                        },
                    ),
                    rx.text(
                        entry.complexity,
                        style={
                            "font_size": "0.72rem",
                            "color": TEXT_MUTED,
                            "font_family": "monospace",
                        },
                    ),
                    spacing="2",
                    align="center",
                ),
                # Issue count tag
                rx.hstack(
                    rx.box(
                        style={
                            "width": "6px",
                            "height": "6px",
                            "border_radius": "50%",
                            "background": RED,
                        },
                    ),
                    rx.text(
                        f"{entry.violation_count} issue(s)",
                        style={
                            "font_size": "0.72rem",
                            "color": TEXT_MUTED,
                            "font_family": "monospace",
                        },
                    ),
                    spacing="2",
                    align="center",
                ),
                spacing="5",
                flex_wrap="wrap",
            ),

            spacing="3",
            width="100%",
        ),
        style={
            "padding": "1rem 1.2rem",
            "background": BG_PANEL,
            "border": f"1px solid {BG_BORDER}",
            "border_radius": "12px",
            "transition": "border-color 0.2s, transform 0.15s",
            "_hover": {
                "border_color": f"{GREEN}40",
                "transform": "translateX(4px)",
            },
        },
        width="100%",
    )


def empty_history() -> rx.Component:
    return rx.vstack(
        rx.text("📂", style={"font_size": "2.5rem"}),
        rx.text(
            "No analyses yet",
            style={
                "font_family": "monospace",
                "color": TEXT_DIM,
                "font_size": "0.88rem",
            },
        ),
        rx.link(
            "Go analyse some code →",
            href="/analyser",
            style={
                "font_family": "monospace",
                "font_size": "0.8rem",
                "color": GREEN,
                "text_decoration": "none",
                "_hover": {"text_decoration": "underline"},
            },
        ),
        align="center",
        justify="center",
        style={"padding": "4rem 1rem"},
        spacing="3",
    )


def history_panel() -> rx.Component:
    return rx.vstack(
        # Panel header
        rx.hstack(
            rx.vstack(
                rx.text(
                    "ANALYSIS HISTORY",
                    style={
                        "font_family": "monospace",
                        "font_size": "0.66rem",
                        "letter_spacing": "0.2em",
                        "color": GREEN,
                        "text_transform": "uppercase",
                    },
                ),
                rx.heading(
                    "Past Reviews",
                    style={
                        "font_family": "monospace",
                        "font_size": "1.25rem",
                        "font_weight": "700",
                        "color": TEXT_MAIN,
                    },
                ),
                spacing="1",
                align="start",
            ),
            rx.spacer(),
            # Clear all button
            rx.button(
                "Clear All",
                on_click=AppState.clear_history,
                style={
                    "background": "transparent",
                    "border": f"1px solid {RED}44",
                    "color": RED,
                    "font_family": "monospace",
                    "font_size": "0.73rem",
                    "padding": "0.4rem 0.85rem",
                    "border_radius": "7px",
                    "cursor": "pointer",
                    "_hover": {"background": f"{RED}10"},
                },
            ),
            width="100%",
            align="center",
        ),

        rx.cond(
            AppState.history.length() == 0,
            empty_history(),
            rx.scroll_area(
                rx.vstack(
                    rx.foreach(AppState.history, history_card),
                    spacing="2",
                    width="100%",
                ),
                style={"max_height": "calc(100vh - 300px)"},
                width="100%",
            ),
        ),

        spacing="4",
        width="100%",
        style={
            "padding": "1.5rem",
            "background": BG_PANEL,
            "border": f"1px solid {BG_BORDER}",
            "border_radius": "14px",
        },
    )


# AI Chat
def chat_bubble(msg: ChatMessage) -> rx.Component:
    is_user = msg.role == "user"

    bubble = rx.vstack(
        rx.text(
            msg.content,
            style={
                "font_size": "0.84rem",
                "color": TEXT_MAIN,
                "line_height": "1.65",
                # Use monospace for user messages to match the code feel
                "font_family": rx.cond(is_user, "monospace", "system-ui, sans-serif"),
            },
        ),
        rx.text(
            msg.timestamp,
            style={
                "font_size": "0.67rem",
                "color": TEXT_DIM,
                "font_family": "monospace",
            },
        ),
        spacing="1",
        style={
            "padding": "0.72rem 1rem",
            "border_radius": rx.cond(
                is_user,
                "10px 10px 2px 10px",   # user bubble: pointy bottom-right
                "10px 10px 10px 2px",   # AI bubble: pointy bottom-left
            ),
            "background": rx.cond(
                is_user,
                f"linear-gradient(135deg, {GREEN}20, {BLUE}20)",
                BG_DARK,
            ),
            "border": rx.cond(
                is_user,
                f"1px solid {GREEN}44",
                f"1px solid {BG_BORDER}",
            ),
            "max_width": "85%",
        },
        align=rx.cond(is_user, "end", "start"),
    )
    return rx.hstack(
        rx.cond(is_user, rx.spacer(), rx.box()),
        bubble,
        width="100%",
        align="end",
    )


def chat_header() -> rx.Component:
    return rx.hstack(
        # Bot icon
        rx.box(
            rx.text("🤖", style={"font_size": "1rem"}),
            style={
                "width": "36px",
                "height": "36px",
                "border_radius": "10px",
                "background": f"{GREEN}14",
                "border": f"1px solid {GREEN}33",
                "display": "flex",
                "align_items": "center",
                "justify_content": "center",
            },
        ),
        rx.vstack(
            rx.text(
                "AI Code Assistant",
                style={
                    "font_family": "monospace",
                    "font_weight": "700",
                    "font_size": "0.88rem",
                    "color": TEXT_MAIN,
                },
            ),
            # Online status dot
            rx.hstack(
                rx.box(
                    style={
                        "width": "6px",
                        "height": "6px",
                        "border_radius": "50%",
                        "background": GREEN,
                    },
                ),
                rx.text(
                    "Online",
                    style={
                        "font_size": "0.7rem",
                        "color": GREEN,
                        "font_family": "monospace",
                    },
                ),
                spacing="2",
                align="center",
            ),
            spacing="0",
            align="start",
        ),
        align="center",
        spacing="3",
        style={
            "padding": "1rem 1.2rem",
            "border_bottom": f"1px solid {BG_BORDER}",
        },
        width="100%",
    )


def chat_messages_area() -> rx.Component:
    welcome_message = rx.vstack(
        rx.text("👋", style={"font_size": "2rem"}),
        rx.text(
            "Ask me anything about your code analysis — violations, complexity, best practices, or how to fix an issue.",
            style={
                "color": TEXT_MUTED,
                "font_size": "0.84rem",
                "text_align": "center",
                "line_height": "1.65",
                "max_width": "280px",
            },
        ),
        align="center",
        justify="center",
        style={"padding": "2.5rem 1rem"},
        spacing="3",
    )

    thinking_indicator = rx.hstack(
        rx.box(
            rx.text(
                "thinking...",
                style={
                    "font_family": "monospace",
                    "font_size": "0.78rem",
                    "color": GREEN,
                },
            ),
            style={
                "padding": "0.55rem 0.9rem",
                "background": BG_DARK,
                "border": f"1px solid {GREEN}33",
                "border_radius": "10px",
            },
        ),
        rx.spacer(),
    )

    return rx.scroll_area(
        rx.vstack(
            rx.cond(
                AppState.chat_messages.length() == 0,
                welcome_message,
                rx.foreach(AppState.chat_messages, chat_bubble),
            ),
            rx.cond(
                AppState.is_chatting,
                thinking_indicator,
                rx.box(),
            ),
            spacing="2",
            width="100%",
            padding="1rem",
        ),
        style={"height": "360px"},
        width="100%",
    )


def chat_input_bar() -> rx.Component:
    return rx.hstack(
        rx.input(
            value=AppState.chat_input,
            on_change=AppState.set_chat_input,
            placeholder="Ask about your analysis...",
            on_key_down=AppState.send_chat,
            style={
                "font_family": "monospace",
                "font_size": "0.82rem",
                "flex": "1",
                "background": BG_DARK,
                "border": f"1px solid {BG_BORDER}",
                "border_radius": "8px",
                "padding": "0.6rem 0.9rem",
                "color": TEXT_MAIN,
                "_focus": {
                    "outline": "none",
                    "border_color": f"{GREEN}55",
                },
                "_placeholder": {"color": TEXT_DIM},
            },
        ),
        rx.button(
            "→",
            on_click=AppState.send_chat,
            disabled=AppState.is_chatting,
            style={
                "background": f"linear-gradient(135deg, {GREEN}, {BLUE})",
                "color": "#0a0a0f",
                "font_weight": "700",
                "font_size": "1rem",
                "width": "40px",
                "height": "38px",
                "border": "none",
                "border_radius": "8px",
                "cursor": "pointer",
                "_disabled": {"opacity": "0.5", "cursor": "not-allowed"},
            },
        ),
        style={
            "padding": "0.8rem 1rem",
            "border_top": f"1px solid {BG_BORDER}",
        },
        align="center",
        spacing="2",
        width="100%",
    )


def chat_panel() -> rx.Component:
    return rx.vstack(
        chat_header(),
        chat_messages_area(),
        chat_input_bar(),
        spacing="0",
        style={
            "background": BG_PANEL,
            "border": f"1px solid {BG_BORDER}",
            "border_radius": "14px",
            "overflow": "hidden",
        },
        width="100%",
    )


# ── Page
def history_page() -> rx.Component:
    return rx.box(
        navbar(),

        rx.box(
            rx.vstack(
                # Page title
                rx.vstack(
                    rx.text(
                        "HISTORY & ASSISTANT",
                        style={
                            "font_family": "monospace",
                            "font_size": "0.68rem",
                            "letter_spacing": "0.25em",
                            "color": GREEN,
                            "text_transform": "uppercase",
                        },
                    ),
                    rx.heading(
                        "Your code journey, all in one place.",
                        style={
                            "font_family": "monospace",
                            "font_size": ["1.4rem", "1.8rem"],
                            "font_weight": "800",
                            "color": TEXT_MAIN,
                        },
                    ),
                    rx.text(
                        "Browse past analyses and chat with the AI assistant about any review.",
                        style={"color": TEXT_MUTED, "font_size": "0.9rem"},
                    ),
                    spacing="2",
                    align="start",
                ),

                # Two-column layout: history | chat
                rx.grid(
                    history_panel(),
                    chat_panel(),
                    columns="2",
                    spacing="5",
                    width="100%",
                    style={
                        "grid_template_columns": "repeat(auto-fit, minmax(320px, 1fr))",
                    },
                ),

                spacing="6",
                width="100%",
                max_width="1300px",
                padding_x=["1rem", "2rem"],
                padding_y="2.5rem",
            ),
            style={
                "display": "flex",
                "justify_content": "center",
                "background": BG_DARK,
                "min_height": "calc(100vh - 64px)",
            },
            width="100%",
        ),

        footer(),

        style={
            "min_height": "100vh",
            "background": BG_DARK,
            "display": "flex",
            "flex_direction": "column",
        },
    )