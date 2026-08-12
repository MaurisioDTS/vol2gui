"""Detección de sistema operativo y perfil sugerido desde ``imageinfo``.

``imageinfo`` imprime una línea como::

    Suggested Profile(s) : Win7SP1x64, Win7SP0x64, Win2008R2SP0x64

A partir del nombre del perfil se infiere el SO. Para Linux y Mac, los perfiles
no se sugieren automáticamente (hay que instalarlos), por lo que también se
ofrece detección heurística a partir de cadenas presentes en la imagen.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

from core.i18n import t


class OSType(str, Enum):
    WINDOWS = "Windows"
    LINUX = "Linux"
    MAC = "Mac"
    UNKNOWN = "Desconocido"


# Clave i18n para cada SO; los nombres propios (Windows/Linux/Mac) son iguales
# en ambos idiomas, sólo cambia "Desconocido"/"Unknown".
_OS_I18N_KEY = {
    OSType.WINDOWS: "os.windows",
    OSType.LINUX: "os.linux",
    OSType.MAC: "os.mac",
    OSType.UNKNOWN: "os.unknown",
}


def os_label(os_type: "OSType") -> str:
    """Etiqueta del SO en el idioma activo (para mostrar en la interfaz)."""
    return t(_OS_I18N_KEY.get(os_type, "os.unknown"))


@dataclass
class ProfileInfo:
    """Resultado de la detección de perfil."""

    os_type: OSType = OSType.UNKNOWN
    suggested_profiles: List[str] = field(default_factory=list)
    selected_profile: Optional[str] = None
    raw_imageinfo: str = ""

    @property
    def has_profile(self) -> bool:
        return bool(self.selected_profile)


def _os_from_profile_name(name: str) -> OSType:
    lowered = name.lower()
    if lowered.startswith("win") or "vista" in lowered or "xp" in lowered:
        return OSType.WINDOWS
    if lowered.startswith("linux"):
        return OSType.LINUX
    if lowered.startswith("mac") or lowered.startswith("osx"):
        return OSType.MAC
    return OSType.UNKNOWN


def detect_from_imageinfo(output: str) -> ProfileInfo:
    """Parsea la salida de ``imageinfo`` y construye un ``ProfileInfo``."""
    info = ProfileInfo(raw_imageinfo=output)

    match = re.search(r"Suggested Profile\(s\)\s*:\s*(.+)", output)
    if match:
        # Los perfiles vienen separados por comas; cada uno puede llevar una
        # anotación entre paréntesis (instancia detectada) que se descarta.
        raw = match.group(1)
        profiles = []
        for chunk in raw.split(","):
            cleaned = re.sub(r"\(.*?\)", "", chunk).strip()
            if cleaned and cleaned.lower() != "no suggestion":
                profiles.append(cleaned)
        info.suggested_profiles = profiles
        if profiles:
            info.selected_profile = profiles[0]
            info.os_type = _os_from_profile_name(profiles[0])

    # Si imageinfo no sugirió nada útil, intenta inferir el SO por otras pistas.
    if info.os_type == OSType.UNKNOWN:
        info.os_type = _heuristic_os(output)

    return info


def _heuristic_os(text: str) -> OSType:
    lowered = text.lower()
    if "linux" in lowered:
        return OSType.LINUX
    if "mac" in lowered or "darwin" in lowered:
        return OSType.MAC
    if "windows" in lowered or "ntoskrnl" in lowered:
        return OSType.WINDOWS
    return OSType.UNKNOWN


# Plugins de detección de SO para imágenes Linux/Mac, que no aparecen en
# ``imageinfo`` (requieren perfil instalado). Útiles si el usuario ya conoce
# que la imagen es Linux/Mac.
LINUX_DETECT_PLUGINS = ["linux_pslist"]
MAC_DETECT_PLUGINS = ["mac_pslist"]


def profile_summary(info: ProfileInfo) -> str:
    """Resumen legible para mostrar en la UI o en el log."""
    lines = [t("profile.os_detected", os=os_label(info.os_type))]
    if info.suggested_profiles:
        lines.append(t("profile.suggested", profiles=", ".join(info.suggested_profiles)))
    if info.selected_profile:
        lines.append(t("profile.selected", profile=info.selected_profile))
    else:
        lines.append(t("profile.none_suggested"))
    return "\n".join(lines)
