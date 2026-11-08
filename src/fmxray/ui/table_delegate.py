"""Draws 1-20 attributes as small pills tinted with their band colour."""

from PySide6.QtCore import QModelIndex, QPersistentModelIndex, QRectF, Qt
from PySide6.QtGui import QColor, QPainter
from PySide6.QtWidgets import QStyle, QStyledItemDelegate, QStyleOptionViewItem, QWidget

from fmxray.ui.table_model import PILL_ROLE
from fmxray.ui.theme import TOKENS, attribute_band

PILL_ALPHA = 40  # band colour behind the number, out of 255
PILL_RADIUS = 4
PILL_PADDING = 6  # each side of the number


def pill_colors(value: object) -> tuple[QColor, QColor] | None:
    """(background, text) for a 1-20 value; None for anything else."""
    if isinstance(value, bool) or not isinstance(value, int) or not 1 <= value <= 20:
        return None
    band = attribute_band(value)
    text = QColor(TOKENS[band]) if band else QColor(TOKENS["text"])
    background = QColor(text)
    background.setAlpha(PILL_ALPHA)
    return background, text


class AttributeDelegate(QStyledItemDelegate):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

    def paint(
        self,
        painter: QPainter,
        option: QStyleOptionViewItem,
        index: QModelIndex | QPersistentModelIndex,
    ) -> None:
        value = index.data(PILL_ROLE)
        colors = pill_colors(value)
        if colors is None:
            super().paint(painter, option, index)
            return
        background, text = colors
        item = QStyleOptionViewItem(option)
        self.initStyleOption(item, index)
        item.text = ""
        widget = item.widget
        style = widget.style() if widget is not None else None
        if style is not None:  # selection and hover backgrounds
            style.drawControl(QStyle.ControlElement.CE_ItemViewItem, item, painter, widget)
        label = str(value)
        width = item.fontMetrics.horizontalAdvance(label) + 2 * PILL_PADDING
        height = min(item.rect.height() - 6, item.fontMetrics.height() + 4)
        rect = QRectF(0, 0, width, height)
        rect.moveCenter(QRectF(item.rect).center())
        rect.moveRight(item.rect.right() - PILL_PADDING)  # numbers stay right-aligned
        painter.save()
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(background)
        painter.drawRoundedRect(rect, PILL_RADIUS, PILL_RADIUS)
        painter.setFont(item.font)
        painter.setPen(text)
        painter.drawText(rect, Qt.AlignmentFlag.AlignCenter, label)
        painter.restore()
