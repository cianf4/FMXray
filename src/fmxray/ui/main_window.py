"""Main window: career bar, quick filters, text bar, saved searches and views, table, card."""

import os
from pathlib import Path

import polars as pl
from PySide6.QtCore import QModelIndex, QPoint, Qt, QTimer
from PySide6.QtWidgets import (
    QComboBox,
    QFileDialog,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QListWidgetItem,
    QMainWindow,
    QMenu,
    QPushButton,
    QSplitter,
    QTableView,
    QVBoxLayout,
    QWidget,
)

from fmxray.application.app import App
from fmxray.application.column_views import BUILTIN_VIEWS, ColumnView
from fmxray.application.errors import FmxrayError
from fmxray.application.export import export_csv as write_csv
from fmxray.application.filters import FilterState, active_count
from fmxray.application.import_save import ImportResult, ImportStatus
from fmxray.application.save_folders import default_save_folders
from fmxray.application.search import SearchResult
from fmxray.application.session import BrowseSession
from fmxray.domain.search.errors import SearchError
from fmxray.domain.search.parser import SEARCH_SCHEMA, SortKey
from fmxray.ui.filters_dialog import FiltersDialog
from fmxray.ui.import_worker import ImportRunner
from fmxray.ui.player_card import PlayerCard
from fmxray.ui.quick_filters import QuickFilters
from fmxray.ui.table_model import PlayerTableModel
from fmxray.ui.watcher import SaveFolderWatcher

FILTER_DEBOUNCE_MS = 150  # wait for the user to stop dragging or typing
_EMPTY_FRAME = pl.DataFrame(schema={"uid": pl.Int64()})


class MainWindow(QMainWindow):
    def __init__(self, app: App, session: BrowseSession) -> None:
        super().__init__()
        self.setWindowTitle(self.tr("FM X-Ray"))
        self.app, self.session = app, session
        self._result: SearchResult | None = None
        self._refresh_timer = QTimer(self)
        self._refresh_timer.setSingleShot(True)
        self._refresh_timer.setInterval(FILTER_DEBOUNCE_MS)
        self._refresh_timer.timeout.connect(self.refresh)
        self.watcher = SaveFolderWatcher(parent=self)
        self.watcher.save_ready.connect(self._save_ready)
        self.runner = ImportRunner(app.import_factory, self)
        self.runner.imported.connect(self._imported)
        self.runner.failed.connect(self._import_failed)
        self._importing_career: str | None = None

        central = QWidget(self)
        layout = QVBoxLayout(central)
        layout.addLayout(self._career_bar())
        layout.addLayout(self._filter_bar())
        layout.addLayout(self._text_bar())
        self.empty_label = QLabel(
            self.tr(
                "No careers yet: use Import… for one save, "
                "or Watch folder… to follow FM's save folder."
            ),
            central,
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.empty_label)
        layout.addWidget(self._body(), 1)
        self.setCentralWidget(central)

        self.filters_dialog = FiltersDialog(self)
        self.filters_dialog.state_changed.connect(self._filters_changed)
        self.quick.open_all_requested.connect(self.filters_dialog.show)
        self._load_careers()

    # --- layout -----------------------------------------------------------------------

    def _career_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self.career_box, self.snapshot_box = QComboBox(self), QComboBox(self)
        self.career_box.currentTextChanged.connect(self._career_changed)
        self.snapshot_box.currentIndexChanged.connect(self._snapshot_changed)
        self.info_label = QLabel(self)
        self.info_label.setProperty("role", "muted")
        import_button = QPushButton(self.tr("Import…"), self)
        import_button.clicked.connect(self.import_dialog)
        bar.addWidget(QLabel(self.tr("Career"), self))
        bar.addWidget(self.career_box)
        bar.addWidget(QLabel(self.tr("Snapshot"), self))
        bar.addWidget(self.snapshot_box)
        bar.addWidget(self.info_label, 1)
        bar.addWidget(import_button)
        watch_button = QPushButton(self.tr("Watch folder…"), self)
        watch_button.setToolTip(self.tr("Import automatically every time FM saves"))
        watch_button.clicked.connect(self.watch_dialog)
        bar.addWidget(watch_button)
        self.career_bar = bar
        return bar

    def _filter_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self.quick = QuickFilters(self)
        self.quick.state_changed.connect(self._filters_changed)
        save, export = (
            QPushButton(self.tr("Save search"), self),
            QPushButton(self.tr("Export CSV"), self),
        )
        save.clicked.connect(self.save_search)
        export.clicked.connect(self.export_csv)
        bar.addWidget(self.quick, 1)
        bar.addWidget(save)
        bar.addWidget(export)
        return bar

    def _text_bar(self) -> QHBoxLayout:
        bar = QHBoxLayout()
        self.text_bar = QLineEdit(self)
        self.text_bar.setPlaceholderText(self.tr("Optional: type a filter, e.g. age<22 pa>180"))
        self.text_bar.textEdited.connect(self._text_edited)
        self.text_error = QLabel(self)
        self.text_error.setProperty("role", "error")
        self.text_error.hide()
        bar.addWidget(self.text_bar, 1)
        bar.addWidget(self.text_error)
        return bar

    def _body(self) -> QSplitter:
        splitter = QSplitter(self)
        side = QWidget(splitter)
        column = QVBoxLayout(side)
        column.addWidget(QLabel(self.tr("Saved searches"), side))
        self.saved_list = QListWidget(side)
        self.saved_list.currentItemChanged.connect(self._saved_chosen)
        column.addWidget(self.saved_list, 1)
        column.addWidget(QLabel(self.tr("Column views"), side))
        self.views_list = QListWidget(side)
        self.views_list.currentItemChanged.connect(self._view_chosen)
        column.addWidget(self.views_list, 1)
        save_view = QPushButton(self.tr("Save view…"), side)
        save_view.clicked.connect(self.save_view)
        column.addWidget(save_view)

        self.model = PlayerTableModel()
        self.model.sort_requested.connect(self._sort_requested)
        self.table = QTableView(splitter)
        self.table.setModel(self.model)
        self.table.setSelectionBehavior(QTableView.SelectionBehavior.SelectRows)
        self.table.setSelectionMode(QTableView.SelectionMode.SingleSelection)
        header = self.table.horizontalHeader()
        header.setSortIndicatorShown(True)
        header.sectionClicked.connect(self._header_clicked)
        header.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        header.customContextMenuRequested.connect(self._column_menu)
        self.table.selectionModel().currentRowChanged.connect(lambda *_: self._show_selected())

        self.card = PlayerCard(splitter)
        splitter.setStretchFactor(1, 1)
        self._fill_views()
        return splitter

    # --- careers and snapshots --------------------------------------------------------

    def _load_careers(self) -> None:
        careers = self.app.catalog.list_careers()
        current = self.session.career if self.session.career in careers else None
        self.career_box.blockSignals(True)
        self.career_box.clear()
        self.career_box.addItems(careers)
        self.career_box.blockSignals(False)
        if careers:
            self.career_box.setCurrentText(current or careers[0])
            self._career_changed(self.career_box.currentText())
        else:
            self.refresh()

    def _career_changed(self, name: str) -> None:
        self.session.career = name or None
        self.session.snapshot_id = None
        self._fill_snapshots()
        self._load_options()
        self._fill_saved()
        self.refresh()
        self._follow_source()

    def _follow_source(self) -> None:
        """Watch the save folder associated with the current career, if any."""
        career_id = self.app.catalog.find_career(self.session.career or "")
        source = None if career_id is None else self.app.career_sources.get(career_id)
        if source is None:
            self.watcher.stop()
        elif source != self.watcher.target:
            self.watcher.watch(source)
            self.statusBar().showMessage(self.tr("Watching %1").replace("%1", str(source)))

    def _fill_snapshots(self) -> None:
        self.snapshot_box.blockSignals(True)
        self.snapshot_box.clear()
        self.snapshot_box.addItem(self.tr("Latest"), None)
        career_id = self.app.catalog.find_career(self.session.career or "")
        if career_id is not None:
            for meta in reversed(self.app.catalog.list_snapshots(career_id)):
                self.snapshot_box.addItem(
                    f"{meta.game_date} · {meta.snapshot_id[:8]}", meta.snapshot_id
                )
        self.snapshot_box.blockSignals(False)

    def _snapshot_changed(self, index: int) -> None:
        self.session.snapshot_id = self.snapshot_box.itemData(index)
        self._load_options()
        self.refresh()

    def _load_options(self) -> None:
        try:
            for name in self.filters_dialog.choice_fields():
                self.filters_dialog.set_options(name, self.session.options(name))
        except FmxrayError as error:
            self.statusBar().showMessage(str(error))

    def reload_snapshot(self) -> None:
        """A new save was imported: show the latest snapshot, keeping filters and selection."""
        self.session.snapshot_id = None
        self._fill_snapshots()
        self._load_options()
        self._fill_saved()
        self.refresh()

    # --- filters ----------------------------------------------------------------------

    def _filters_changed(self, state: FilterState) -> None:
        self.session.set_filters(state)
        self._sync_controls()
        self.text_bar.setText(self.session.text)
        self._refresh_timer.start()

    def _text_edited(self, text: str) -> None:
        try:
            self.session.set_text(text)
        except SearchError as error:
            self.text_error.setText(str(error))
            self.text_error.show()
            return
        self.text_error.hide()
        self._sync_controls()
        self._refresh_timer.start()

    def _sync_controls(self) -> None:
        locked = self.session.advanced is not None
        for editor in (self.quick, self.filters_dialog):
            editor.set_state(self.session.filters)
            editor.set_locked(locked)
        self.quick.set_active_count(active_count(self.session.filters))

    def _header_clicked(self, section: int) -> None:
        field = self.model.columns[section]
        current = self.session.sort[0] if self.session.sort else None
        descending = not current.descending if current and current.field == field else True
        order = Qt.SortOrder.DescendingOrder if descending else Qt.SortOrder.AscendingOrder
        self.table.horizontalHeader().setSortIndicator(section, order)
        self.model.sort(section, order)

    def _sort_requested(self, field: str, descending: bool) -> None:
        self.session.sort = (SortKey(field, descending),)
        self.refresh()

    # --- results ----------------------------------------------------------------------

    def refresh(self) -> None:
        self._refresh_timer.stop()
        selected = self.selected_uid()
        try:
            result = self.session.refresh()
        except (FmxrayError, SearchError) as error:
            self.statusBar().showMessage(str(error))
            return
        self._result = result
        self.empty_label.setVisible(result is None)
        if result is None:
            self.model.set_result(_EMPTY_FRAME, (), {})
            self.info_label.setText("")
            self.card.clear()
            return
        new = self.session.new_uids()
        self.model.set_result(result.frame, self.session.view.columns, result.meta.provenance, new)
        players = result.total
        self.info_label.setText(
            self.tr("%1 players · game date %2")
            .replace("%1", f"{players:,}").replace("%2", str(result.meta.game_date))
        )  # fmt: skip
        self.filters_dialog.set_counts(active_count(self.session.filters), players)
        if result.money_fields:
            self.statusBar().showMessage(
                self.tr("Money is in the save's internal unit (not euros yet)")
            )
        self._select_uid(selected)

    def _select_uid(self, uid: int | None) -> None:
        row = None if uid is None else self.model.row_of(uid)
        if row is None:
            self.table.clearSelection()
            self.table.setCurrentIndex(QModelIndex())
            self.card.clear()
            return
        self.table.selectRow(row)
        self._show_selected()

    def selected_uid(self) -> int | None:
        index = self.table.currentIndex()
        if not index.isValid() or index.row() >= self.model.rowCount():
            return None
        return self.model.uid_at(index.row())

    def _show_selected(self) -> None:
        uid = self.selected_uid()
        if uid is None or self._result is None:
            self.card.clear()
            return
        rows = self._result.frame.filter(pl.col("uid") == uid).to_dicts()
        if rows:
            self.card.show_player(self._result.meta, rows[0])

    # --- saved searches, views, export, import ---------------------------------------

    def _fill_saved(self) -> None:
        counts = self.session.saved_new_counts()
        self.saved_list.blockSignals(True)
        self.saved_list.clear()
        for search in self.app.saved_searches.list():
            new = counts.get(search.name, 0)
            item = QListWidgetItem(search.name + (f"  +{new}" if new else ""), self.saved_list)
            item.setData(Qt.ItemDataRole.UserRole, search.name)
            item.setToolTip(search.query_text)
        self.saved_list.blockSignals(False)

    def _saved_chosen(self, item: QListWidgetItem | None) -> None:
        if item is None:
            return
        self.session.open_saved(item.data(Qt.ItemDataRole.UserRole))
        self._sync_controls()
        self.text_bar.setText(self.session.text)
        self.text_error.hide()
        self.refresh()

    def save_search(self) -> None:
        name, ok = QInputDialog.getText(self, self.tr("Save search"), self.tr("Name"))
        if not ok or not name.strip():
            return
        try:
            self.app.save_search.execute(name.strip(), self.session.text)
        except (FmxrayError, SearchError) as error:
            self.statusBar().showMessage(str(error))
            return
        self._fill_saved()

    def _fill_views(self) -> None:
        self.views_list.blockSignals(True)
        self.views_list.clear()
        for view in (*BUILTIN_VIEWS, *self.app.column_views.list()):
            item = QListWidgetItem(view.name, self.views_list)
            item.setData(Qt.ItemDataRole.UserRole, view.columns)
        self.views_list.blockSignals(False)

    def _view_chosen(self, item: QListWidgetItem | None) -> None:
        if item is not None:
            self._set_view(ColumnView(item.text(), tuple(item.data(Qt.ItemDataRole.UserRole))))

    def _set_view(self, view: ColumnView) -> None:
        self.session.view = view
        if self._result is not None:
            selected = self.selected_uid()
            meta = self._result.meta
            self.model.set_result(
                self._result.frame, view.columns, meta.provenance, self.session.new_uids()
            )
            self._select_uid(selected)

    def _column_menu(self, point: QPoint) -> None:
        menu = QMenu(self)
        shown = self.session.view.columns
        for name in SEARCH_SCHEMA.names():
            action = menu.addAction(name)
            action.setCheckable(True)
            action.setChecked(name in shown)
            action.setEnabled(name != "name")
            action.toggled.connect(lambda on, n=name: self._toggle_column(n, on))
        menu.exec(self.table.horizontalHeader().mapToGlobal(point))

    def _toggle_column(self, name: str, on: bool) -> None:
        columns = [c for c in self.session.view.columns if c != name] + ([name] if on else [])
        self._set_view(ColumnView(self.tr("Custom"), tuple(columns)))

    def save_view(self) -> None:
        name, ok = QInputDialog.getText(self, self.tr("Save view"), self.tr("Name"))
        if ok and name.strip():
            self.app.column_views.save(ColumnView(name.strip(), self.session.view.columns))
            self._fill_views()

    def export_csv(self) -> None:
        if self._result is None:
            return
        path, _ = QFileDialog.getSaveFileName(self, self.tr("Export CSV"), "", "CSV (*.csv)")
        if not path:
            return
        rows = write_csv(self._result.frame, Path(path), self.session.view.columns)
        self.statusBar().showMessage(
            self.tr("Wrote %1 rows to %2").replace("%1", str(rows)).replace("%2", path)
        )

    def import_dialog(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, self.tr("Import a save"), "", "FM saves (*.fm)")
        if not path:
            return
        default = self.session.career or Path(path).stem
        career, ok = QInputDialog.getText(
            self, self.tr("Career"), self.tr("Career name"), text=default
        )
        if ok and career.strip():
            self.import_save(Path(path), career.strip())

    def import_save(self, path: Path, career: str) -> None:
        """Imports on the worker thread; the table reloads when it is done."""
        self._importing_career = career
        self.statusBar().showMessage(self.tr("Importing %1…").replace("%1", path.name))
        self.runner.start(path, career)

    def watch_dialog(self) -> None:
        suggested = default_save_folders(os.environ, Path.home())
        start = str(suggested[0]) if suggested else ""
        folder = QFileDialog.getExistingDirectory(self, self.tr("Folder FM saves into"), start)
        if not folder:
            return
        default = self.session.career or "Career"
        title, label = self.tr("Career"), self.tr("Career fed by this folder")
        career, ok = QInputDialog.getText(self, title, label, text=default)
        if ok and career.strip():
            self.follow_folder(Path(folder), career.strip())

    def follow_folder(self, folder: Path, career: str) -> None:
        """Associates `folder` with `career`, imports its newest save and watches it."""
        career_id = self.app.catalog.get_or_create_career(career)
        self.app.career_sources.set(career_id, folder)
        self.session.career = career
        saves = (
            sorted(folder.glob("*.fm"), key=lambda p: p.stat().st_mtime)
            if folder.is_dir()
            else [folder]
        )
        if saves and saves[-1].exists():
            self.import_save(saves[-1], career)
        self._load_careers()

    def _save_ready(self, path: Path) -> None:
        if self.session.career is not None:
            self.import_save(path, self.session.career)

    def _imported(self, result: ImportResult) -> None:
        career, self._importing_career = self._importing_career, None
        if result.status is ImportStatus.ALREADY_IMPORTED:
            self.statusBar().showMessage(self.tr("Already imported"))
            return
        self.statusBar().showMessage(
            self.tr("Imported %1 players").replace("%1", f"{result.meta.row_count:,}")
        )
        if career is not None and career != self.session.career:
            self.session.career = career
        if self.career_box.findText(self.session.career or "") < 0:
            self._load_careers()
        else:
            self.reload_snapshot()

    def _import_failed(self, message: str) -> None:
        self._importing_career = None
        self.statusBar().showMessage(self.tr("Import failed: %1").replace("%1", message))
