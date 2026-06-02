"""Artefactos forenses para imágenes Linux."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QWidget

from core.runner import VolatilityRunner
from ui.artifacts.base import ArtifactSpec, ArtifactTab

LINUX_ARTIFACTS: list[ArtifactSpec] = [
    ("Historial bash", "linux_bash", [], "Historial de comandos bash recuperado de memoria."),
    ("Procesos (psaux)", "linux_psaux", [], "Procesos con su línea de comandos completa."),
    ("Conexiones (netstat)", "linux_netstat", [], "Conexiones de red activas."),
    ("Interfaces (ifconfig)", "linux_ifconfig", [], "Configuración de interfaces de red."),
    ("Módulos kernel (lsmod)", "linux_lsmod", [], "Módulos del kernel cargados."),
    ("Syscall hooks", "linux_check_syscall", [], "Detección de hooks en la tabla de syscalls (rootkits)."),
    ("Creds sospechosas", "linux_check_creds", [], "Procesos que comparten credenciales (posible escalada)."),
    ("Puntos de montaje", "linux_mount", [], "Sistemas de ficheros montados."),
    ("dmesg", "linux_dmesg", [], "Buffer de mensajes del kernel (dmesg)."),
    ("Ficheros abiertos", "linux_lsof", [], "Descriptores de fichero abiertos por proceso."),
    ("Librerías (proc_maps)", "linux_proc_maps", [], "Regiones de memoria mapeadas por proceso."),
    ("Módulos ocultos", "linux_hidden_modules", [], "Módulos del kernel ocultos (rootkits)."),
    ("ARP / Route", "linux_route_cache", [], "Caché de rutas de red."),
    ("Variables de entorno", "linux_psenv", [], "Variables de entorno por proceso."),
]


class LinuxArtifactsTab(ArtifactTab):
    """Pestaña de artefactos Linux."""

    def __init__(self, runner: VolatilityRunner, parent: Optional[QWidget] = None) -> None:
        super().__init__(runner, LINUX_ARTIFACTS, parent)
