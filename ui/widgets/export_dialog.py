"""Diálogo de exportación reutilizable para tablas de resultados.

Permite elegir formato (CSV/JSON/HTML) y destino. La extracción de ficheros
de la imagen usa diálogos nativos directamente; este diálogo es para exportar
resultados de análisis (tablas) a disco.
"""

from __future__ import annotations

from typing import List, Optional

from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from core.i18n import t
from utils import audit_log, export


class ExportDialog(QDialog):
    """Diálogo para exportar una tabla a CSV/JSON/HTML."""

    _FORMATS = {
        "CSV (*.csv)": ("csv", export.export_csv),
        "JSON (*.json)": ("json", export.export_json),
        "HTML (*.html)": ("html", export.export_html),
    }

    def __init__(
        self,
        headers: List[str],
        rows: List[List[str]],
        default_name: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._headers = headers
        self._rows = rows
        self._default_name = default_name or t("export.default_name")
        self.setWindowTitle(t("plugin.export_title"))
        self.resize(480, 160)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        fmt_row = QHBoxLayout()
        fmt_row.addWidget(QLabel(t("export.format_label")))
        self._fmt = QComboBox()
        self._fmt.addItems(list(self._FORMATS.keys()))
        self._fmt.currentTextChanged.connect(self._sync_extension)
        fmt_row.addWidget(self._fmt, 1)
        layout.addLayout(fmt_row)

        path_row = QHBoxLayout()
        path_row.addWidget(QLabel(t("export.dest_label")))
        self._path = QLineEdit(f"{self._default_name}.csv")
        path_row.addWidget(self._path, 1)
        browse = QPushButton(t("common.browse"))
        browse.clicked.connect(self._browse)
        path_row.addWidget(browse)
        layout.addLayout(path_row)

        info = QLabel(t("export.rows_to_export", count=len(self._rows)))
        info.setStyleSheet("color:#888;")
        layout.addWidget(info)

        buttons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._do_export)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _sync_extension(self, fmt_label: str) -> None:
        ext = self._FORMATS[fmt_label][0]
        current = self._path.text().rsplit(".", 1)[0] or self._default_name
        self._path.setText(f"{current}.{ext}")

    def _browse(self) -> None:
        path, _ = QFileDialog.getSaveFileName(
            self, t("export.save_as"), self._path.text(), export.file_filter()
        )
        if path:
            self._path.setText(path)

    def _do_export(self) -> None:
        path = self._path.text().strip()
        if not path:
            QMessageBox.warning(self, t("export.empty_dest_title"), t("export.empty_dest_msg"))
            return
        fmt_label = self._fmt.currentText()
        fmt_name, func = self._FORMATS[fmt_label]
        try:
            if fmt_name == "html":
                func(path, self._headers, self._rows, self._default_name)
            else:
                func(path, self._headers, self._rows)
            audit_log.log_export(fmt_name, path, len(self._rows))
        except OSError as exc:
            QMessageBox.warning(self, t("plugin.export_error"), str(exc))
            return
        self.accept()
