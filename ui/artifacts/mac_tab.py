"""Artefactos forenses para imágenes macOS."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QWidget

from core.runner import VolatilityRunner
from ui.artifacts.base import ArtifactSpec, ArtifactTab

MAC_ARTIFACTS: list[ArtifactSpec] = [
    ("Historial bash", "mac_bash", [], "Historial de comandos bash en memoria."),
    ("Conexiones (netstat)", "mac_netstat", [], "Conexiones de red activas."),
    ("Interfaces (ifconfig)", "mac_ifconfig", [], "Configuración de interfaces de red."),
    ("Extensiones kernel", "mac_lsmod", [], "Extensiones del kernel cargadas (kext)."),
    ("Syscall hooks", "mac_check_syscall", [], "Detección de hooks en la tabla de syscalls."),
    ("TrustedBSD", "mac_trustedbsd", [], "Hooks de política de seguridad TrustedBSD (rootkits)."),
    ("Mapas dyld", "mac_dyld_maps", [], "Librerías dinámicas cargadas por proceso."),
    ("Ficheros abiertos", "mac_lsof", [], "Descriptores de fichero abiertos por proceso."),
    ("Variables de entorno", "mac_psenv", [], "Variables de entorno por proceso."),
    ("Lista de ficheros", "mac_list_files", [], "Ficheros referenciados en el caché de la imagen."),
    ("ARP", "mac_arp", [], "Tabla ARP."),
    ("Rutas de red", "mac_route", [], "Tabla de rutas de red."),
    ("Notifiers", "mac_notifiers", [], "Notification callbacks (posibles hooks)."),
]


class MacArtifactsTab(ArtifactTab):
    """Pestaña de artefactos macOS."""

    def __init__(self, runner: VolatilityRunner, parent: Optional[QWidget] = None) -> None:
        super().__init__(runner, MAC_ARTIFACTS, parent)
