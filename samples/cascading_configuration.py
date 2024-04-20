from dataclasses import dataclass
from dataclasses import field

from dynascope import dynamic
from dynascope import scope_manager


@dataclass
class Border:
    corners: str = "square"
    width: float = 1.0
    color: str = "black"
    ...

    def _css_style(self):
        border_radius = 4 if self.corners == "rounded" else 0
        return f"border: {self.width}px solid {self.color}; border-radius: {border_radius}px"


def border(corners="square", width=1.0, color="black"):
    return scope_manager(style.border, corners=corners, width=width, color=color)


@dataclass
class Background:
    color: str = "white"
    ...

    def _css_style(self):
        return f"background-color: {self.color}"


def background(color="white"):
    return scope_manager(style.background, color=color)


@dataclass
class Text:
    color: str = "black"
    ...

    def _css_style(self):
        return f"color: {self.color}"


def text(color="black"):
    return scope_manager(style.text, color=color)


@dataclass
class Style:
    border: Border = field(default_factory=Border)
    background: Background = field(default_factory=Background)
    text: Text = field(default_factory=Text)

    def _css_style(self, extras=None):
        styles = [self.border, self.background, self.text]
        if extras:
            styles.extend(extras)
        return str("; ".join(item if isinstance(item, str) else item._css_style() for item in styles))


style = dynamic(Style)


class Page:
    def __init__(self):
        self.html = ""

    def add(self, html_fragment):
        self.html += html_fragment

    def render(self):
        return f"<html><body>{self.html}</body></html>"


def button(text, x=0, y=0):
    position = f"position: absolute; left: {x}px; top: {y}px"
    return f'<button style="{style._css_style(extras=[position])}">{text}</button>'
