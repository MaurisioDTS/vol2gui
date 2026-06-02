"""Wrapper de ejecución del binario Volatility 2.6 standalone.

Ofrece dos modos:
  - ``run``: ejecución síncrona, devuelve la salida completa.
  - ``run_async``: ejecución en un QThread, emite señales con el resultado
    para no bloquear la interfaz.
"""

from __future__ import annotations

import os
import shlex
import subprocess
from typing import List, Optional

from PyQt5.QtCore import QObject, QThread, pyqtSignal


class VolatilityError(Exception):
    """Error al ejecutar el binario de Volatility."""


class VolatilityRunner:
    """Encapsula las llamadas al binario ``volatility``.

    Mantiene la ruta del binario, la imagen activa y el perfil detectado para
    no tener que repetirlos en cada plugin.
    """

    def __init__(
        self,
        binary_path: str,
        image_path: Optional[str] = None,
        profile: Optional[str] = None,
    ) -> None:
        self.binary_path = os.path.abspath(binary_path)
        if not os.path.isfile(self.binary_path):
            raise VolatilityError(f"No se encontró el binario: {self.binary_path}")
        self.image_path = image_path
        self.profile = profile

    def build_command(self, plugin: str, extra_args: Optional[List[str]] = None) -> List[str]:
        """Construye la lista de argumentos para ``subprocess``."""
        cmd: List[str] = [self.binary_path]
        if self.image_path:
            cmd += ["-f", self.image_path]
        if self.profile:
            cmd += ["--profile", self.profile]
        cmd.append(plugin)
        if extra_args:
            cmd += extra_args
        return cmd

    def run(
        self,
        plugin: str,
        extra_args: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> str:
        """Ejecuta un plugin de forma síncrona y devuelve stdout.

        Volatility 2 escribe avisos y mensajes de progreso por stderr; los
        concatenamos sólo si stdout queda vacío para no perder información de
        error útil.
        """
        cmd = self.build_command(plugin, extra_args)
        try:
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=timeout,
                check=False,
            )
        except FileNotFoundError as exc:  # pragma: no cover - defensivo
            raise VolatilityError(f"No se pudo ejecutar el binario: {exc}") from exc
        except subprocess.TimeoutExpired as exc:
            raise VolatilityError(
                f"El plugin '{plugin}' superó el tiempo límite ({timeout}s)."
            ) from exc

        stdout = proc.stdout.decode("utf-8", errors="replace")
        stderr = proc.stderr.decode("utf-8", errors="replace")

        if not stdout.strip() and stderr.strip():
            # Probablemente un error de perfil o de imagen.
            return stderr
        return stdout

    def command_string(self, plugin: str, extra_args: Optional[List[str]] = None) -> str:
        """Devuelve el comando como cadena legible (para el log forense)."""
        return " ".join(shlex.quote(part) for part in self.build_command(plugin, extra_args))

    def run_async(
        self,
        plugin: str,
        extra_args: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> "PluginWorker":
        """Crea y arranca un worker en segundo plano. Devuelve el worker.

        El llamante debe conectar las señales ``finished`` / ``failed`` antes
        de que termine; como mínimo debe guardar la referencia para que el
        QThread no sea recolectado.
        """
        worker = PluginWorker(self, plugin, extra_args, timeout)
        worker.start()
        return worker


class PluginWorker(QThread):
    """Ejecuta un plugin en un hilo aparte y emite el resultado."""

    finished_ok = pyqtSignal(str, str)  # (plugin, salida)
    failed = pyqtSignal(str, str)  # (plugin, mensaje de error)

    def __init__(
        self,
        runner: VolatilityRunner,
        plugin: str,
        extra_args: Optional[List[str]] = None,
        timeout: Optional[int] = None,
    ) -> None:
        super().__init__()
        self._runner = runner
        self._plugin = plugin
        self._extra_args = extra_args
        self._timeout = timeout

    def run(self) -> None:  # noqa: D401 - override de QThread
        try:
            output = self._runner.run(self._plugin, self._extra_args, self._timeout)
            self.finished_ok.emit(self._plugin, output)
        except VolatilityError as exc:
            self.failed.emit(self._plugin, str(exc))
        except Exception as exc:  # pragma: no cover - defensivo
            self.failed.emit(self._plugin, f"Error inesperado: {exc}")
