import reflex as rx
from ai_codereviewer.components.colors import (
    BG_DARK, BG_BORDER, BG_PANEL, GREEN, BLUE, PURPLE,
    TEXT_MAIN, TEXT_MUTED, TEXT_DIM
)


# Sample code shown in the hero preview box
SAMPLE_CODE = """import os
import sys   # unused import

def process(data, x):
    result = data * 2
    unused_var = 42   # will be flagged

    return result

# code after return ← unreachable
print("done")"""


def hero_badge() -> rx.Component:
    return rx.hstack(
        # Pulsing green dot
        rx.box(
            style={
                "width": "7px",
                "height": "7px",
                "border_radius": "50%",
                "background": GREEN,
            },
        ),
        rx.text(
            "Static Analysis + AI Suggestions",
            style={
                "font_family": "monospace",
                "font_size": "0.72rem",
                "letter_spacing": "0.12em",
                "text_transform": "uppercase",
                "color": GREEN,
            },
        ),
        style={
            "display": "inline_flex",
            "align_items": "center",
            "gap": "0.5rem",
            "padding": "0.35rem 0.9rem",
            "border": f"1px solid {GREEN}44",
            "border_radius": "99px",
            "background": f"{GREEN}0a",
        },
    )


def hero_headline() -> rx.Component:
    return rx.vstack(
        rx.text("Catch bugs before"),
        rx.text(
            "they catch you.",
            style={
                # Gradient text effect: green → blue
                "background": f"linear-gradient(135deg, {GREEN}, {BLUE})",
                "background_clip": "text",
                "-webkit-background-clip": "text",
                "color": "transparent",
            },
        ),
        style={
            "font_family": "monospace",
            "font_size": ["2.2rem", "3rem", "3.8rem"],
            "font_weight": "800",
            "line_height": "1.1", 
            "color": TEXT_MAIN,
            "text_align": "center",
            "letter_spacing": "-0.02em",
            "width": "100%",
        },
        spacing="0", 
        align="center",
    )

def hero_description() -> rx.Component:
    return rx.text(
        "Drop your Python, C, C++, or Java code into CodeReview.ai and get instant "
        "static analysis, AI-powered suggestions, and a quality score — all in seconds.",
        style={
            "color": TEXT_MUTED,
            "font_size": ["0.92rem", "1rem"],
            "max_width": "540px",
            "text_align": "center",
            "line_height": "1.75",
        },
    )


def hero_buttons() -> rx.Component:
    return rx.hstack(
        rx.link(
            "Start Analysing →",
            href="/analyser",
            style={
                "background": f"linear-gradient(135deg, {GREEN}, {BLUE})",
                "color": "#0a0a0f",
                "font_family": "monospace",
                "font_weight": "700",
                "font_size": "0.88rem",
                "padding": "0.8rem 1.8rem",
                "border_radius": "10px",
                "text_decoration": "none",
                "transition": "opacity 0.2s, transform 0.2s",
                "_hover": {
                    "opacity": "0.88",
                    "transform": "translateY(-2px)",
                },
            },
        ),
        rx.link(
            "View History",
            href="/history",
            style={
                "color": TEXT_MUTED,
                "font_family": "monospace",
                "font_size": "0.88rem",
                "text_decoration": "none",
                "padding": "0.8rem 1.4rem",
                "border": f"1px solid {BG_BORDER}",
                "border_radius": "10px",
                "transition": "all 0.2s",
                "_hover": {
                    "color": TEXT_MAIN,
                    "border_color": "#475569",
                },
            },
        ),
        spacing="3",
        flex_wrap="wrap",
        justify="center",
    )


def code_preview_box() -> rx.Component:
    return rx.box(
        rx.hstack(
            rx.box(style={"width": "12px", "height": "12px", "border_radius": "50%", "background": "#ff5f57"}),
            rx.box(style={"width": "12px", "height": "12px", "border_radius": "50%", "background": "#febc2e"}),
            rx.box(style={"width": "12px", "height": "12px", "border_radius": "50%", "background": "#28c840"}),
            rx.spacer(),
            rx.text(
                "sample.py",
                style={
                    "color": TEXT_DIM,
                    "font_size": "0.72rem",
                    "font_family": "monospace",
                },
            ),
            style={
                "padding": "0.7rem 1rem",
                "border_bottom": f"1px solid {BG_BORDER}",
            },
            align="center",
        ),
        rx.box(
            rx.text(
                SAMPLE_CODE,
                style={
                    "font_family": "monospace",
                    "font_size": "0.8rem",
                    "color": TEXT_MUTED,
                    "white_space": "pre",
                    "line_height": "1.8",
                    "padding": "1.2rem 1.4rem",
                },
            ),
        ),
        style={
            "background": BG_PANEL,
            "border": f"1px solid {BG_BORDER}",
            "border_radius": "12px",
            "max_width": "440px",
            "width": "100%",
            "overflow": "hidden",
            "box_shadow": f"0 0 50px {GREEN}0e",
        },
    )


def hero() -> rx.Component:
    return rx.box(
        # Grid Background
        rx.box(
            style={
                "position": "absolute",
                "inset": "0",
                "background_image": (
                    f"linear-gradient(to right, {BG_BORDER} 1px, transparent 1px), "
                    f"linear-gradient(to bottom, {BG_BORDER} 1px, transparent 1px)"
                ),
                "background_size": "48px 48px",
                "opacity": "0.3",
                "pointer_events": "none",
            },
        ),
        # Green Glow Top
        rx.box(
            style={
                "position": "absolute",
                "width": "600px",
                "height": "600px",
                "border_radius": "50%",
                "background": f"radial-gradient(circle, {GREEN}16 0%, transparent 70%)",
                "top": "-200px",
                "left": "50%",
                "transform": "translateX(-50%)",
                "pointer_events": "none",
            },
        ),
        # Purple Glow Bottom
        rx.box(
            style={
                "position": "absolute",
                "width": "350px",
                "height": "350px",
                "border_radius": "50%",
                "background": f"radial-gradient(circle, {PURPLE}0e 0%, transparent 70%)",
                "bottom": "0",
                "right": "8%",
                "pointer_events": "none",
            },
        ),

        rx.vstack(
            hero_badge(),
            hero_headline(),
            hero_description(),
            hero_buttons(),
            code_preview_box(),
            spacing="6",
            align="center",
            padding_x="2rem",
            padding_y="6rem",
            style={
                "position": "relative",
                "z_index": "1",
            },
        ),

        style={
            "position": "relative",
            "overflow": "hidden",
            "background": BG_DARK,
            "min_height": "90vh",
            "display": "flex",
            "align_items": "center",
            "justify_content": "center",
        },
        width="100%",
    )