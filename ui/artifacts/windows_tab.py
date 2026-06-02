"""Artefactos forenses para imágenes Windows."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QWidget

from core.runner import VolatilityRunner
from ui.artifacts.base import ArtifactSpec, ArtifactTab

WINDOWS_ARTIFACTS: list[ArtifactSpec] = [
    ("Registro (hives)", "hivelist", [], "Lista de hives del registro cargados en memoria."),
    ("Servicios", "svcscan", [], "Servicios de Windows registrados (svcscan)."),
    ("Conexiones de red", "netscan", [], "Conexiones y sockets de red (netscan)."),
    ("Cmdline", "cmdline", [], "Argumentos de línea de comandos por proceso."),
    ("Historial CMD", "cmdscan", [], "Comandos escritos en consolas (cmdscan)."),
    ("Consolas", "consoles", [], "Contenido de buffers de consola (consoles)."),
    ("DLLs cargadas", "dlllist", [], "DLLs cargadas por cada proceso."),
    ("Módulos (ldrmodules)", "ldrmodules", [], "Compara módulos cargados vs ocultos (rootkits)."),
    ("Malfind (inyección)", "malfind", [], "Detección de código inyectado / shellcode en memoria."),
    ("Hashes (hashdump)", "hashdump", [], "Hashes NTLM de cuentas locales (SAM)."),
    ("Cached hashes", "cachedump", [], "Hashes de dominio cacheados."),
    ("Shimcache", "shimcache", [], "Artefactos de ejecución (Application Compatibility Cache)."),
    ("UserAssist", "userassist", [], "Programas ejecutados por el usuario (UserAssist)."),
    ("Amcache", "amcache", [], "Información de ejecución desde Amcache."),
    ("Portapapeles", "clipboard", [], "Contenido del portapapeles en memoria."),
    ("MFT (mftparser)", "mftparser", [], "Tabla maestra de ficheros (MFT) completa."),
    ("Callbacks", "callbacks", [], "Rutinas de notificación del sistema (posibles hooks)."),
    ("SSDT", "ssdt", [], "Tabla de descriptores de servicios del sistema (hooks SSDT)."),
    ("Drivers (modscan)", "modscan", [], "Módulos del kernel / drivers cargados."),
]


class WindowsArtifactsTab(ArtifactTab):
    """Pestaña de artefactos Windows."""

    def __init__(self, runner: VolatilityRunner, parent: Optional[QWidget] = None) -> None:
        super().__init__(runner, WINDOWS_ARTIFACTS, parent)
