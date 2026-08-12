"""Visor reutilizable de contenido binario en hexadecimal y texto.

Componente independiente pensado para reutilizarse en cualquier sección del
programa que necesite inspeccionar bytes en crudo (explorador de ficheros,
artefactos, búsqueda, etc.).

Flujo típico con Volatility (Windows/Linux/macOS):

  1. El plugin de volcado escribe un fichero temporal (``dumpfiles``,
     ``linux_find_file``, ``mac_dump_file``, etc.).
  2. ``load_from_dump_path()`` lee esos bytes y los muestra en hex/strings.

También admite carga directa con ``load_bytes()`` / ``load_file()`` y el
volcado asíncrono integrado con ``dump_and_show()``.
"""

from __future__ import annotations

import os
from typing import TYPE_CHECKING, Callable, List, Optional

if TYPE_CHECKING:
    from core.runner import PluginWorker, VolatilityRunner

from core.i18n import t

from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

# Límite de bytes a renderizar para no congelar la interfaz con ficheros enormes.
_DEFAULT_MAX_BYTES = 1024 * 1024  # 1 MiB

_MODE_HEX = 0
_MODE_STRINGS = 1
_MODE_BOTH = 2


class HexViewer(QWidget):
    """Muestra contenido binario en hexadecimal y/o como cadenas de texto."""

    def __init__(
        self,
        parent: Optional[QWidget] = None,
        max_bytes: int = _DEFAULT_MAX_BYTES,
        min_string_len: int = 4,
    ) -> None:
        super().__init__(parent)
        self._max_bytes = max_bytes
        self._min_string_len = min_string_len
        self._data: bytes = b""
        self._title: str = ""
        self._truncated = False
        self._build_ui()

    # ------------------------------------------------------------------ UI --
    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        top = QHBoxLayout()
        self._title_label = QLabel(t("hex.no_content"))
        self._title_label.setStyleSheet("color:#4ec9b0;")
        self._title_label.setWordWrap(True)
        top.addWidget(self._title_label, 1)

        top.addWidget(QLabel(t("hex.view_label")))
        self._mode = QComboBox()
        self._mode.addItems([t("hex.mode_hex"), t("hex.mode_strings"), t("hex.mode_both")])
        self._mode.currentIndexChanged.connect(lambda _idx: self._render())
        top.addWidget(self._mode)
        layout.addLayout(top)

        self._editor = QPlainTextEdit()
        self._editor.setReadOnly(True)
        self._editor.setLineWrapMode(QPlainTextEdit.NoWrap)
        font = QFont("monospace")
        font.setStyleHint(QFont.Monospace)
        self._editor.setFont(font)
        layout.addWidget(self._editor, 1)

    # -------------------------------------------------------------- API ----
    def clear(self) -> None:
        """Vacía el visor."""
        self._data = b""
        self._title = ""
        self._truncated = False
        self._title_label.setText(t("hex.no_content"))
        self._editor.clear()

    def load_bytes(self, data: bytes, title: str = "") -> None:
        """Carga bytes ya disponibles en memoria."""
        data = data or b""
        self._truncated = len(data) > self._max_bytes
        self._data = data[: self._max_bytes]
        self._title = title
        self._update_title()
        self._render()

    def load_file(self, path: str, title: str = "") -> None:
        """Carga el contenido de un fichero del disco."""
        try:
            with open(path, "rb") as handle:
                # Lee un byte de más para detectar truncamiento.
                data = handle.read(self._max_bytes + 1)
        except OSError as exc:
            self._data = b""
            self._truncated = False
            self._title_label.setText(t("hex.read_error", error=exc))
            self._editor.clear()
            return
        self.load_bytes(data, title or os.path.basename(path))

    def load_from_dump_path(self, path: Optional[str], title: str = "") -> Optional[str]:
        """Lee un fichero volcado por Volatility y lo muestra.

        Devuelve ``None`` si todo fue bien, o un mensaje de error en caso contrario.
        """
        if not path or not os.path.isfile(path):
            self.clear()
            return t("hex.no_readable_dump")
        try:
            with open(path, "rb") as handle:
                data = handle.read()
        except OSError as exc:
            self.clear()
            return t("hex.dump_read_error", error=exc)
        self.load_bytes(data, title=title)
        return None

    @staticmethod
    def find_largest_file_in_dir(directory: str) -> Optional[str]:
        """Devuelve el fichero de mayor tamaño dentro de ``directory``."""
        best: Optional[str] = None
        best_size = -1
        for root, _dirs, files in os.walk(directory):
            for filename in files:
                candidate = os.path.join(root, filename)
                try:
                    size = os.path.getsize(candidate)
                except OSError:
                    continue
                if size > best_size:
                    best_size = size
                    best = candidate
        return best

    def dump_and_show(
        self,
        runner: "VolatilityRunner",
        plugin: str,
        extra_args: List[str],
        title: str,
        *,
        output_path: Optional[str] = None,
        search_dir: Optional[str] = None,
        on_loaded: Optional[Callable[[str], None]] = None,
        on_failed: Optional[Callable[[str, str], None]] = None,
    ) -> "PluginWorker":
        """Ejecuta un plugin de volcado y, al terminar, muestra el resultado.

        Para ``dump_mode`` tipo fichero (Linux/macOS), pase ``output_path``.
        Para volcado en directorio (Windows ``dumpfiles``), pase ``search_dir``.
        """
        from core.runner import PluginWorker

        def _on_ok(_plugin: str, output: str) -> None:
            path = output_path
            if search_dir:
                path = self.find_largest_file_in_dir(search_dir)
            err = self.load_from_dump_path(path, title=title)
            if err:
                if on_failed:
                    on_failed(_plugin, f"{err}\n\n{t('common.plugin_output')}:\n{output[:500]}")
            elif on_loaded:
                on_loaded(title)

        worker: PluginWorker = runner.run_async(plugin, extra_args)
        worker.finished_ok.connect(_on_ok)
        if on_failed:
            worker.failed.connect(on_failed)
        return worker

    # -------------------------------------------------------------- render --
    def _update_title(self) -> None:
        name = self._title or t("hex.no_name")
        size = len(self._data)
        suffix = t("hex.truncated") if self._truncated else ""
        self._title_label.setText(t("hex.bytes_shown", name=name, size=size, suffix=suffix))

    def _render(self) -> None:
        mode = self._mode.currentIndex()
        if mode == _MODE_HEX:
            text = self._to_hex(self._data)
        elif mode == _MODE_STRINGS:
            text = self._to_strings(self._data, self._min_string_len)
        else:
            text = (
                t("hex.section_hex") + "\n"
                + self._to_hex(self._data)
                + "\n\n" + t("hex.section_strings") + "\n"
                + self._to_strings(self._data, self._min_string_len)
            )
        self._editor.setPlainText(text)

    @staticmethod
    def _to_hex(data: bytes, width: int = 16) -> str:
        """Genera un volcado hexadecimal clásico con offset, bytes y ASCII."""
        if not data:
            return t("hex.empty")
        lines: List[str] = []
        for offset in range(0, len(data), width):
            chunk = data[offset : offset + width]
            hex_cells = [f"{byte:02x}" for byte in chunk]
            # Separa en dos grupos de 8 para facilitar la lectura.
            first = " ".join(hex_cells[:8])
            second = " ".join(hex_cells[8:])
            hex_part = f"{first}  {second}".rstrip()
            hex_part = hex_part.ljust(width * 3)
            ascii_part = "".join(
                chr(byte) if 32 <= byte < 127 else "." for byte in chunk
            )
            lines.append(f"{offset:08x}  {hex_part} |{ascii_part}|")
        return "\n".join(lines)

    @staticmethod
    def _to_strings(data: bytes, min_len: int = 4) -> str:
        """Extrae secuencias de caracteres imprimibles (estilo ``strings``)."""
        if not data:
            return t("hex.empty")
        result: List[str] = []
        current: List[str] = []
        for byte in data:
            if 32 <= byte < 127:
                current.append(chr(byte))
            else:
                if len(current) >= min_len:
                    result.append("".join(current))
                current = []
        if len(current) >= min_len:
            result.append("".join(current))
        return "\n".join(result) if result else t("hex.no_printable")
