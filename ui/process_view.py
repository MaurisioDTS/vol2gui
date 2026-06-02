"""Vista de procesos: PSlist (tabla) y PStree (árbol jerárquico).

Es agnóstica al SO: recibe el ``OSType`` y elige los nombres de plugin
adecuados (pslist/pstree para Windows, linux_*/mac_* para el resto). Doble
clic sobre un proceso abre una ventana de detalle con dlllist, cmdline y
handles de ese PID (cuando el SO lo soporta).
"""

from __future__ import annotations

from typing import Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTabWidget,
    QTextEdit,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.parser import parse_pstree, parse_table
from core.profile import OSType
from core.runner import PluginWorker, VolatilityRunner
from utils import audit_log

# Mapeo de plugins por SO.
_PLUGINS = {
    OSType.WINDOWS: {
        "pslist": "pslist",
        "pstree": "pstree",
        "detail": [("Línea de comando", "cmdline"), ("DLLs", "dlllist"), ("Handles", "handles")],
        "pid_flag": "-p",
    },
    OSType.LINUX: {
        "pslist": "linux_pslist",
        "pstree": "linux_pstree",
        "detail": [("Argumentos", "linux_psaux"), ("Mapas", "linux_proc_maps")],
        "pid_flag": "-p",
    },
    OSType.MAC: {
        "pslist": "mac_pslist",
        "pstree": "mac_pstree",
        "detail": [("Mapas dyld", "mac_dyld_maps"), ("Entorno", "mac_psenv")],
        "pid_flag": "-p",
    },
}


def _plugins_for(os_type: OSType) -> Dict:
    return _PLUGINS.get(os_type, _PLUGINS[OSType.WINDOWS])


class ProcessView(QWidget):
    """Pestaña con sub-pestañas PSlist y PStree."""

    def __init__(
        self,
        runner: VolatilityRunner,
        os_type: OSType,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._os_type = os_type
        self._plugins = _plugins_for(os_type)
        self._workers: List[PluginWorker] = []
        self._detail_windows: List[QWidget] = []
        self._loaded = False
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        self._reload_btn = QPushButton("Recargar procesos")
        self._reload_btn.clicked.connect(self.load)
        controls.addWidget(self._reload_btn)
        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filtrar por nombre o PID...")
        self._filter.textChanged.connect(self._apply_filter)
        controls.addWidget(self._filter, 1)
        layout.addLayout(controls)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, 1)

        # --- PSlist (tabla) ---
        self._pslist_table = QTableWidget()
        self._pslist_table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._pslist_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._pslist_table.setSortingEnabled(True)
        self._pslist_table.doubleClicked.connect(self._on_table_double_click)
        self._tabs.addTab(self._pslist_table, "PSList")

        # --- PStree (árbol) ---
        self._pstree = QTreeWidget()
        self._pstree.setHeaderLabels(["Proceso", "PID", "PPID"])
        self._pstree.itemDoubleClicked.connect(self._on_tree_double_click)
        self._tabs.addTab(self._pstree, "PSTree")

        hint = QLabel("Doble clic en un proceso para ver su detalle (cmdline, DLLs, handles).")
        hint.setStyleSheet("color:#888;font-size:11px;")
        layout.addWidget(hint)

    # ----------------------------------------------------------------- carga --
    def load(self) -> None:
        self._loaded = True
        self._progress.show()
        self._reload_btn.setEnabled(False)

        ps_plugin = self._plugins["pslist"]
        tree_plugin = self._plugins["pstree"]

        audit_log.log_plugin(ps_plugin, self._runner.command_string(ps_plugin))
        ps_worker = self._runner.run_async(ps_plugin)
        ps_worker.finished_ok.connect(self._on_pslist)
        ps_worker.failed.connect(self._on_failed)
        self._workers.append(ps_worker)

        audit_log.log_plugin(tree_plugin, self._runner.command_string(tree_plugin))
        tree_worker = self._runner.run_async(tree_plugin)
        tree_worker.finished_ok.connect(self._on_pstree)
        tree_worker.failed.connect(self._on_failed)
        self._workers.append(tree_worker)

    def load_if_needed(self) -> None:
        if not self._loaded:
            self.load()

    def _on_pslist(self, _plugin: str, output: str) -> None:
        headers, rows = parse_table(output)
        self._pslist_headers = headers or ["Salida"]
        self._pslist_table.setSortingEnabled(False)
        self._pslist_table.setColumnCount(len(self._pslist_headers))
        self._pslist_table.setHorizontalHeaderLabels(self._pslist_headers)
        self._pslist_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c in range(len(self._pslist_headers)):
                value = row[c] if c < len(row) else ""
                self._pslist_table.setItem(r, c, QTableWidgetItem(value))
        self._pslist_table.resizeColumnsToContents()
        self._pslist_table.setSortingEnabled(True)
        self._maybe_done()

    def _on_pstree(self, _plugin: str, output: str) -> None:
        nodes = parse_pstree(output)
        self._pstree.clear()
        stack: List[QTreeWidgetItem] = []
        for node in nodes:
            item = QTreeWidgetItem([node["name"], node["pid"], node["ppid"]])
            depth = node["depth"]
            # Ajusta la pila para encontrar el padre según la profundidad.
            while len(stack) > depth:
                stack.pop()
            if stack:
                stack[-1].addChild(item)
            else:
                self._pstree.addTopLevelItem(item)
            stack.append(item)
        self._pstree.expandAll()
        self._maybe_done()

    def _maybe_done(self) -> None:
        if all(not w.isRunning() for w in self._workers):
            self._progress.hide()
            self._reload_btn.setEnabled(True)

    def _on_failed(self, plugin: str, message: str) -> None:
        self._progress.hide()
        self._reload_btn.setEnabled(True)
        QMessageBox.warning(self, f"Error en {plugin}", message)

    # ---------------------------------------------------------------- filtro --
    def _apply_filter(self, text: str) -> None:
        text = text.lower().strip()
        for r in range(self._pslist_table.rowCount()):
            visible = not text
            if not visible:
                for c in range(self._pslist_table.columnCount()):
                    item = self._pslist_table.item(r, c)
                    if item and text in item.text().lower():
                        visible = True
                        break
            self._pslist_table.setRowHidden(r, not visible)
        self._filter_tree(self._pstree.invisibleRootItem(), text)

    def _filter_tree(self, parent: QTreeWidgetItem, text: str) -> bool:
        any_visible = False
        for i in range(parent.childCount()):
            child = parent.child(i)
            child_match = self._filter_tree(child, text)
            own_match = (not text) or any(
                text in (child.text(c) or "").lower() for c in range(child.columnCount())
            )
            visible = child_match or own_match
            child.setHidden(not visible)
            any_visible = any_visible or visible
        return any_visible

    # ----------------------------------------------------- detalle de proceso --
    def _on_table_double_click(self, index) -> None:
        row = index.row()
        pid = self._find_pid_in_table(row)
        name = self._find_name_in_table(row)
        if pid:
            self._open_detail(pid, name)

    def _on_tree_double_click(self, item: QTreeWidgetItem) -> None:
        pid = item.text(1)
        name = item.text(0)
        if pid:
            self._open_detail(pid, name)

    def _find_pid_in_table(self, row: int) -> str:
        headers = getattr(self, "_pslist_headers", [])
        for c, header in enumerate(headers):
            if header.strip().upper() in ("PID",):
                item = self._pslist_table.item(row, c)
                return item.text().strip() if item else ""
        return ""

    def _find_name_in_table(self, row: int) -> str:
        headers = getattr(self, "_pslist_headers", [])
        for c, header in enumerate(headers):
            if "name" in header.lower():
                item = self._pslist_table.item(row, c)
                return item.text().strip() if item else ""
        return ""

    def _open_detail(self, pid: str, name: str) -> None:
        window = ProcessDetailWindow(self._runner, self._plugins, pid, name)
        window.show()
        self._detail_windows.append(window)


class ProcessDetailWindow(QWidget):
    """Ventana con sub-pestañas de detalle para un PID concreto."""

    def __init__(
        self,
        runner: VolatilityRunner,
        plugins: Dict,
        pid: str,
        name: str,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent, Qt.Window)
        self._runner = runner
        self._plugins = plugins
        self._pid = pid
        self._workers: List[PluginWorker] = []
        self.setWindowTitle(f"Detalle de proceso - {name} (PID {pid})")
        self.resize(820, 560)
        self._build_ui(name)
        self._load_all()

    def _build_ui(self, name: str) -> None:
        layout = QVBoxLayout(self)
        header = QLabel(f"Proceso: {name}   |   PID: {self._pid}")
        header.setStyleSheet("font-size:14px;color:#4ec9b0;font-weight:bold;")
        layout.addWidget(header)

        self._tabs = QTabWidget()
        layout.addWidget(self._tabs, 1)

        self._editors: Dict[str, QTextEdit] = {}
        for label, _plugin in self._plugins["detail"]:
            editor = QTextEdit()
            editor.setReadOnly(True)
            editor.setLineWrapMode(QTextEdit.NoWrap)
            editor.setStyleSheet("font-family:monospace;")
            editor.setPlainText("Cargando...")
            self._tabs.addTab(editor, label)
            self._editors[label] = editor

    def _load_all(self) -> None:
        pid_flag = self._plugins.get("pid_flag", "-p")
        for label, plugin in self._plugins["detail"]:
            extra = [pid_flag, self._pid]
            audit_log.log_plugin(plugin, self._runner.command_string(plugin, extra))
            worker = self._runner.run_async(plugin, extra)
            worker.finished_ok.connect(self._make_handler(label))
            worker.failed.connect(self._make_fail_handler(label))
            self._workers.append(worker)

    def _make_handler(self, label: str):
        def handler(_plugin: str, output: str) -> None:
            self._editors[label].setPlainText(output or "(sin salida)")
        return handler

    def _make_fail_handler(self, label: str):
        def handler(_plugin: str, message: str) -> None:
            self._editors[label].setPlainText(f"Error: {message}")
        return handler
