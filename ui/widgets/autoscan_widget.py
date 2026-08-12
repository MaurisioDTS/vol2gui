"""Auto-scan de malware: ejecuta en lote los plugins de detecci?n.

Lanza secuencialmente un conjunto de plugins orientados a detecci?n de malware
y rootkits seg?n el SO, acumula la salida y permite guardar un informe HTML
consolidado para la investigaci?n.
"""

from __future__ import annotations

import html
from datetime import datetime
from typing import List, Optional, Tuple

from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core import i18n
from core.i18n import t
from core.profile import OSType
from core.runner import PluginWorker, VolatilityRunner
from utils import audit_log

# Plugins de detecci?n por SO: (clave_i18n_etiqueta, plugin). Se guardan claves
# i18n (no texto) porque el diccionario se eval?a al importar el m?dulo.
_SCAN_PLUGINS = {
    OSType.WINDOWS: [
        ("autoscan.win.malfind", "malfind"),
        ("autoscan.win.ldrmodules", "ldrmodules"),
        ("autoscan.win.apihooks", "apihooks"),
        ("autoscan.win.ssdt", "ssdt"),
        ("autoscan.win.callbacks", "callbacks"),
        ("autoscan.win.psxview", "psxview"),
    ],
    OSType.LINUX: [
        ("autoscan.linux.syscall", "linux_check_syscall"),
        ("autoscan.linux.hidden_modules", "linux_hidden_modules"),
        ("autoscan.linux.creds", "linux_check_creds"),
        ("autoscan.linux.fop", "linux_check_fop"),
        ("autoscan.linux.tty", "linux_check_tty"),
    ],
    OSType.MAC: [
        ("autoscan.mac.syscall", "mac_check_syscall"),
        ("autoscan.mac.trustedbsd", "mac_trustedbsd"),
        ("autoscan.mac.sysctl", "mac_check_sysctl"),
        ("autoscan.mac.trap_table", "mac_check_trap_table"),
        ("autoscan.mac.notifiers", "mac_notifiers"),
    ],
}


class AutoScanWidget(QWidget):
    """Ejecuta en serie los plugins de detecci?n de malware."""

    def __init__(
        self,
        runner: VolatilityRunner,
        os_type: OSType,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._plugins: List[Tuple[str, str]] = _SCAN_PLUGINS.get(os_type, [])
        self._results: List[Tuple[str, str, str]] = []  # (etiqueta, plugin, salida)
        self._queue: List[Tuple[str, str]] = []
        self._worker: Optional[PluginWorker] = None
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel(t("autoscan.title"))
        title.setStyleSheet("font-size:15px;color:#f48771;font-weight:bold;")
        layout.addWidget(title)

        desc = QLabel(t("autoscan.desc"))
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#888;font-size:11px;")
        layout.addWidget(desc)

        row = QHBoxLayout()
        self._scan_btn = QPushButton(t("autoscan.start_btn"))
        self._scan_btn.clicked.connect(self.start_scan)
        row.addWidget(self._scan_btn)
        self._report_btn = QPushButton(t("autoscan.save_report_btn"))
        self._report_btn.clicked.connect(self._save_report)
        self._report_btn.setEnabled(False)
        row.addWidget(self._report_btn)
        row.addStretch(1)
        layout.addLayout(row)

        self._progress = QProgressBar()
        self._progress.hide()
        layout.addWidget(self._progress)

        self._status = QLabel("")
        self._status.setStyleSheet("color:#4ec9b0;")
        layout.addWidget(self._status)

        self._output = QTextEdit()
        self._output.setReadOnly(True)
        self._output.setLineWrapMode(QTextEdit.NoWrap)
        self._output.setStyleSheet("font-family:monospace;")
        layout.addWidget(self._output, 1)

    def start_scan(self) -> None:
        if not self._plugins:
            QMessageBox.information(self, t("autoscan.no_plugins_title"), t("autoscan.no_plugins_msg"))
            return
        if self._worker is not None and self._worker.isRunning():
            return
        self._results.clear()
        self._output.clear()
        self._queue = list(self._plugins)
        self._scan_btn.setEnabled(False)
        self._report_btn.setEnabled(False)
        self._progress.show()
        self._progress.setRange(0, len(self._queue))
        self._progress.setValue(0)
        audit_log.log_action("AUTO-SCAN iniciado")
        self._run_next()

    def _run_next(self) -> None:
        if not self._queue:
            self._finish()
            return
        label_key, plugin = self._queue[0]
        label = t(label_key)
        self._status.setText(t("autoscan.running", plugin=plugin, label=label))
        audit_log.log_plugin(plugin, self._runner.command_string(plugin))
        self._worker = self._runner.run_async(plugin)
        self._worker.finished_ok.connect(self._on_result)
        self._worker.failed.connect(self._on_result_failed)

    def _on_result(self, plugin: str, output: str) -> None:
        label_key, _ = self._queue.pop(0)
        label = t(label_key)
        self._results.append((label, plugin, output))
        self._append_section(label, plugin, output)
        self._progress.setValue(self._progress.value() + 1)
        self._run_next()

    def _on_result_failed(self, plugin: str, message: str) -> None:
        label_key, _ = self._queue.pop(0)
        label = t(label_key)
        self._results.append((label, plugin, f"[ERROR] {message}"))
        self._append_section(label, plugin, f"[ERROR] {message}")
        self._progress.setValue(self._progress.value() + 1)
        self._run_next()

    def _append_section(self, label: str, plugin: str, output: str) -> None:
        self._output.append(f"\n{'=' * 70}")
        self._output.append(f"## {label}  ({plugin})")
        self._output.append("=" * 70)
        self._output.append(output.strip() or t("common.no_results"))

    def _finish(self) -> None:
        self._progress.hide()
        self._scan_btn.setEnabled(True)
        self._report_btn.setEnabled(True)
        self._status.setText(t("autoscan.completed"))
        audit_log.log_action("AUTO-SCAN completado")

    def _save_report(self) -> None:
        if not self._results:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, t("autoscan.save_report_title"), "autoscan_report.html", "HTML (*.html)"
        )
        if not path:
            return
        try:
            self._write_html(path)
            audit_log.log_export("html", path, len(self._results))
            self._status.setText(t("autoscan.report_saved", path=path))
        except OSError as exc:
            QMessageBox.warning(self, t("common.error"), str(exc))

    def _write_html(self, path: str) -> None:
        lang = i18n.get_language()
        parts = [
            f"<!DOCTYPE html><html lang='{lang}'><head><meta charset='utf-8'>",
            f"<title>{html.escape(t('autoscan.report_html_title'))}</title><style>",
            "body{font-family:Segoe UI,Arial,sans-serif;background:#1e1e1e;color:#ddd;margin:24px;}",
            "h1{color:#f48771;} h2{color:#4ec9b0;border-bottom:1px solid #3c3c3c;padding-top:16px;}",
            "pre{background:#252526;padding:12px;overflow:auto;border:1px solid #3c3c3c;font-size:12px;}",
            ".meta{color:#888;font-size:12px;}",
            "</style></head><body>",
            f"<h1>{html.escape(t('autoscan.report_html_heading'))}</h1>",
            f"<div class='meta'>{html.escape(t('autoscan.report_image'))}: {html.escape(self._runner.image_path or '')}<br>",
            f"{html.escape(t('autoscan.report_profile'))}: {html.escape(self._runner.profile or '')}<br>",
            f"{html.escape(t('autoscan.report_generated'))}: {datetime.now().isoformat(timespec='seconds')}</div>",
        ]
        for label, plugin, output in self._results:
            parts.append(f"<h2>{html.escape(label)} ({html.escape(plugin)})</h2>")
            parts.append(f"<pre>{html.escape(output.strip() or t('common.no_results'))}</pre>")
        parts.append("</body></html>")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(parts))
