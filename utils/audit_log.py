"""Registro de auditoría forense.

Toda acción relevante (carga de imagen, ejecución de plugin, extracción de
fichero, exportación) se registra con marca de tiempo en un fichero de log
junto a la aplicación. Esto aporta trazabilidad a la cadena de custodia.
"""

from __future__ import annotations

import logging
import os
from datetime import datetime
from typing import Optional

_LOGGER_NAME = "vol2gui.audit"
_DEFAULT_LOG = os.path.join(os.getcwd(), "audit.log")

_logger: Optional[logging.Logger] = None


def init_audit_log(log_path: str = _DEFAULT_LOG) -> logging.Logger:
    """Inicializa (una vez) el logger de auditoría."""
    global _logger
    if _logger is not None:
        return _logger

    logger = logging.getLogger(_LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    if not logger.handlers:
        handler = logging.FileHandler(log_path, encoding="utf-8")
        formatter = logging.Formatter("%(asctime)s | %(message)s")
        handler.setFormatter(formatter)
        logger.addHandler(handler)

    _logger = logger
    logger.info("=== Sesión iniciada: %s ===", datetime.now().isoformat(timespec="seconds"))
    return logger


def _get_logger() -> logging.Logger:
    if _logger is None:
        return init_audit_log()
    return _logger


def log_action(message: str) -> None:
    """Registra una acción genérica."""
    _get_logger().info(message)


def log_image_loaded(image_path: str, md5: str = "", sha256: str = "") -> None:
    msg = f"IMAGEN CARGADA: {image_path}"
    if md5:
        msg += f" | MD5={md5}"
    if sha256:
        msg += f" | SHA256={sha256}"
    log_action(msg)


def log_plugin(plugin: str, command: str) -> None:
    log_action(f"PLUGIN: {plugin} | CMD: {command}")


def log_extraction(plugin: str, destination: str, target: str = "") -> None:
    msg = f"EXTRACCIÓN: plugin={plugin} -> {destination}"
    if target:
        msg += f" | objetivo={target}"
    log_action(msg)


def log_export(fmt: str, destination: str, rows: int = 0) -> None:
    log_action(f"EXPORTACIÓN: formato={fmt} filas={rows} -> {destination}")
