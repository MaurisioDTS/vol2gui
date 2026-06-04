"""Gestión de perfiles personalizados de Volatility 2.

En Volatility 2 los perfiles que no vienen de serie (sobre todo Linux y macOS)
se distribuyen como archivos ``.zip``. El binario los reconoce cuando se le
indica la carpeta que los contiene con la opción ``--plugins=<carpeta>``; a
partir de ahí aparecen en ``--info`` y pueden usarse con ``--profile=<nombre>``.

Este módulo localiza la carpeta ``profiles/`` del proyecto, lista los archivos
de perfil que el analista haya guardado en ella y extrae los nombres de perfil
reales de la salida de ``--info`` para ofrecerlos como recursos en la interfaz.
"""

from __future__ import annotations

import os
import re
from typing import List

#: Nombre de la carpeta donde el usuario guarda sus perfiles de Volatility 2.
PROFILES_DIRNAME = "profiles"


def default_profiles_dir() -> str:
    """Devuelve la ruta de la carpeta ``profiles/`` junto al proyecto."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(here, PROFILES_DIRNAME)


def list_profile_archives(profiles_dir: str) -> List[str]:
    """Lista las rutas de los archivos ``.zip`` de perfil en ``profiles_dir``."""
    if not profiles_dir or not os.path.isdir(profiles_dir):
        return []
    return sorted(
        os.path.join(profiles_dir, name)
        for name in os.listdir(profiles_dir)
        if name.lower().endswith(".zip")
    )


def has_profiles(profiles_dir: str) -> bool:
    """Indica si hay al menos un archivo de perfil en la carpeta."""
    return bool(list_profile_archives(profiles_dir))


# Cabecera de la sección de perfiles en la salida de ``volatility --info``.
_PROFILES_HEADER = re.compile(r"^Profiles?\s*$", re.IGNORECASE)
# Una entrada de perfil: ``Nombre   - Descripción``.
_PROFILE_ENTRY = re.compile(r"^(\w[\w.\-]*)\s+-\s+")


def parse_info_profiles(output: str) -> List[str]:
    """Extrae los nombres de perfil de la salida de ``volatility --info``.

    Sólo se devuelven los perfiles de Linux y macOS, que son los que el analista
    aporta a través de la carpeta ``profiles/`` (el binario no trae ninguno de
    serie). Así se evita inundar la lista con los cientos de perfiles de Windows
    incorporados.
    """
    profiles: List[str] = []
    in_section = False
    for line in output.splitlines():
        if _PROFILES_HEADER.match(line.strip()):
            in_section = True
            continue
        if not in_section:
            continue
        stripped = line.strip()
        # Una línea en blanco o una nueva cabecera (texto seguido de ``---``)
        # marca el final de la sección de perfiles.
        if not stripped or set(stripped) == {"-"}:
            continue
        match = _PROFILE_ENTRY.match(stripped)
        if not match:
            # Probablemente hemos salido de la sección de perfiles.
            break
        name = match.group(1)
        if name.lower().startswith(("linux", "mac")):
            profiles.append(name)
    return sorted(set(profiles))
