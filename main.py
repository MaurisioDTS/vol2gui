#!/usr/bin/env python3
"""Punto de entrada del wrapper GUI de Volatility 2.6.

Flujo:
  1. Muestra un diálogo de arranque para elegir binario + imagen + perfil.
  2. Crea el ``VolatilityRunner`` y la ventana principal.
  3. La ventana principal genera el reporte automático y construye las
     pestañas según el SO detectado.
"""

from __future__ import annotations

import sys

from PyQt5.QtWidgets import QApplication, QMessageBox

from core.profiles import default_profiles_dir
from core.runner import VolatilityError, VolatilityRunner
from ui.image_loader import StartupDialog
from ui.main_window import MainWindow
from ui.theme import DARK_QSS
from utils import audit_log


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Volatility 2 GUI")
    app.setStyleSheet(DARK_QSS)

    audit_log.init_audit_log()

    dialog = StartupDialog()
    if not dialog.exec_():
        return 0

    try:
        runner = VolatilityRunner(
            binary_path=dialog.binary_path,
            image_path=dialog.image_path,
            profile=dialog.manual_profile or None,
            profiles_dir=default_profiles_dir(),
        )
    except VolatilityError as exc:
        QMessageBox.critical(None, "Error al iniciar", str(exc))
        return 1

    window = MainWindow(runner, manual_profile=dialog.manual_profile)
    window.show()
    return app.exec_()


if __name__ == "__main__":
    sys.exit(main())
