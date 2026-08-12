"""Ventana principal del wrapper de Volatility 2.

Orquesta el flujo completo:
  1. Muestra el reporte automático de la imagen (hashes + imageinfo).
  2. Al detectarse el SO/perfil, construye dinámicamente las pestañas:
     procesos, sistema de ficheros, artefactos del SO, búsqueda y auto-scan.
"""

from __future__ import annotations

import os
from typing import Optional

from PyQt5.QtWidgets import (
    QLabel,
    QMainWindow,
    QMessageBox,
    QTabWidget,
    QWidget,
)

from core.i18n import t
from core.profile import OSType, ProfileInfo, os_label
from core.runner import VolatilityRunner
from ui.artifacts.linux_tab import LinuxArtifactsTab
from ui.artifacts.mac_tab import MacArtifactsTab
from ui.artifacts.windows_tab import WindowsArtifactsTab
from ui.filesystem_view import FilesystemView
from ui.image_loader import ImageReportWidget
from ui.process_view import ProcessView
from ui.theme import DARK_QSS
from ui.widgets.autoscan_widget import AutoScanWidget
from ui.widgets.search_widget import SearchWidget
from utils import audit_log


class MainWindow(QMainWindow):
    """Ventana principal de la aplicación."""

    def __init__(
        self,
        runner: VolatilityRunner,
        manual_profile: str = "",
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        if manual_profile:
            self._runner.profile = manual_profile
        self._os_tabs_built = False

        self.setWindowTitle(t("main.window_title"))
        self.resize(1200, 760)
        self.setStyleSheet(DARK_QSS)

        self._tabs = QTabWidget()
        self.setCentralWidget(self._tabs)

        self.statusBar().showMessage(
            t(
                "main.status",
                image=os.path.basename(runner.image_path or ""),
                binary=os.path.basename(runner.binary_path),
            )
        )

        # Pestaña de reporte (siempre la primera).
        self._report = ImageReportWidget(self._runner)
        self._report.profile_detected.connect(self._on_profile_detected)
        self._tabs.addTab(self._report, t("main.tab_report"))

        self._report.start()

        # Si el usuario fijó un perfil manual, no esperamos a imageinfo para
        # construir las pestañas: inferimos el SO del nombre del perfil.
        if manual_profile:
            info = ProfileInfo(selected_profile=manual_profile)
            from core.profile import _os_from_profile_name

            info.os_type = _os_from_profile_name(manual_profile)
            if info.os_type != OSType.UNKNOWN:
                self._build_os_tabs(info)

    # ----------------------------------------------------- construcción de UI --
    def _on_profile_detected(self, info: ProfileInfo) -> None:
        if self._os_tabs_built:
            return
        if info.os_type == OSType.UNKNOWN:
            self.statusBar().showMessage(t("main.os_not_detected"))
            return
        self._build_os_tabs(info)

    def _build_os_tabs(self, info: ProfileInfo) -> None:
        if self._os_tabs_built:
            return
        self._os_tabs_built = True
        os_type = info.os_type
        audit_log.log_action(
            f"SO detectado: {os_type.value} | perfil: {self._runner.profile or '(ninguno)'}"
        )

        # Procesos.
        self._process_view = ProcessView(self._runner, os_type)
        self._tabs.addTab(self._process_view, t("main.tab_processes"))

        # Sistema de ficheros.
        self._fs_view = FilesystemView(self._runner, os_type)
        self._tabs.addTab(self._fs_view, t("main.tab_filesystem"))

        # Artefactos según SO.
        if os_type == OSType.WINDOWS:
            artifacts = WindowsArtifactsTab(self._runner)
        elif os_type == OSType.LINUX:
            artifacts = LinuxArtifactsTab(self._runner)
        else:
            artifacts = MacArtifactsTab(self._runner)
        self._tabs.addTab(artifacts, t("main.tab_artifacts", os=os_label(os_type)))

        # Búsqueda de cadenas.
        self._search = SearchWidget(self._runner, os_type)
        self._tabs.addTab(self._search, t("main.tab_search"))

        # Auto-scan de malware.
        self._autoscan = AutoScanWidget(self._runner, os_type)
        self._tabs.addTab(self._autoscan, t("main.tab_autoscan"))

        # Carga perezosa al cambiar de pestaña.
        self._tabs.currentChanged.connect(self._on_tab_changed)

        self.statusBar().showMessage(
            t(
                "main.status_full",
                os=os_label(os_type),
                profile=self._runner.profile or t("main.no_profile"),
                image=os.path.basename(self._runner.image_path or ""),
            )
        )

    def _on_tab_changed(self, index: int) -> None:
        widget = self._tabs.widget(index)
        if widget is getattr(self, "_process_view", None):
            self._process_view.load_if_needed()
        elif widget is getattr(self, "_fs_view", None):
            self._fs_view.load_if_needed()

    def closeEvent(self, event) -> None:  # noqa: N802 - override Qt
        audit_log.log_action("=== Sesión finalizada ===")
        super().closeEvent(event)
