"""Artefactos forenses para imágenes Linux."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QWidget

from core.runner import VolatilityRunner
from ui.artifacts.base import ArtifactSpec, ArtifactTab

LINUX_ARTIFACTS: list[ArtifactSpec] = [
    ("art.linux.bash.label", "linux_bash", [], "art.linux.bash.desc"),
    ("art.linux.psaux.label", "linux_psaux", [], "art.linux.psaux.desc"),
    ("art.linux.netstat.label", "linux_netstat", [], "art.linux.netstat.desc"),
    ("art.linux.ifconfig.label", "linux_ifconfig", [], "art.linux.ifconfig.desc"),
    ("art.linux.lsmod.label", "linux_lsmod", [], "art.linux.lsmod.desc"),
    ("art.linux.check_syscall.label", "linux_check_syscall", [], "art.linux.check_syscall.desc"),
    ("art.linux.check_creds.label", "linux_check_creds", [], "art.linux.check_creds.desc"),
    ("art.linux.mount.label", "linux_mount", [], "art.linux.mount.desc"),
    ("art.linux.dmesg.label", "linux_dmesg", [], "art.linux.dmesg.desc"),
    ("art.linux.lsof.label", "linux_lsof", [], "art.linux.lsof.desc"),
    ("art.linux.proc_maps.label", "linux_proc_maps", [], "art.linux.proc_maps.desc"),
    ("art.linux.hidden_modules.label", "linux_hidden_modules", [], "art.linux.hidden_modules.desc"),
    ("art.linux.route_cache.label", "linux_route_cache", [], "art.linux.route_cache.desc"),
    ("art.linux.psenv.label", "linux_psenv", [], "art.linux.psenv.desc"),
]


class LinuxArtifactsTab(ArtifactTab):
    """Pestaña de artefactos Linux."""

    def __init__(self, runner: VolatilityRunner, parent: Optional[QWidget] = None) -> None:
        super().__init__(runner, LINUX_ARTIFACTS, parent)
