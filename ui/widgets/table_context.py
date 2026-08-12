"""Menú contextual de copia en celdas de ``QTableWidget``."""

from __future__ import annotations

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMenu, QTableWidget

from core.i18n import t


def enable_cell_copy_menu(table: QTableWidget) -> None:
    """Muestra «Copiar» al pulsar botón derecho sobre una celda con contenido."""
    table.setContextMenuPolicy(Qt.CustomContextMenu)
    table.customContextMenuRequested.connect(
        lambda pos, tbl=table: _show_cell_copy_menu(tbl, pos)
    )


def _show_cell_copy_menu(table: QTableWidget, pos) -> None:
    item = table.itemAt(pos)
    if item is None:
        return
    text = item.text()
    if not text:
        return

    menu = QMenu(table)
    copy_action = menu.addAction(t("common.copy"))
    if menu.exec_(table.viewport().mapToGlobal(pos)) == copy_action:
        QApplication.clipboard().setText(text)
