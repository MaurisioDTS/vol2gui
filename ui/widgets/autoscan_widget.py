"""Auto-scan de malware: ejecuta en lote los plugins de detección.

Lanza secuencialmente un conjunto de plugins orientados a detección de malware
y rootkits según el SO, acumula la salida y permite guardar un informe HTML
consolidado para la investigación.
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

from core.profile import OSType
from core.runner import PluginWorker, VolatilityRunner
from utils import audit_log

# Plugins de detección por SO: (etiqueta, plugin).
_SCAN_PLUGINS = {
    OSType.WINDOWS: [
        ("Inyección de código (malfind)", "malfind"),
        ("Módulos ocultos (ldrmodules)", "ldrmodules"),
        ("API hooks (apihooks)", "apihooks"),
        ("Hooks SSDT (ssdt)", "ssdt"),
        ("Callbacks del sistema", "callbacks"),
        ("Procesos ocultos (psxview)", "psxview"),
    ],
    OSType.LINUX: [
        ("Hooks de syscalls", "linux_check_syscall"),
        ("Módulos ocultos", "linux_hidden_modules"),
        ("Credenciales sospechosas", "linux_check_creds"),
        ("Hooks de fops", "linux_check_fop"),
        ("TTY hooks", "linux_check_tty"),
    ],
    OSType.MAC: [
        ("Hooks de syscalls", "mac_check_syscall"),
        ("TrustedBSD", "mac_trustedbsd"),
        ("Hooks de sysctl", "mac_check_sysctl"),
        ("Trap table", "mac_check_trap_table"),
        ("Notifiers", "mac_notifiers"),
    ],
}


class AutoScanWidget(QWidget):
    """Ejecuta en serie los plugins de detección de malware."""

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

        title = QLabel("Auto-scan de malware y rootkits")
        title.setStyleSheet("font-size:15px;color:#f48771;font-weight:bold;")
        layout.addWidget(title)

        desc = QLabel(
            "Ejecuta en lote los plugins de detección de inyección de código, "
            "hooks y artefactos ocultos. Al terminar puedes guardar un informe HTML."
        )
        desc.setWordWrap(True)
        desc.setStyleSheet("color:#888;font-size:11px;")
        layout.addWidget(desc)

        row = QHBoxLayout()
        self._scan_btn = QPushButton("Iniciar auto-scan")
        self._scan_btn.clicked.connect(self.start_scan)
        row.addWidget(self._scan_btn)
        self._report_btn = QPushButton("Guardar informe HTML")
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
            QMessageBox.information(self, "Sin plugins", "No hay plugins de scan para este SO.")
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
        label, plugin = self._queue[0]
        self._status.setText(f"Ejecutando {plugin} ({label})...")
        audit_log.log_plugin(plugin, self._runner.command_string(plugin))
        self._worker = self._runner.run_async(plugin)
        self._worker.finished_ok.connect(self._on_result)
        self._worker.failed.connect(self._on_result_failed)

    def _on_result(self, plugin: str, output: str) -> None:
        label, _ = self._queue.pop(0)
        self._results.append((label, plugin, output))
        self._append_section(label, plugin, output)
        self._progress.setValue(self._progress.value() + 1)
        self._run_next()

    def _on_result_failed(self, plugin: str, message: str) -> None:
        label, _ = self._queue.pop(0)
        self._results.append((label, plugin, f"[ERROR] {message}"))
        self._append_section(label, plugin, f"[ERROR] {message}")
        self._progress.setValue(self._progress.value() + 1)
        self._run_next()

    def _append_section(self, label: str, plugin: str, output: str) -> None:
        self._output.append(f"\n{'=' * 70}")
        self._output.append(f"## {label}  ({plugin})")
        self._output.append("=" * 70)
        self._output.append(output.strip() or "(sin resultados)")

    def _finish(self) -> None:
        self._progress.hide()
        self._scan_btn.setEnabled(True)
        self._report_btn.setEnabled(True)
        self._status.setText("Auto-scan completado.")
        audit_log.log_action("AUTO-SCAN completado")

    def _save_report(self) -> None:
        if not self._results:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar informe de auto-scan", "autoscan_report.html", "HTML (*.html)"
        )
        if not path:
            return
        try:
            self._write_html(path)
            audit_log.log_export("html", path, len(self._results))
            self._status.setText(f"Informe guardado: {path}")
        except OSError as exc:
            QMessageBox.warning(self, "Error", str(exc))

    def _write_html(self, path: str) -> None:
        parts = [
            "<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>",
            "<title>Informe de auto-scan</title><style>",
            "body{font-family:Segoe UI,Arial,sans-serif;background:#1e1e1e;color:#ddd;margin:24px;}",
            "h1{color:#f48771;} h2{color:#4ec9b0;border-bottom:1px solid #3c3c3c;padding-top:16px;}",
            "pre{background:#252526;padding:12px;overflow:auto;border:1px solid #3c3c3c;font-size:12px;}",
            ".meta{color:#888;font-size:12px;}",
            "</style></head><body>",
            "<h1>Informe de auto-scan de malware</h1>",
            f"<div class='meta'>Imagen: {html.escape(self._runner.image_path or '')}<br>",
            f"Perfil: {html.escape(self._runner.profile or '')}<br>",
            f"Generado: {datetime.now().isoformat(timespec='seconds')}</div>",
        ]
        for label, plugin, output in self._results:
            parts.append(f"<h2>{html.escape(label)} ({html.escape(plugin)})</h2>")
            parts.append(f"<pre>{html.escape(output.strip() or '(sin resultados)')}</pre>")
        parts.append("</body></html>")
        with open(path, "w", encoding="utf-8") as fh:
            fh.write("\n".join(parts))
