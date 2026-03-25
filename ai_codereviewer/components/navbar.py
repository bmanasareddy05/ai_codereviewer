import reflex as rx
from ai_codereviewer.state import AppState
from ai_codereviewer.components.colors import (
    BG_DARK, BG_PANEL, BG_BORDER, 
    GREEN, BLUE, TEXT_MAIN, TEXT_MUTED
)

def nav_link(label: str, href: str) -> rx.Component:
    # Check if this link matches the current browser path
    is_active = rx.State.router.page.full_path == href
    
    return rx.link(
        rx.vstack(
            rx.text(
                label,
                style={
                    "color": rx.cond(is_active, TEXT_MAIN, TEXT_MUTED),
                    "font_family": "monospace",
                    "font_weight": rx.cond(is_active, "700", "500"),
                    "font_size": "0.85rem",
                    "transition": "color 0.2s",
                    "_hover": {"color": TEXT_MAIN},
                },
            ),
            rx.box(
                style={
                    "width": rx.cond(is_active, "100%", "0%"),
                    "height": "2px",
                    "background": GREEN,
                    "transition": "width 0.2s",
                }
            ),
            spacing="1",
            align="center",
        ),
        href=href,
        style={"text_decoration": "none"},
    )

def navbar() -> rx.Component:
    """
    The main navigation bar at the top of every page.
    GitHub section has been removed for a cleaner look.
    """
    return rx.box(
        rx.hstack(
            # Logo Section
            rx.link(
                rx.hstack(
                    rx.box(
                        rx.text("⬡", style={"font_size": "1.5rem", "color": GREEN}),
                        style={"padding": "4px"}
                    ),
                    rx.text(
                        "AI_REVIEWER",
                        style={
                            "font_family": "monospace",
                            "font_weight": "800",
                            "letter_spacing": "0.1em",
                            "color": TEXT_MAIN,
                            "font_size": "1rem",
                        },
                    ),
                    align="center",
                    spacing="2",
                ),
                href="/",
                style={"text_decoration": "none"},
            ),
            
            rx.spacer(),
            # Navigation Links
            rx.hstack(
                nav_link("Home", "/"),
                nav_link("Analyser", "/analyser"), 
                nav_link("History", "/history"),
                spacing="7",
                align="center",
            ),
            
            rx.spacer(),
            width="100%",
            max_width="1400px",
            padding_x="2rem",
            align="center",
        ),
        style={
            "width": "100%",
            "height": "64px",
            "background": f"{BG_DARK}aa",
            "backdrop_filter": "blur(10px)",
            "border_bottom": f"1px solid {BG_BORDER}",
            "position": "sticky",
            "top": "0",
            "z_index": "1000",
            "display": "flex",
            "justify_content": "center",
        },
    )