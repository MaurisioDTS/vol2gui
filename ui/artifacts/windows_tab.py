"""Artefactos forenses para imágenes Windows."""

from __future__ import annotations

from typing import Optional

from PyQt5.QtWidgets import QWidget

from core.runner import VolatilityRunner
from ui.artifacts.base import ArtifactSpec, ArtifactTab

WINDOWS_ARTIFACTS: list[ArtifactSpec] = [
    ("art.win.hivelist.label", "hivelist", [], "art.win.hivelist.desc"),
    ("art.win.svcscan.label", "svcscan", [], "art.win.svcscan.desc"),
    ("art.win.netscan.label", "netscan", [], "art.win.netscan.desc"),
    ("art.win.cmdline.label", "cmdline", [], "art.win.cmdline.desc"),
    ("art.win.cmdscan.label", "cmdscan", [], "art.win.cmdscan.desc"),
    ("art.win.consoles.label", "consoles", [], "art.win.consoles.desc"),
    ("art.win.dlllist.label", "dlllist", [], "art.win.dlllist.desc"),
    ("art.win.ldrmodules.label", "ldrmodules", [], "art.win.ldrmodules.desc"),
    ("art.win.malfind.label", "malfind", [], "art.win.malfind.desc"),
    ("art.win.hashdump.label", "hashdump", [], "art.win.hashdump.desc"),
    ("art.win.cachedump.label", "cachedump", [], "art.win.cachedump.desc"),
    ("art.win.shimcache.label", "shimcache", [], "art.win.shimcache.desc"),
    ("art.win.userassist.label", "userassist", [], "art.win.userassist.desc"),
    ("art.win.amcache.label", "amcache", [], "art.win.amcache.desc"),
    ("art.win.clipboard.label", "clipboard", [], "art.win.clipboard.desc"),
    ("art.win.mftparser.label", "mftparser", [], "art.win.mftparser.desc"),
    ("art.win.callbacks.label", "callbacks", [], "art.win.callbacks.desc"),
    ("art.win.ssdt.label", "ssdt", [], "art.win.ssdt.desc"),
    ("art.win.modscan.label", "modscan", [], "art.win.modscan.desc"),
]


class WindowsArtifactsTab(ArtifactTab):
    """Pestaña de artefactos Windows."""

    def __init__(self, runner: VolatilityRunner, parent: Optional[QWidget] = None) -> None:
        super().__init__(runner, WINDOWS_ARTIFACTS, parent)
