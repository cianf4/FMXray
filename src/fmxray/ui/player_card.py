"""Side panel with the selected player, drawn in Qt Quick (QML) for smooth GPU animations.

The card keeps the widget interface the main window uses; CardModel prepares the content.
"""

from collections.abc import Mapping
from pathlib import Path

from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor
from PySide6.QtQuickWidgets import QQuickWidget
from PySide6.QtWidgets import QLabel, QVBoxLayout, QWidget

from fmxray.domain.snapshot import SnapshotMeta
from fmxray.ui.card_model import CardModel
from fmxray.ui.theme import CARD_ANIMATION_MS, TOKENS

CARD_QML = Path(__file__).parent / "qml" / "PlayerCard.qml"
CARD_INSET_PX = 5  # keeps the square QML surface inside the panel's rounded corners


class PlayerCard(QWidget):
    def __init__(self, parent: QWidget | None = None, qml: Path = CARD_QML) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(CARD_INSET_PX, CARD_INSET_PX, CARD_INSET_PX, CARD_INSET_PX)
        self.view = QQuickWidget(self)
        # Owned by the view: Qt tears the QML down first, so no binding reads a dead model.
        self.model = CardModel(self.view)
        self.view.setResizeMode(QQuickWidget.ResizeMode.SizeRootObjectToView)
        self.view.setClearColor(QColor(TOKENS["surface"]))
        context = self.view.rootContext()
        context.setContextProperty("card", self.model)
        context.setContextProperty("theme", {**TOKENS, "animationMs": CARD_ANIMATION_MS})
        self.view.setSource(QUrl.fromLocalFile(str(qml)))
        if self.view.status() == QQuickWidget.Status.Error:
            errors = "\n".join(error.toString() for error in self.view.errors())
            message = QLabel(self.tr("The player card could not load:\n%1").replace("%1", errors))
            message.setProperty("role", "error")
            message.setWordWrap(True)
            layout.addWidget(message)
            self.view.hide()
        else:
            layout.addWidget(self.view)

    def show_player(self, meta: SnapshotMeta, values: Mapping[str, object]) -> None:
        self.model.set_player(meta, values)

    def clear(self) -> None:
        self.model.clear()

    def copy_name(self) -> None:
        self.model.copyName()
