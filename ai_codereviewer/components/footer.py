import reflex as rx
from ai_codereviewer.components.colors import (
    BG_SURFACE, BG_BORDER, BG_PANEL, GREEN, TEXT_MAIN, TEXT_MUTED, TEXT_DIM
)
FOOTER_LINKS = [
    ("Home",     "/"),
    ("Analyser", "/analyser"),
    ("History",  "/history"),
]


def footer_logo() -> rx.Component:
    return rx.vstack(
        rx.hstack(
            rx.text(
                "⬡",
                style={"color": GREEN, "font_size": "1.1rem"},
            ),
            rx.text(
                "Codereview.ai",
                style={
                    "font_family": "monospace",
                    "font_weight": "700",
                    "color": TEXT_MAIN,
                    "font_size": "0.95rem",
                },
            ),
            spacing="2",
            align="center",
        ),
        rx.text(
            "AI-powered static analysis and code review for Python, C, C++ and Java.",
            style={
                "color": TEXT_MUTED,
                "font_size": "0.82rem",
                "max_width": "280px",
                "line_height": "1.6",
            },
        ),
        spacing="2",
        align="start",
    )


def footer_links() -> rx.Component:
    """Navigation links inside the footer."""
    return rx.hstack(
        *[
            rx.link(
                label,
                href=href,
                style={
                    "color": TEXT_MUTED,
                    "font_size": "0.82rem",
                    "font_family": "monospace",
                    "text_decoration": "none",
                    "_hover": {"color": GREEN},
                },
            )
            for label, href in FOOTER_LINKS
        ],
        spacing="5",
    )


def status_indicator() -> rx.Component:
    return rx.hstack(
        rx.box(
            style={
                "width": "6px",
                "height": "6px",
                "border_radius": "50%",
                "background": GREEN,
            },
        ),
        rx.text(
            "All systems operational",
            style={
                "color": TEXT_MUTED,
                "font_size": "0.73rem",
            },
        ),
        spacing="2",
        align="center",
    )


def footer() -> rx.Component:
    return rx.box(
        rx.vstack(
            # Divider line at the top of footer
            rx.divider(
                style={
                    "border_color": BG_BORDER,
                    "margin_bottom": "1.5rem",
                },
            ),

            # Top row: logo and links
            rx.hstack(
                footer_logo(),
                rx.spacer(),
                footer_links(),
                width="100%",
                align="start",
                flex_wrap="wrap",
                spacing="4",
            ),

            rx.box(style={"height": "1.2rem"}),  # spacer

            # Bottom row: copyright and status
            rx.hstack(
                rx.text(
                    "© 2025 Codereview.ai — Built with Reflex",
                    style={
                        "color": TEXT_DIM,
                        "font_size": "0.75rem",
                        "font_family": "monospace",
                    },
                ),
                rx.spacer(),
                status_indicator(),
                width="100%",
                align="center",
            ),

            spacing="0",
            width="100%",
        ),
        style={
            "padding": "2rem 2.5rem 1.5rem",
            "background": BG_SURFACE,
            "border_top": f"1px solid {BG_BORDER}",
            "margin_top": "auto",
        },
        width="100%",
    )