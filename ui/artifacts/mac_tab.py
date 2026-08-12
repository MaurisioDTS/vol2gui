"""Artefactos forenses para imágenes macOS."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QWidget

from core.runner import VolatilityRunner
from ui.artifacts.base import ArtifactSpec, ArtifactTab

MAC_ARTIFACTS: list[ArtifactSpec] = [
    ("art.mac.bash.label", "mac_bash", [], "art.mac.bash.desc"),
    ("art.mac.netstat.label", "mac_netstat", [], "art.mac.netstat.desc"),
    ("art.mac.ifconfig.label", "mac_ifconfig", [], "art.mac.ifconfig.desc"),
    ("art.mac.lsmod.label", "mac_lsmod", [], "art.mac.lsmod.desc"),
    ("art.mac.check_syscall.label", "mac_check_syscall", [], "art.mac.check_syscall.desc"),
    ("art.mac.trustedbsd.label", "mac_trustedbsd", [], "art.mac.trustedbsd.desc"),
    ("art.mac.dyld_maps.label", "mac_dyld_maps", [], "art.mac.dyld_maps.desc"),
    ("art.mac.lsof.label", "mac_lsof", [], "art.mac.lsof.desc"),
    ("art.mac.psenv.label", "mac_psenv", [], "art.mac.psenv.desc"),
    ("art.mac.list_files.label", "mac_list_files", [], "art.mac.list_files.desc"),
    ("art.mac.arp.label", "mac_arp", [], "art.mac.arp.desc"),
    ("art.mac.route.label", "mac_route", [], "art.mac.route.desc"),
    ("art.mac.notifiers.label", "mac_notifiers", [], "art.mac.notifiers.desc"),
]


class MacArtifactsTab(ArtifactTab):
    """Pestaña de artefactos macOS."""

    def __init__(self, runner: VolatilityRunner, parent: Optional[QWidget] = None) -> None:
        super().__init__(runner, MAC_ARTIFACTS, parent)
