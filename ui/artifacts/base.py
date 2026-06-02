"""Base común para las pestañas de artefactos.

Cada artefacto es una sub-pestaña que envuelve un ``PluginOutputWidget``. Las
sub-pestañas se ejecutan de forma perezosa: el plugin sólo se lanza la primera
vez que el usuario abre esa sub-pestaña, evitando saturar la imagen con
ejecuciones simultáneas.
"""

from __future__ import annotations

from typing import List, Optional, Tuple

from PyQt5.QtWidgets import QTabWidget, QWidget

from core.runner import VolatilityRunner
from ui.widgets.plugin_output import PluginOutputWidget

# (etiqueta, plugin, extra_args, descripción)
ArtifactSpec = Tuple[str, str, List[str], str]


class ArtifactTab(QWidget):
    """Contenedor de sub-pestañas de artefactos con carga perezosa."""

    def __init__(
        self,
        runner: VolatilityRunner,
        specs: List[ArtifactSpec],
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._widgets: List[PluginOutputWidget] = []

        from PyQt5.QtWidgets import QVBoxLayout

        layout = QVBoxLayout(self)
        self._tabs = QTabWidget()
        self._tabs.currentChanged.connect(self._on_tab_changed)
        layout.addWidget(self._tabs)

        for label, plugin, extra_args, description in specs:
            widget = PluginOutputWidget(self._runner, plugin, extra_args, description)
            self._widgets.append(widget)
            self._tabs.addTab(widget, label)

    def _on_tab_changed(self, index: int) -> None:
        if 0 <= index < len(self._widgets):
            self._widgets[index].run_if_needed()
