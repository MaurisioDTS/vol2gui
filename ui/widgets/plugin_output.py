"""Widget genérico para ejecutar un plugin y mostrar su salida.

Combina:
  - Un botón para (re)ejecutar el plugin en segundo plano.
  - Una barra de filtro de texto en vivo.
  - Una tabla con los resultados parseados.
  - Un botón para ver la salida cruda.
  - Un botón para exportar (CSV/JSON/HTML).

Lo usan todas las pestañas de artefactos para no duplicar lógica.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QFileDialog,
    QHBoxLayout,
    QHeaderView,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.parser import parse_table
from core.runner import PluginWorker, VolatilityRunner
from utils import audit_log, export


class PluginOutputWidget(QWidget):
    """Ejecuta un plugin de Volatility y muestra su salida en una tabla."""

    def __init__(
        self,
        runner: VolatilityRunner,
        plugin: str,
        extra_args: Optional[List[str]] = None,
        description: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._plugin = plugin
        self._extra_args = extra_args or []
        self._worker: Optional[PluginWorker] = None
        self._raw_output = ""
        self._headers: List[str] = []
        self._rows: List[List[str]] = []
        self._has_run = False

        self._build_ui(description)

    # ------------------------------------------------------------------ UI --
    def _build_ui(self, description: str) -> None:
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self._run_btn = QPushButton(f"Ejecutar  {self._plugin}")
        self._run_btn.clicked.connect(self.run_plugin)
        top.addWidget(self._run_btn)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filtrar resultados...")
        self._filter.textChanged.connect(self._apply_filter)
        top.addWidget(self._filter, 1)

        self._raw_btn = QPushButton("Ver raw")
        self._raw_btn.clicked.connect(self._show_raw)
        self._raw_btn.setEnabled(False)
        top.addWidget(self._raw_btn)

        self._export_btn = QPushButton("Exportar")
        self._export_btn.clicked.connect(self._export)
        self._export_btn.setEnabled(False)
        top.addWidget(self._export_btn)

        layout.addLayout(top)

        if description:
            desc = QLabel(description)
            desc.setWordWrap(True)
            desc.setStyleSheet("color:#888;font-size:11px;")
            layout.addWidget(desc)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)  # modo indeterminado
        self._progress.hide()
        layout.addWidget(self._progress)

        self._status = QLabel("Pulsa «Ejecutar» para lanzar el plugin.")
        self._status.setStyleSheet("color:#4ec9b0;")
        layout.addWidget(self._status)

        self._table = QTableWidget()
        self._table.setSortingEnabled(True)
        self._table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self._table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self._table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive)
        layout.addWidget(self._table, 1)

    # ------------------------------------------------------------- ejecución --
    def run_plugin(self, force: bool = True) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._has_run = True
        self._run_btn.setEnabled(False)
        self._progress.show()
        self._status.setText(f"Ejecutando {self._plugin}...")

        audit_log.log_plugin(
            self._plugin, self._runner.command_string(self._plugin, self._extra_args)
        )

        self._worker = self._runner.run_async(self._plugin, self._extra_args)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)

    def run_if_needed(self) -> None:
        """Lanza el plugin sólo la primera vez (carga perezosa de pestañas)."""
        if not self._has_run:
            self.run_plugin()

    def _on_finished(self, plugin: str, output: str) -> None:
        self._raw_output = output
        self._headers, self._rows = parse_table(output)
        self._populate_table()
        self._progress.hide()
        self._run_btn.setEnabled(True)
        self._raw_btn.setEnabled(True)
        self._export_btn.setEnabled(bool(self._rows))
        n = len(self._rows)
        self._status.setText(f"{plugin}: {n} fila(s).")
        if n == 0 and output.strip():
            self._status.setText(f"{plugin}: sin resultados tabulares (usa «Ver raw»).")

    def _on_failed(self, plugin: str, message: str) -> None:
        self._progress.hide()
        self._run_btn.setEnabled(True)
        self._status.setText(f"Error en {plugin}.")
        QMessageBox.warning(self, f"Error en {plugin}", message)

    # ---------------------------------------------------------------- tabla --
    def _populate_table(self) -> None:
        self._table.setSortingEnabled(False)
        headers = self._headers if self._headers else ["Salida"]
        self._table.setColumnCount(len(headers))
        self._table.setHorizontalHeaderLabels(headers)
        self._table.setRowCount(len(self._rows))
        for r, row in enumerate(self._rows):
            for c in range(len(headers)):
                value = row[c] if c < len(row) else ""
                self._table.setItem(r, c, QTableWidgetItem(value))
        self._table.resizeColumnsToContents()
        self._table.setSortingEnabled(True)

    def _apply_filter(self, text: str) -> None:
        text = text.lower().strip()
        for r in range(self._table.rowCount()):
            visible = not text
            if not visible:
                for c in range(self._table.columnCount()):
                    item = self._table.item(r, c)
                    if item and text in item.text().lower():
                        visible = True
                        break
            self._table.setRowHidden(r, not visible)

    # ----------------------------------------------------------- auxiliares --
    def _show_raw(self) -> None:
        dlg = _RawDialog(self._plugin, self._raw_output, self)
        dlg.exec_()

    def _export(self) -> None:
        if not self._rows:
            return
        path, selected = QFileDialog.getSaveFileName(
            self, "Exportar resultados", f"{self._plugin}.csv", export.file_filter()
        )
        if not path:
            return
        headers = self._headers if self._headers else ["Salida"]
        try:
            if path.endswith(".json") or "JSON" in selected:
                export.export_json(path, headers, self._rows)
                fmt = "json"
            elif path.endswith(".html") or "HTML" in selected:
                export.export_html(path, headers, self._rows, title=self._plugin)
                fmt = "html"
            else:
                export.export_csv(path, headers, self._rows)
                fmt = "csv"
            audit_log.log_export(fmt, path, len(self._rows))
            self._status.setText(f"Exportado a {path}")
        except OSError as exc:
            QMessageBox.warning(self, "Error al exportar", str(exc))


class _RawDialog(QWidget):
    """Ventana flotante con la salida cruda del plugin."""

    def __init__(self, plugin: str, raw: str, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent, Qt.Window)
        self.setWindowTitle(f"Salida cruda - {plugin}")
        self.resize(800, 600)
        layout = QVBoxLayout(self)
        editor = QTextEdit()
        editor.setReadOnly(True)
        editor.setLineWrapMode(QTextEdit.NoWrap)
        editor.setPlainText(raw)
        editor.setStyleSheet("font-family:monospace;")
        layout.addWidget(editor)

    def exec_(self) -> None:
        self.show()
