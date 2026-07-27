from __future__ import annotations

import pyqtgraph as pg
from PyQt5 import QtGui


NODE_COLORS = {}

GRAPH_STYLESHEET = """
QWidget {
    background: #171819;
    color: #d7dce2;
    font-size: 11px;
}
QMenu {
    background: #26292d;
    border: 1px solid #3d424a;
    padding: 4px;
}
QMenu::item {
    padding: 5px 22px 5px 10px;
    border-radius: 3px;
}
QMenu::item:selected {
    background: #3e6ea8;
}
"""

NODE_WIDGET_STYLESHEET = """
QWidget#LedNodeBody {
    background: __NODE_BACKGROUND__;
    border: 1px solid #101214;
    border-top: 0;
}
QWidget[ledRole="elementRow"] {
    background: #2b2f34;
    border-bottom: 1px solid #202327;
}
QWidget[ledRole="elementRow"]:hover {
    background: #31363c;
}
QLabel[ledRole="elementName"] {
    color: #cfd5dd;
    font-weight: 600;
}
QLabel[ledRole="elementValue"] {
    color: #e5e9ef;
    background: #1d2024;
    border: 1px solid #383e46;
    border-radius: 3px;
    padding: 3px 6px;
}
QWidget[ledRole="valueControls"] {
    background: transparent;
}
QLineEdit, QComboBox {
    color: #eef3f8;
    background: #1c1f23;
    border: 1px solid #3c444d;
    border-radius: 3px;
    padding: 3px 6px;
    selection-background-color: #4f86c6;
}
QLineEdit:focus, QComboBox:focus {
    border-color: #69a7e8;
}
QComboBox::drop-down {
    width: 18px;
    border: 0;
}
QComboBox QAbstractItemView {
    color: #eef3f8;
    background: #24282e;
    border: 1px solid #414852;
    selection-background-color: #3e6ea8;
    outline: 0;
}
QPushButton {
    color: #eef3f8;
    background: #2f3842;
    border: 1px solid #46515d;
    border-radius: 3px;
    padding: 3px 8px;
}
QPushButton:hover {
    background: #3a4652;
}
QDial {
    background: transparent;
}
"""


def node_accent(module_name: str | None = None) -> str:
    if module_name is None:
        return "#7b5cc7"
    try:
        from frontend.registry.registry import node_color_for_module

        return node_color_for_module(module_name)
    except Exception:
        return "#7b5cc7"


def darken(hex_color: str, amount: int = 32) -> str:
    color = QtGui.QColor(hex_color)
    return QtGui.QColor(
        max(color.red() - amount, 0),
        max(color.green() - amount, 0),
        max(color.blue() - amount, 0),
    ).name()


def tint(hex_color: str, ratio: float = 0.16, base: str = "#24272b") -> str:
    color = QtGui.QColor(hex_color)
    base_color = QtGui.QColor(base)
    return QtGui.QColor(
        round(base_color.red() * (1 - ratio) + color.red() * ratio),
        round(base_color.green() * (1 - ratio) + color.green() * ratio),
        round(base_color.blue() * (1 - ratio) + color.blue() * ratio),
    ).name()


def node_widget_stylesheet(module_name: str | None = None) -> str:
    return NODE_WIDGET_STYLESHEET.replace(
        "__NODE_BACKGROUND__",
        tint(node_accent(module_name), 0.08, "#30343a"),
    )


def apply_node_graphics_style(item, name: str, module_name: str | None = None) -> None:
    accent = node_accent(module_name)
    item.setPen(pg.mkPen(darken(accent, 46), width=1.2))
    item.setBrush(pg.mkBrush(QtGui.QColor(tint(accent, 0.14, "#2b2f34"))))
    item.hoverBrush = pg.mkBrush(QtGui.QColor(tint(accent, 0.24)))
    item.selectBrush = pg.mkBrush(42, 48, 58, 255)
    item.selectPen = pg.mkPen(QtGui.QColor("#9cc9ff"), width=2)
    item.nameItem.setDefaultTextColor(QtGui.QColor("#edf2f7"))


def style_terminal(terminal_item, io: str, accent: str, linked: bool = False) -> None:
    fill = QtGui.QColor(accent)
    pen = QtGui.QPen(QtGui.QColor("#d7dce2"))
    pen.setWidthF(1.1)
    terminal_item.setBrush(pg.mkBrush(fill))
    terminal_item.box.setPen(pen)
    terminal_item.box.setRect(0, 0, 12, 12)


def color_button_stylesheet(hex_value: str) -> str:
    color = QtGui.QColor(hex_value)
    text_color = "#111417" if color.lightness() > 150 else "#f8fafc"
    return (
        "QPushButton {"
        f"background-color: {hex_value};"
        "border: 1px solid #111417;"
        "border-radius: 4px;"
        f"color: {text_color};"
        "font-weight: 700;"
        "}"
        "QPushButton:hover { border-color: #d7dce2; }"
    )
