"""Selección de imagen de RAM y reporte automático inicial.

Contiene:
  - ``StartupDialog``: diálogo para elegir el binario de Volatility y la imagen.
  - ``HashWorker``: calcula MD5/SHA256 de la imagen en segundo plano.
  - ``ImageReportWidget``: ejecuta ``imageinfo`` y muestra el reporte (SO,
    perfil, fecha, arquitectura, KDBG) más los hashes de integridad.
"""

from __future__ import annotations

import hashlib
import os
from typing import Optional

from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QProgressBar,
    QPushButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from core.parser import parse_imageinfo
from core.profile import OSType, ProfileInfo, detect_from_imageinfo, profile_summary
from core.profiles import default_profiles_dir, has_profiles
from core.runner import PluginWorker, ProfileListWorker, VolatilityError, VolatilityRunner
from utils import audit_log


def _default_binary() -> str:
    """Ruta por defecto del binario: ``volatility`` junto a la app."""
    here = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    candidate = os.path.join(here, "volatility")
    return candidate if os.path.isfile(candidate) else ""


class StartupDialog(QDialog):
    """Pide la ruta del binario de Volatility y de la imagen de RAM."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Volatility 2 GUI - Cargar imagen")
        self.resize(620, 200)
        self.binary_path = ""
        self.image_path = ""
        self.manual_profile = ""
        self._profile_worker: Optional[ProfileListWorker] = None
        self._build_ui()
        self._refresh_local_profiles()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        form = QFormLayout()

        self._binary = QLineEdit(_default_binary())
        self._binary.editingFinished.connect(self._refresh_local_profiles)
        bin_row = QHBoxLayout()
        bin_row.addWidget(self._binary, 1)
        bin_btn = QPushButton("...")
        bin_btn.setFixedWidth(36)
        bin_btn.clicked.connect(self._pick_binary)
        bin_row.addWidget(bin_btn)
        bin_container = QWidget()
        bin_container.setLayout(bin_row)
        form.addRow("Binario Volatility:", bin_container)

        self._image = QLineEdit()
        img_row = QHBoxLayout()
        img_row.addWidget(self._image, 1)
        img_btn = QPushButton("...")
        img_btn.setFixedWidth(36)
        img_btn.clicked.connect(self._pick_image)
        img_row.addWidget(img_btn)
        img_container = QWidget()
        img_container.setLayout(img_row)
        form.addRow("Imagen de RAM:", img_container)

        self._profile = QComboBox()
        self._profile.setEditable(True)
        self._profile.lineEdit().setPlaceholderText(
            "(opcional) perfil manual, p. ej. Win7SP1x64 o LinuxUbuntu..."
        )
        form.addRow("Perfil (opcional):", self._profile)

        layout.addLayout(form)

        hint = QLabel(
            "El perfil puede dejarse vacío: se detectará con «imageinfo». "
            "Para Linux/Mac suele ser necesario indicarlo manualmente. Los "
            "perfiles guardados en la carpeta «profiles/» se cargan "
            "automáticamente en este desplegable."
        )
        hint.setWordWrap(True)
        hint.setStyleSheet("color:#888;font-size:11px;")
        layout.addWidget(hint)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).setText("Cargar")
        buttons.accepted.connect(self._accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _pick_binary(self) -> None:
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar binario Volatility")
        if path:
            self._binary.setText(path)

    def _pick_image(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar imagen de RAM",
            "",
            "Imágenes de memoria (*.raw *.mem *.vmem *.dmp *.lime *.bin *.img *.dump);;Todos los archivos (*)",
        )
        if path:
            self._image.setText(path)

    def _accept(self) -> None:
        from PyQt5.QtWidgets import QMessageBox

        binary = self._binary.text().strip()
        image = self._image.text().strip()
        if not binary or not os.path.isfile(binary):
            QMessageBox.warning(self, "Binario no válido", "Selecciona un binario de Volatility válido.")
            return
        if not image or not os.path.isfile(image):
            QMessageBox.warning(self, "Imagen no válida", "Selecciona una imagen de RAM válida.")
            return
        self.binary_path = binary
        self.image_path = image
        self.manual_profile = self._profile.currentText().strip()
        self.accept()

    def _refresh_local_profiles(self) -> None:
        """Carga en el desplegable los perfiles de la carpeta ``profiles/``.

        Necesita un binario válido (``--info`` lo ejecuta el binario) y que la
        carpeta contenga archivos de perfil. Se hace en segundo plano para no
        bloquear el diálogo.
        """
        binary = self._binary.text().strip()
        profiles_dir = default_profiles_dir()
        if not binary or not os.path.isfile(binary) or not has_profiles(profiles_dir):
            return
        if self._profile_worker is not None and self._profile_worker.isRunning():
            return
        try:
            runner = VolatilityRunner(binary, profiles_dir=profiles_dir)
        except VolatilityError:
            return
        self._profile_worker = ProfileListWorker(runner)
        self._profile_worker.finished_ok.connect(self._on_local_profiles)
        self._profile_worker.start()

    def _on_local_profiles(self, profiles: list) -> None:
        current = self._profile.currentText()
        for prof in profiles:
            if self._profile.findText(prof) < 0:
                self._profile.addItem(prof)
        # Preserva lo que el analista hubiera escrito a mano.
        self._profile.setCurrentText(current)


class HashWorker(QThread):
    """Calcula MD5 y SHA256 de la imagen sin bloquear la UI."""

    finished_ok = pyqtSignal(str, str)  # md5, sha256
    progress = pyqtSignal(int)  # porcentaje 0-100

    def __init__(self, image_path: str) -> None:
        super().__init__()
        self._image_path = image_path

    def run(self) -> None:
        md5 = hashlib.md5()
        sha256 = hashlib.sha256()
        try:
            total = os.path.getsize(self._image_path)
            read = 0
            chunk = 1024 * 1024 * 8
            with open(self._image_path, "rb") as fh:
                while True:
                    data = fh.read(chunk)
                    if not data:
                        break
                    md5.update(data)
                    sha256.update(data)
                    read += len(data)
                    if total:
                        self.progress.emit(int(read * 100 / total))
            self.finished_ok.emit(md5.hexdigest(), sha256.hexdigest())
        except OSError:
            self.finished_ok.emit("(error)", "(error)")


class ImageReportWidget(QWidget):
    """Muestra el reporte automático de la imagen: hashes + imageinfo."""

    profile_detected = pyqtSignal(object)  # emite un ProfileInfo

    def __init__(self, runner: VolatilityRunner, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._runner = runner
        self._hash_worker: Optional[HashWorker] = None
        self._info_worker: Optional[PluginWorker] = None
        self._profile_worker: Optional[ProfileListWorker] = None
        self._local_profiles: list = []
        self._profile_info = ProfileInfo()
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)

        title = QLabel("Reporte automático de la imagen")
        title.setStyleSheet("font-size:15px;color:#4ec9b0;font-weight:bold;")
        layout.addWidget(title)

        self._summary = QLabel("Analizando imagen...")
        self._summary.setWordWrap(True)
        self._summary.setTextInteractionFlags(Qt.TextSelectableByMouse)
        self._summary.setStyleSheet("font-family:monospace;")
        layout.addWidget(self._summary)

        self._hash_progress = QProgressBar()
        self._hash_progress.setFormat("Calculando hashes... %p%")
        layout.addWidget(self._hash_progress)

        self._info_progress = QProgressBar()
        self._info_progress.setRange(0, 0)
        self._info_progress.setFormat("Ejecutando imageinfo...")
        layout.addWidget(self._info_progress)

        layout.addWidget(QLabel("Salida de imageinfo:"))
        self._raw = QTextEdit()
        self._raw.setReadOnly(True)
        self._raw.setLineWrapMode(QTextEdit.NoWrap)
        self._raw.setStyleSheet("font-family:monospace;")
        layout.addWidget(self._raw, 1)

        profile_row = QHBoxLayout()
        profile_row.addWidget(QLabel("Perfil activo:"))
        self._profile_combo = QComboBox()
        self._profile_combo.setEditable(True)
        self._profile_combo.currentTextChanged.connect(self._on_profile_changed)
        profile_row.addWidget(self._profile_combo, 1)
        self._apply_btn = QPushButton("Aplicar perfil")
        self._apply_btn.clicked.connect(self._apply_profile)
        profile_row.addWidget(self._apply_btn)
        layout.addLayout(profile_row)

    # --------------------------------------------------------------- arranque --
    def start(self) -> None:
        """Lanza el cálculo de hashes y la ejecución de imageinfo."""
        self._md5 = ""
        self._sha256 = ""

        self._hash_worker = HashWorker(self._runner.image_path)
        self._hash_worker.progress.connect(self._hash_progress.setValue)
        self._hash_worker.finished_ok.connect(self._on_hashes)
        self._hash_worker.start()

        audit_log.log_plugin("imageinfo", self._runner.command_string("imageinfo"))
        self._info_worker = self._runner.run_async("imageinfo")
        self._info_worker.finished_ok.connect(self._on_imageinfo)
        self._info_worker.failed.connect(self._on_info_failed)

        # Carga en segundo plano los perfiles de la carpeta ``profiles/`` para
        # ofrecerlos como recursos en el desplegable de perfil activo.
        self._profile_worker = ProfileListWorker(self._runner)
        self._profile_worker.finished_ok.connect(self._on_local_profiles)
        self._profile_worker.start()

    # ---------------------------------------------------------------- hashes --
    def _on_hashes(self, md5: str, sha256: str) -> None:
        self._md5 = md5
        self._sha256 = sha256
        self._hash_progress.setValue(100)
        self._hash_progress.setFormat("Hashes calculados")
        audit_log.log_image_loaded(self._runner.image_path, md5, sha256)
        self._refresh_summary()

    # ------------------------------------------------------------- imageinfo --
    def _on_imageinfo(self, _plugin: str, output: str) -> None:
        self._info_progress.hide()
        self._raw.setPlainText(output)
        self._profile_info = detect_from_imageinfo(output)
        self._populate_profiles()
        self._refresh_summary()
        self.profile_detected.emit(self._profile_info)

    def _on_info_failed(self, _plugin: str, message: str) -> None:
        self._info_progress.hide()
        self._raw.setPlainText(f"Error al ejecutar imageinfo:\n{message}")

    def _populate_profiles(self) -> None:
        self._profile_combo.blockSignals(True)
        self._profile_combo.clear()
        if self._runner.profile:
            self._profile_combo.addItem(self._runner.profile)
        for prof in self._profile_info.suggested_profiles:
            if self._profile_combo.findText(prof) < 0:
                self._profile_combo.addItem(prof)
        if self._profile_combo.count() == 0 and self._profile_info.selected_profile:
            self._profile_combo.addItem(self._profile_info.selected_profile)
        # Añade los perfiles locales (carpeta ``profiles/``) ya conocidos.
        for prof in self._local_profiles:
            if self._profile_combo.findText(prof) < 0:
                self._profile_combo.addItem(prof)
        self._profile_combo.blockSignals(False)
        # Asegura que el runner tenga un perfil si se detectó alguno.
        if not self._runner.profile and self._profile_info.selected_profile:
            self._runner.profile = self._profile_info.selected_profile
            self._profile_combo.setCurrentText(self._profile_info.selected_profile)

    def _on_local_profiles(self, profiles: list) -> None:
        """Incorpora al desplegable los perfiles de la carpeta ``profiles/``."""
        self._local_profiles = profiles or []
        if not self._local_profiles:
            return
        current = self._profile_combo.currentText()
        self._profile_combo.blockSignals(True)
        for prof in self._local_profiles:
            if self._profile_combo.findText(prof) < 0:
                self._profile_combo.addItem(prof)
        if current:
            self._profile_combo.setCurrentText(current)
        self._profile_combo.blockSignals(False)
        audit_log.log_action(
            "Perfiles locales cargados desde profiles/: " + ", ".join(self._local_profiles)
        )

    def _on_profile_changed(self, text: str) -> None:
        # Sólo actualiza la previsualización; se aplica con el botón.
        pass

    def _apply_profile(self) -> None:
        profile = self._profile_combo.currentText().strip()
        if profile:
            self._runner.profile = profile
            self._profile_info.selected_profile = profile
            audit_log.log_action(f"PERFIL aplicado: {profile}")
            self._refresh_summary()

    # ---------------------------------------------------------------- resumen --
    def _refresh_summary(self) -> None:
        parsed = parse_imageinfo(self._profile_info.raw_imageinfo)
        lines = [
            f"Imagen        : {self._runner.image_path}",
            f"MD5           : {getattr(self, '_md5', '') or '(calculando...)'}",
            f"SHA256        : {getattr(self, '_sha256', '') or '(calculando...)'}",
            "",
            profile_summary(self._profile_info),
        ]
        for key in ("Image date and time", "Image local date and time", "Number of Processors", "KDBG"):
            if key in parsed:
                lines.append(f"{key}: {parsed[key]}")
        self._summary.setText("\n".join(lines))

    @property
    def profile_info(self) -> ProfileInfo:
        return self._profile_info
