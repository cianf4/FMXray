"""Min-max (or min-only) control for one field: spin boxes on fixed scales, text boxes otherwise."""

from datetime import date

import polars as pl
from PySide6.QtCore import QSignalBlocker, Signal
from PySide6.QtWidgets import QHBoxLayout, QLabel, QLineEdit, QSpinBox, QWidget

from fmxray.application.filter_layout import slider_bounds
from fmxray.application.filters import Range
from fmxray.domain.search.parser import SEARCH_SCHEMA
from fmxray.domain.search.spec import Value


def _parse(dtype: pl.DataType, text: str) -> Value | None:
    text = text.strip()
    if not text:
        return None
    try:
        if isinstance(dtype, pl.Date):
            return date.fromisoformat(text)
        if dtype.is_integer():
            return int(text)
        return float(text)
    except ValueError:
        return None  # half-typed: no filter until it parses


class RangeControl(QWidget):
    range_changed = Signal(str, object)  # field, Range (Range() = no filter)

    def __init__(self, field: str, parent: QWidget | None = None, min_only: bool = False) -> None:
        super().__init__(parent)
        self.field = field
        self._min_only = min_only
        self._dtype = SEARCH_SCHEMA[field]
        self._bounds = slider_bounds(field)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._low: QSpinBox | QLineEdit
        self._high: QSpinBox | QLineEdit
        if self._bounds is not None:
            lo, hi = self._bounds
            self._low, self._high = QSpinBox(self), QSpinBox(self)
            for box, start, hint in ((self._low, lo, "min"), (self._high, hi, "")):
                box.setRange(lo, hi)
                box.setValue(start)
                if hint:  # the low box shows "min" while it sits on the scale's bottom
                    box.setSpecialValueText(self.tr(hint))
                box.valueChanged.connect(self._changed)
        else:
            hint = "YYYY-MM-DD" if isinstance(self._dtype, pl.Date) else ""
            self._low, self._high = QLineEdit(self), QLineEdit(self)
            for edit, placeholder in ((self._low, self.tr("min")), (self._high, self.tr("max"))):
                edit.setPlaceholderText(f"{placeholder} {hint}".strip())
                edit.textChanged.connect(self._changed)
        layout.addWidget(self._low)
        if min_only:  # the max box exists but stays out of the layout and out of range()
            self._high.hide()
            self._high.setParent(None)
            return
        layout.addWidget(QLabel("\u2013", self))  # en dash
        layout.addWidget(self._high)

    def range(self) -> Range:
        if isinstance(self._low, QSpinBox) and isinstance(self._high, QSpinBox):
            assert self._bounds is not None
            lo, hi = self._bounds
            low, high = self._low.value(), self._high.value()
            return Range(None if low == lo else low, None if high == hi or self._min_only else high)
        assert isinstance(self._low, QLineEdit) and isinstance(self._high, QLineEdit)
        top = None if self._min_only else _parse(self._dtype, self._high.text())
        return Range(_parse(self._dtype, self._low.text()), top)

    def set_range(self, value: Range, emit: bool = False) -> None:
        for box, bound, default in (
            (self._low, value.low, 0), (self._high, value.high, 1),
        ):  # fmt: skip
            with QSignalBlocker(box):
                if isinstance(box, QSpinBox):
                    assert self._bounds is not None
                    box.setValue(
                        int(bound) if isinstance(bound, int | float) else self._bounds[default]
                    )
                else:
                    box.setText("" if bound is None else str(bound))
        if emit:
            self._changed()

    def _changed(self) -> None:
        self.range_changed.emit(self.field, self.range())
