"""Explorador del sistema de ficheros en memoria.

Enumera los ficheros presentes en la imagen (sin extraerlos) y los presenta en
un árbol navegable. La extracción es SIEMPRE bajo demanda: el usuario
selecciona un fichero, pulsa «Extraer» y el sistema operativo muestra un
diálogo para elegir el destino.

Plugins por SO:
  - Windows: ``filescan`` (enumerar) + ``dumpfiles -Q <offset> -D <dir>``.
  - Linux:   ``linux_enumerate_files`` + ``linux_find_file -i <inodo> -O <fichero>``.
  - Mac:     ``mac_list_files`` (enumerar) + ``mac_dump_file -q <vnode> -O <fichero>``.
"""

from __future__ import annotations

import os
import shutil
import tempfile
from typing import Dict, List, Optional

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QProgressBar,
    QPushButton,
    QSplitter,
    QStyle,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from core.parser import parse_table
from core.runner import PluginWorker, VolatilityRunner
from core.profile import OSType
from ui.widgets.hex_viewer import HexViewer
from utils import audit_log

# Columnas del árbol: primero el identificador (offset/inodo), luego el nombre.
_COL_ID = 0
_COL_NAME = 1
_COL_SIZE = 2
_COL_MTIME = 3

# Roles de datos en los items del árbol.
_ROLE_IDENTIFIER = Qt.UserRole + 1  # offset/inodo para extracción
_ROLE_FULLPATH = Qt.UserRole + 2
_ROLE_IS_FILE = Qt.UserRole + 3


_FS_CONFIG = {
    OSType.WINDOWS: {
        "enum_plugin": "filescan",
        "id_headers": ["Offset(P)", "Offset"],
        "path_headers": ["Name"],
        "size_headers": ["Size", "File Size", "FileSize", "Length"],
        "mtime_headers": ["Modified", "Modified Time", "MTime", "LastWrite", "Last Write", "LastWriteTime"],
        "dump_plugin": "dumpfiles",
        "dump_mode": "dir",  # dumpfiles escribe en un directorio
        "dump_id_flag": "-Q",
        "dump_dir_flag": "-D",
        "separator": "\\",
        "strip_prefixes": ["\\Device\\HarddiskVolume1", "\\Device\\HarddiskVolume2", "\\Device\\HarddiskVolume0"],
    },
    OSType.LINUX: {
        "enum_plugin": "linux_enumerate_files",
        "id_headers": ["Inode Address", "Inode"],
        "path_headers": ["Path", "File Path"],
        "size_headers": ["Size", "File Size", "FileSize", "Length"],
        "mtime_headers": ["Modified", "Modified Time", "MTime", "Last Modified", "LastWrite", "Last Write"],
        "dump_plugin": "linux_find_file",
        "dump_mode": "file",  # linux_find_file escribe un fichero concreto
        "dump_id_flag": "-i",
        "dump_out_flag": "-O",
        "separator": "/",
        "strip_prefixes": [],
    },
    OSType.MAC: {
        "enum_plugin": "mac_list_files",
        "id_headers": ["Offset", "File Pointer", "Address", "Vnode", "vnode"],
        "path_headers": ["Path", "File Path"],
        "size_headers": ["Size", "File Size", "FileSize", "Length"],
        "mtime_headers": ["Modified", "Modified Time", "MTime", "Last Modified", "LastWrite", "Last Write"],
        "dump_plugin": "mac_dump_file",
        "dump_mode": "file",  # mac_dump_file escribe un fichero concreto
        "dump_id_flag": "-q",
        "dump_out_flag": "-O",
        "separator": "/",
        "strip_prefixes": [],
    },
}


def _config_for(os_type: OSType) -> Dict:
    return _FS_CONFIG.get(os_type, _FS_CONFIG[OSType.WINDOWS])


def _build_dump_extra(config: Dict, identifier: str, output_path: str) -> List[str]:
    """Construye los argumentos del plugin de volcado según el SO."""
    if config["dump_mode"] == "dir":
        return [
            config.get("dump_id_flag", "-Q"),
            identifier,
            config.get("dump_dir_flag", "-D"),
            output_path,
        ]
    return [
        config.get("dump_id_flag", "-i"),
        identifier,
        config.get("dump_out_flag", "-O"),
        output_path,
    ]


class FilesystemView(QWidget):
    """Árbol navegable de ficheros con extracción bajo demanda."""

    def __init__(
        self,
        runner: VolatilityRunner,
        os_type: OSType,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self._runner = runner
        self._os_type = os_type
        self._config = _config_for(os_type)
        self._worker: Optional[PluginWorker] = None
        self._dump_workers: List[PluginWorker] = []
        self._temp_dirs: List[str] = []
        self._loaded = False
        self._dir_icon = self.style().standardIcon(QStyle.SP_DirIcon)
        self._file_icon = self.style().standardIcon(QStyle.SP_FileIcon)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        controls = QHBoxLayout()
        self._load_btn = QPushButton(f"Enumerar ficheros ({self._config['enum_plugin']})")
        self._load_btn.clicked.connect(self.load)
        controls.addWidget(self._load_btn)

        self._filter = QLineEdit()
        self._filter.setPlaceholderText("Filtrar por nombre o ruta...")
        self._filter.textChanged.connect(self._apply_filter)
        controls.addWidget(self._filter, 1)

        self._preview_btn = QPushButton("Visualizar (hex/strings)")
        self._preview_btn.clicked.connect(self._preview_selected)
        self._preview_btn.setEnabled(False)
        controls.addWidget(self._preview_btn)

        self._extract_btn = QPushButton("Extraer seleccionado...")
        self._extract_btn.clicked.connect(self._extract_selected)
        self._extract_btn.setEnabled(False)
        controls.addWidget(self._extract_btn)
        layout.addLayout(controls)

        warn = QLabel(
            "Esta vista NO extrae ficheros automáticamente. Selecciona un fichero "
            "y pulsa «Visualizar» para inspeccionarlo (volcado temporal) o «Extraer» "
            "para elegir dónde volcarlo de forma permanente."
        )
        warn.setWordWrap(True)
        warn.setStyleSheet("color:#d7ba7d;font-size:11px;")
        layout.addWidget(warn)

        self._progress = QProgressBar()
        self._progress.setRange(0, 0)
        self._progress.hide()
        layout.addWidget(self._progress)

        self._status = QLabel("Pulsa «Enumerar ficheros» para construir el árbol.")
        self._status.setStyleSheet("color:#4ec9b0;")
        layout.addWidget(self._status)

        # Pantalla dividida: árbol a la izquierda, visor hex/strings a la derecha.
        splitter = QSplitter(Qt.Horizontal)

        self._tree = QTreeWidget()
        self._tree.setHeaderLabels(
            ["Identificador (offset/inodo)", "Nombre", "Tamaño", "Modificado"]
        )
        self._tree.itemSelectionChanged.connect(self._on_selection_changed)
        self._tree.setContextMenuPolicy(Qt.CustomContextMenu)
        self._tree.customContextMenuRequested.connect(self._on_context_menu)
        splitter.addWidget(self._tree)

        self._viewer = HexViewer()
        splitter.addWidget(self._viewer)
        splitter.setStretchFactor(0, 3)
        splitter.setStretchFactor(1, 4)
        layout.addWidget(splitter, 1)

    # ----------------------------------------------------------------- carga --
    def load(self) -> None:
        if self._worker is not None and self._worker.isRunning():
            return
        self._loaded = True
        self._load_btn.setEnabled(False)
        self._progress.show()
        plugin = self._config["enum_plugin"]
        self._status.setText(f"Enumerando ficheros con {plugin} (puede tardar)...")
        audit_log.log_plugin(plugin, self._runner.command_string(plugin))
        self._worker = self._runner.run_async(plugin)
        self._worker.finished_ok.connect(self._on_enum_finished)
        self._worker.failed.connect(self._on_failed)

    def load_if_needed(self) -> None:
        if not self._loaded:
            self.load()

    def _on_enum_finished(self, _plugin: str, output: str) -> None:
        self._progress.hide()
        self._load_btn.setEnabled(True)
        headers, rows = parse_table(output)
        id_idx = self._find_col(headers, self._config["id_headers"])
        path_idx = self._find_col(headers, self._config["path_headers"])
        size_idx = self._find_col(headers, self._config.get("size_headers", []))
        mtime_idx = self._find_col(headers, self._config.get("mtime_headers", []))
        if path_idx < 0:
            self._status.setText("No se pudo interpretar la salida (usa la pestaña de artefactos).")
            return
        entries = []
        for row in rows:
            if path_idx >= len(row):
                continue
            path = row[path_idx].strip()
            identifier = row[id_idx].strip() if 0 <= id_idx < len(row) else ""
            size = row[size_idx].strip() if 0 <= size_idx < len(row) else ""
            mtime = row[mtime_idx].strip() if 0 <= mtime_idx < len(row) else ""
            if path:
                entries.append((path, identifier, size, mtime))
        self._build_tree(entries)
        self._status.setText(f"{len(entries)} ficheros enumerados.")

    def _on_failed(self, plugin: str, message: str) -> None:
        self._progress.hide()
        self._load_btn.setEnabled(True)
        self._status.setText(f"Error en {plugin}.")
        QMessageBox.warning(self, f"Error en {plugin}", message)

    @staticmethod
    def _find_col(headers: List[str], candidates: List[str]) -> int:
        for cand in candidates:
            for idx, header in enumerate(headers):
                if cand.lower() == header.strip().lower():
                    return idx
        # Coincidencia parcial como respaldo.
        for cand in candidates:
            for idx, header in enumerate(headers):
                if cand.lower() in header.strip().lower():
                    return idx
        return -1

    # ------------------------------------------------------------- árbol -----
    def _build_tree(self, entries: List) -> None:
        # Desactiva la ordenación mientras se inserta para no reordenar en cada
        # alta; se reactiva al final ordenando por nombre.
        self._tree.setSortingEnabled(False)
        self._tree.clear()
        sep = self._config["separator"]
        root_nodes: Dict[str, QTreeWidgetItem] = {}

        for path, identifier, size, mtime in entries:
            clean = path
            for prefix in self._config["strip_prefixes"]:
                if clean.startswith(prefix):
                    clean = clean[len(prefix):]
                    break
            parts = [p for p in clean.replace("\\", sep).split(sep) if p]
            if not parts:
                continue

            parent: Optional[QTreeWidgetItem] = None
            accumulated = ""
            for depth, part in enumerate(parts):
                accumulated += sep + part
                is_last = depth == len(parts) - 1
                child = self._find_child(parent, part, root_nodes)
                if child is None:
                    child = QTreeWidgetItem(
                        [
                            identifier if is_last else "",
                            part,
                            size if is_last else "",
                            mtime if is_last else "",
                        ]
                    )
                    child.setData(0, _ROLE_FULLPATH, accumulated)
                    child.setData(0, _ROLE_IS_FILE, is_last)
                    child.setIcon(
                        _COL_NAME, self._file_icon if is_last else self._dir_icon
                    )
                    if is_last:
                        child.setData(0, _ROLE_IDENTIFIER, identifier)
                    if parent is None:
                        self._tree.addTopLevelItem(child)
                        root_nodes[part] = child
                    else:
                        parent.addChild(child)
                elif not is_last and child.data(0, _ROLE_IS_FILE):
                    # Un nodo creado como fichero resulta ser también carpeta
                    # (otra ruta más larga lo contiene): pásalo a directorio.
                    child.setData(0, _ROLE_IS_FILE, False)
                    child.setData(0, _ROLE_IDENTIFIER, "")
                    child.setText(_COL_ID, "")
                    child.setText(_COL_SIZE, "")
                    child.setText(_COL_MTIME, "")
                    child.setIcon(_COL_NAME, self._dir_icon)
                parent = child

        self._tree.setSortingEnabled(True)
        self._tree.sortByColumn(_COL_NAME, Qt.AscendingOrder)

    @staticmethod
    def _find_child(
        parent: Optional[QTreeWidgetItem],
        name: str,
        root_nodes: Dict[str, QTreeWidgetItem],
    ) -> Optional[QTreeWidgetItem]:
        if parent is None:
            return root_nodes.get(name)
        for i in range(parent.childCount()):
            child = parent.child(i)
            if child.text(_COL_NAME) == name:
                return child
        return None

    # ---------------------------------------------------------------- filtro --
    def _apply_filter(self, text: str) -> None:
        text = text.lower().strip()
        self._filter_node(self._tree.invisibleRootItem(), text)

    def _filter_node(self, parent: QTreeWidgetItem, text: str) -> bool:
        any_visible = False
        for i in range(parent.childCount()):
            child = parent.child(i)
            child_visible = self._filter_node(child, text)
            full_path = str(child.data(0, _ROLE_FULLPATH) or "").lower()
            own = (
                (not text)
                or text in child.text(_COL_NAME).lower()
                or text in full_path
            )
            visible = child_visible or own
            child.setHidden(not visible)
            any_visible = any_visible or visible
        return any_visible

    # --------------------------------------------------------------- selección --
    def _on_selection_changed(self) -> None:
        item = self._current_file_item()
        can_dump = item is not None and self._config["dump_plugin"] is not None
        self._extract_btn.setEnabled(can_dump)
        self._preview_btn.setEnabled(can_dump)

    def _current_file_item(self) -> Optional[QTreeWidgetItem]:
        items = self._tree.selectedItems()
        if not items:
            return None
        item = items[0]
        if item.data(0, _ROLE_IS_FILE):
            return item
        return None

    def _on_context_menu(self, pos) -> None:
        from PyQt5.QtWidgets import QMenu

        item = self._tree.itemAt(pos)
        if item is None or not item.data(0, _ROLE_IS_FILE):
            return
        menu = QMenu(self)
        preview_action = menu.addAction("Visualizar (hex/strings)")
        extract_action = menu.addAction("Extraer este fichero...")
        chosen = menu.exec_(self._tree.viewport().mapToGlobal(pos))
        if chosen == preview_action:
            self._preview_item(item)
        elif chosen == extract_action:
            self._extract_item(item)

    # ------------------------------------------------------------ extracción --
    def _extract_selected(self) -> None:
        item = self._current_file_item()
        if item is not None:
            self._extract_item(item)

    def _extract_item(self, item: QTreeWidgetItem) -> None:
        dump_plugin = self._config["dump_plugin"]
        if not dump_plugin:
            QMessageBox.information(
                self,
                "No soportado",
                "La extracción individual de ficheros no está soportada para este SO en Volatility 2.",
            )
            return

        identifier = item.data(0, _ROLE_IDENTIFIER) or ""
        full_path = item.data(0, _ROLE_FULLPATH) or item.text(_COL_NAME)
        suggested_name = os.path.basename(full_path.replace("\\", "/")) or "extraido.bin"

        if self._config["dump_mode"] == "dir":
            dest_dir = QFileDialog.getExistingDirectory(
                self, "Elegir carpeta de destino para la extracción"
            )
            if not dest_dir:
                return
            extra = _build_dump_extra(self._config, identifier, dest_dir)
            destination = dest_dir
        else:  # mode == "file"
            dest_file, _ = QFileDialog.getSaveFileName(
                self, "Guardar fichero extraído como", suggested_name
            )
            if not dest_file:
                return
            extra = _build_dump_extra(self._config, identifier, dest_file)
            destination = dest_file

        if not identifier:
            QMessageBox.warning(self, "Sin identificador", "Este fichero no tiene offset/inodo para extraer.")
            return

        self._status.setText(f"Extrayendo {suggested_name}...")
        self._progress.show()
        audit_log.log_extraction(
            dump_plugin, destination, target=full_path
        )
        worker = self._runner.run_async(dump_plugin, extra)
        worker.finished_ok.connect(self._make_extract_handler(suggested_name, destination))
        worker.failed.connect(self._on_failed)
        self._dump_workers.append(worker)

    def _make_extract_handler(self, name: str, destination: str):
        def handler(_plugin: str, output: str) -> None:
            self._progress.hide()
            self._status.setText(f"Extracción finalizada: {name} -> {destination}")
            QMessageBox.information(
                self,
                "Extracción completada",
                f"Fichero: {name}\nDestino: {destination}\n\nSalida del plugin:\n{output[:500]}",
            )
        return handler

    # --------------------------------------------------------- previsualización --
    def _preview_selected(self) -> None:
        item = self._current_file_item()
        if item is not None:
            self._preview_item(item)

    def _preview_item(self, item: QTreeWidgetItem) -> None:
        """Vuelca el fichero a una carpeta temporal y lo carga en el visor.

        A diferencia de «Extraer», el destino es temporal y se limpia
        automáticamente; sirve sólo para inspeccionar el contenido en hex/texto.
        """
        dump_plugin = self._config["dump_plugin"]
        if not dump_plugin:
            QMessageBox.information(
                self,
                "No soportado",
                "La visualización individual de ficheros no está soportada para "
                "este SO en Volatility 2.",
            )
            return

        identifier = item.data(0, _ROLE_IDENTIFIER) or ""
        if not identifier:
            QMessageBox.warning(
                self, "Sin identificador", "Este fichero no tiene offset/inodo para volcar."
            )
            return

        full_path = item.data(0, _ROLE_FULLPATH) or item.text(_COL_NAME)
        name = os.path.basename(full_path.replace("\\", "/")) or "previsualizacion.bin"

        # Limpia volcados temporales previos (su contenido ya está en memoria).
        self._cleanup_temp_dirs()
        tmp_dir = tempfile.mkdtemp(prefix="vol2gui_preview_")
        self._temp_dirs.append(tmp_dir)

        dump_mode = self._config["dump_mode"]
        if dump_mode == "dir":
            target = tmp_dir
            extra = _build_dump_extra(self._config, identifier, tmp_dir)
        else:
            target = os.path.join(tmp_dir, name)
            extra = _build_dump_extra(self._config, identifier, target)

        self._status.setText(f"Volcando {name} (temporal) para previsualizar...")
        self._progress.show()
        audit_log.log_action(
            f"PREVISUALIZACIÓN: {full_path} | volcado temporal en {tmp_dir}"
        )
        worker = self._viewer.dump_and_show(
            self._runner,
            dump_plugin,
            extra,
            name,
            output_path=target if dump_mode == "file" else None,
            search_dir=tmp_dir if dump_mode == "dir" else None,
            on_loaded=self._on_preview_loaded,
            on_failed=self._on_preview_failed,
        )
        self._dump_workers.append(worker)

    def _on_preview_loaded(self, name: str) -> None:
        self._progress.hide()
        self._status.setText(f"Previsualizando {name} (bytes en memoria).")

    def _on_preview_failed(self, plugin: str, message: str) -> None:
        self._progress.hide()
        self._status.setText("No se pudo previsualizar.")
        QMessageBox.information(self, f"Error en {plugin}", message)

    def _cleanup_temp_dirs(self) -> None:
        for path in self._temp_dirs:
            shutil.rmtree(path, ignore_errors=True)
        self._temp_dirs.clear()

    def closeEvent(self, event) -> None:  # noqa: N802 - override Qt
        self._cleanup_temp_dirs()
        super().closeEvent(event)
