"""Búsqueda de cadenas/patrones en memoria mediante yarascan.

Permite al analista introducir una cadena o patrón y lanzar ``yarascan``
(Windows) o ``linux_yarascan`` / ``mac_yarascan`` según el SO. El resultado se
muestra como salida cruda, ya que yarascan no produce una tabla homogénea.
"""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.i18n import t
from core.profile import OSType
from core.runner import PluginWorker, VolatilityRunner
from utils import audit_log

_YARA_PLUGIN = {
    OSType.WINDOWS: "yarascan",
    OSType.LINUX: "linux_yarascan",
    OSType.MAC: "mac_yarascan",
}


class SearchWidget(QWidget):
    """Búsqueda de patrones en memoria con yarascan."""

    def __init__(
        self,
        runner: VolatilityRunner,
        os_type: OSType,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._plugin = _YARA_PLUGIN.get(os_type, "yarascan")
        self._worker: Optional[PluginWorker] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        row = QHBoxLayout()
        row.addWidget(QLabel(t("search.label")))
        self._pattern = QLineEdit()
        self._pattern.setPlaceholderText(t("search.placeholder"))
        self._pattern.returnPressed.connect(self._search)
        row.addWidget(self._pattern, 1)

        self._mode = QComboBox()
        # El orden importa: 0=texto (-Y), 1=hex (-X), 2=regla YARA (-y).
        self._mode.addItems([t("search.mode_text"), t("search.mode_hex"), t("search.mode_yara")])
        row.addWidget(self._mode)

        self._search_btn = QPushButton(t("search.btn"))
        self._search_btn.clicked.connect(self._search)
        row.addWidget(self._search_btn)
        layout.addLayout(row)

        hint = QLabel(t("search.hint"))
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#888;font-size:11px;")
        layout.addWidget(hint)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setLineWrapMode(QTextEdit.NoWrap)
        self._output.setStyleSheet("font-family:monospace;")
        layout.addWidget(self._output, 1)

    def _build_args(self) -> Optional[list]:
        pattern = self._pattern.text().strip()
        if not pattern:
            QMessageBox.warning(self, t("search.empty_title"), t("search.empty_msg"))
            return None
        mode = self._mode.currentIndex()
        if mode == 0:  # texto literal
            return ["-Y", pattern]
        if mode == 1:  # bytes en hexadecimal
            return ["-X", pattern]
        return ["-y", pattern]  # fichero de reglas YARA

    def _search(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        args = self._build_args()
        if args is None:
            return
        self._search_btn.setEnabled(False)
        self._progress.show()
        self._output.setPlainText(t("search.searching"))
        audit_log.log_plugin(self._plugin, self._runner.command_string(self._plugin, args))
        self._worker = self._runner.run_async(self._plugin, args)
        self._worker.finished_ok.connect(self._on_finished)
        self._worker.failed.connect(self._on_failed)

    def _on_finished(self, _plugin: str, output: str) -> None:
        self._progress.hide()
        self._search_btn.setEnabled(True)
        self._output.setPlainText(output or t("search.no_matches"))

    def _on_failed(self, plugin: str, message: str) -> None:
        self._progress.hide()
        self._search_btn.setEnabled(True)
        self._output.setPlainText(t("search.error", plugin=plugin, message=message))
