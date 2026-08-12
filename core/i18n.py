"""locales

use example:
    from core.i18n import t
    label = QLabel(t("startup.binary_label"))
    status = t("fs.enumerated", count=42)
"""

from __future__ import annotations

import locale
from typing import Dict, Tuple

DEFAULT_LANG = "es"
SUPPORTED_LANGS: Tuple[str, ...] = ("es", "en")

LANGUAGE_NAMES: Dict[str, str] = {
    "es": "Español",
    "en": "English",
}

_current_lang = DEFAULT_LANG
_TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # ---------------------------------------------------------------- común --
    "common.language": {"es": "Idioma", "en": "Language"},
    "common.error": {"es": "Error", "en": "Error"},
    "common.loading": {"es": "Cargando...", "en": "Loading..."},
    "common.no_output": {"es": "(sin salida)", "en": "(no output)"},
    "common.no_results": {"es": "(sin resultados)", "en": "(no results)"},
    "common.output_col": {"es": "Salida", "en": "Output"},
    "common.none": {"es": "(ninguno)", "en": "(none)"},
    "common.browse": {"es": "Examinar...", "en": "Browse..."},
    "common.error_in_plugin": {"es": "Error en {plugin}", "en": "Error in {plugin}"},
    "common.all_files": {"es": "Todos los archivos (*)", "en": "All files (*)"},
    "common.plugin_output": {"es": "Salida del plugin", "en": "Plugin output"},

    # --------------------------------------------------------------- arranque --
    "app.start_error_title": {"es": "Error al iniciar", "en": "Startup error"},

    "startup.title": {
        "es": "Volatility 2 GUI - Cargar imagen",
        "en": "Volatility 2 GUI - Load image",
    },
    "startup.binary_label": {"es": "Binario Volatility:", "en": "Volatility binary:"},
    "startup.image_label": {"es": "Imagen de RAM:", "en": "RAM image:"},
    "startup.profile_label": {"es": "Perfil (opcional):", "en": "Profile (optional):"},
    "startup.profile_placeholder": {
        "es": "(opcional) perfil manual, p. ej. Win7SP1x64 o LinuxUbuntu...",
        "en": "(optional) manual profile, e.g. Win7SP1x64 or LinuxUbuntu...",
    },
    "startup.hint": {
        "es": (
            "El perfil puede dejarse en «(ninguno)»: se detectará con «imageinfo». "
            "Para Linux/Mac suele ser necesario indicarlo manualmente. Los "
            "perfiles de la carpeta «profiles/» aparecen en este desplegable, "
            "pero sólo se aplican si los eliges."
        ),
        "en": (
            "The profile can be left as \"(none)\": it will be detected with \"imageinfo\". "
            "For Linux/Mac you usually need to set it manually. Profiles from the "
            "\"profiles/\" folder appear in this dropdown, but they are only applied "
            "if you select them."
        ),
    },
    "startup.load_btn": {"es": "Cargar", "en": "Load"},
    "startup.pick_binary": {
        "es": "Seleccionar binario Volatility",
        "en": "Select Volatility binary",
    },
    "startup.pick_image": {"es": "Seleccionar imagen de RAM", "en": "Select RAM image"},
    "startup.image_filter": {
        "es": "Imágenes de memoria (*.raw *.mem *.vmem *.dmp *.lime *.bin *.img *.dump);;Todos los archivos (*)",
        "en": "Memory images (*.raw *.mem *.vmem *.dmp *.lime *.bin *.img *.dump);;All files (*)",
    },
    "startup.invalid_binary_title": {"es": "Binario no válido", "en": "Invalid binary"},
    "startup.invalid_binary_msg": {
        "es": "Selecciona un binario de Volatility válido.",
        "en": "Select a valid Volatility binary.",
    },
    "startup.invalid_image_title": {"es": "Imagen no válida", "en": "Invalid image"},
    "startup.invalid_image_msg": {
        "es": "Selecciona una imagen de RAM válida.",
        "en": "Select a valid RAM image.",
    },

    # ---------------------------------------------------------------- reporte --
    "report.title": {
        "es": "Reporte automático de la imagen",
        "en": "Automatic image report",
    },
    "report.analyzing": {"es": "Analizando imagen...", "en": "Analyzing image..."},
    "report.hash_progress": {"es": "Calculando hashes... %p%", "en": "Computing hashes... %p%"},
    "report.hashes_done": {"es": "Hashes calculados", "en": "Hashes computed"},
    "report.running_imageinfo": {"es": "Ejecutando imageinfo...", "en": "Running imageinfo..."},
    "report.waiting_imageinfo": {
        "es": "Esperando la salida de imageinfo (la detección de SO/perfil aún no ha terminado)...",
        "en": "Waiting for imageinfo output (OS/profile detection is not finished yet)...",
    },
    "report.imageinfo_output": {"es": "Salida de imageinfo:", "en": "imageinfo output:"},
    "report.imageinfo_error": {
        "es": "Error al ejecutar imageinfo:\n{message}",
        "en": "Error running imageinfo:\n{message}",
    },
    "report.active_profile": {"es": "Perfil activo:", "en": "Active profile:"},
    "report.apply_profile": {"es": "Aplicar perfil", "en": "Apply profile"},
    "report.clear_profile": {"es": "Quitar perfil", "en": "Clear profile"},
    "report.summary_image": {"es": "Imagen", "en": "Image"},
    "report.computing": {"es": "(calculando...)", "en": "(computing...)"},

    # ------------------------------------------------------------------ main --
    "main.window_title": {
        "es": "Volatility 2 GUI - Análisis forense de memoria",
        "en": "Volatility 2 GUI - Memory forensics",
    },
    "main.status": {
        "es": "Imagen: {image}  |  Binario: {binary}",
        "en": "Image: {image}  |  Binary: {binary}",
    },
    "main.status_full": {
        "es": "SO: {os}  |  Perfil: {profile}  |  Imagen: {image}",
        "en": "OS: {os}  |  Profile: {profile}  |  Image: {image}",
    },
    "main.no_profile": {"es": "(sin perfil)", "en": "(no profile)"},
    "main.os_not_detected": {
        "es": "SO no detectado automáticamente. Aplica un perfil manual en la pestaña Reporte.",
        "en": "OS not detected automatically. Apply a manual profile in the Report tab.",
    },
    "main.tab_report": {"es": "Reporte", "en": "Report"},
    "main.tab_processes": {"es": "Procesos", "en": "Processes"},
    "main.tab_filesystem": {"es": "Sistema de ficheros", "en": "Filesystem"},
    "main.tab_artifacts": {"es": "Artefactos {os}", "en": "{os} artifacts"},
    "main.tab_search": {"es": "Búsqueda", "en": "Search"},
    "main.tab_autoscan": {"es": "Auto-scan", "en": "Auto-scan"},

    # -------------------------------------------------------------- procesos --
    "process.reload": {"es": "Recargar procesos", "en": "Reload processes"},
    "process.filter_placeholder": {
        "es": "Filtrar por nombre o PID...",
        "en": "Filter by name or PID...",
    },
    "process.col_process": {"es": "Proceso", "en": "Process"},
    "process.hint": {
        "es": "Doble clic en un proceso para ver su detalle (cmdline, DLLs, handles).",
        "en": "Double-click a process to see its detail (cmdline, DLLs, handles).",
    },
    "process.detail_cmdline": {"es": "Línea de comando", "en": "Command line"},
    "process.detail_dlls": {"es": "DLLs", "en": "DLLs"},
    "process.detail_handles": {"es": "Handles", "en": "Handles"},
    "process.detail_args": {"es": "Argumentos", "en": "Arguments"},
    "process.detail_maps": {"es": "Mapas", "en": "Maps"},
    "process.detail_dyld_maps": {"es": "Mapas dyld", "en": "dyld maps"},
    "process.detail_env": {"es": "Entorno", "en": "Environment"},
    "process.detail_window_title": {
        "es": "Detalle de proceso - {name} (PID {pid})",
        "en": "Process detail - {name} (PID {pid})",
    },
    "process.detail_header": {
        "es": "Proceso: {name}   |   PID: {pid}",
        "en": "Process: {name}   |   PID: {pid}",
    },
    "process.detail_error": {"es": "Error: {message}", "en": "Error: {message}"},

    # --------------------------------------------------------- sist. ficheros --
    "fs.enum_btn": {
        "es": "Enumerar ficheros ({plugin})",
        "en": "Enumerate files ({plugin})",
    },
    "fs.filter_placeholder": {
        "es": "Filtrar por nombre o ruta...",
        "en": "Filter by name or path...",
    },
    "fs.preview_btn": {"es": "Visualizar (hex/strings)", "en": "Preview (hex/strings)"},
    "fs.extract_btn": {"es": "Extraer seleccionado...", "en": "Extract selected..."},
    "fs.warn": {
        "es": (
            "Esta vista NO extrae ficheros automáticamente. Selecciona un fichero "
            "y pulsa «Visualizar» para inspeccionarlo (volcado temporal) o «Extraer» "
            "para elegir dónde volcarlo de forma permanente."
        ),
        "en": (
            "This view does NOT extract files automatically. Select a file and click "
            "\"Preview\" to inspect it (temporary dump) or \"Extract\" to choose where "
            "to dump it permanently."
        ),
    },
    "fs.status_initial": {
        "es": "Pulsa «Enumerar ficheros» para construir el árbol.",
        "en": "Click \"Enumerate files\" to build the tree.",
    },
    "fs.col_identifier": {
        "es": "Identificador (offset/inodo)",
        "en": "Identifier (offset/inode)",
    },
    "fs.col_name": {"es": "Nombre", "en": "Name"},
    "fs.col_size": {"es": "Tamaño", "en": "Size"},
    "fs.col_modified": {"es": "Modificado", "en": "Modified"},
    "fs.enumerating": {
        "es": "Enumerando ficheros con {plugin} (puede tardar)...",
        "en": "Enumerating files with {plugin} (may take a while)...",
    },
    "fs.parse_failed": {
        "es": "No se pudo interpretar la salida (usa la pestaña de artefactos).",
        "en": "Could not parse the output (use the artifacts tab).",
    },
    "fs.enumerated": {"es": "{count} ficheros enumerados.", "en": "{count} files enumerated."},
    "fs.ctx_preview": {"es": "Visualizar (hex/strings)", "en": "Preview (hex/strings)"},
    "fs.ctx_extract": {"es": "Extraer este fichero...", "en": "Extract this file..."},
    "fs.not_supported_title": {"es": "No soportado", "en": "Not supported"},
    "fs.extract_not_supported": {
        "es": "La extracción individual de ficheros no está soportada para este SO en Volatility 2.",
        "en": "Individual file extraction is not supported for this OS in Volatility 2.",
    },
    "fs.preview_not_supported": {
        "es": "La visualización individual de ficheros no está soportada para este SO en Volatility 2.",
        "en": "Individual file preview is not supported for this OS in Volatility 2.",
    },
    "fs.choose_dest_dir": {
        "es": "Elegir carpeta de destino para la extracción",
        "en": "Choose destination folder for extraction",
    },
    "fs.save_extracted_as": {
        "es": "Guardar fichero extraído como",
        "en": "Save extracted file as",
    },
    "fs.no_identifier_title": {"es": "Sin identificador", "en": "No identifier"},
    "fs.no_identifier_extract": {
        "es": "Este fichero no tiene offset/inodo para extraer.",
        "en": "This file has no offset/inode to extract.",
    },
    "fs.no_identifier_dump": {
        "es": "Este fichero no tiene offset/inodo para volcar.",
        "en": "This file has no offset/inode to dump.",
    },
    "fs.extracting": {"es": "Extrayendo {name}...", "en": "Extracting {name}..."},
    "fs.extract_done_status": {
        "es": "Extracción finalizada: {name} -> {dest}",
        "en": "Extraction finished: {name} -> {dest}",
    },
    "fs.extract_done_title": {"es": "Extracción completada", "en": "Extraction completed"},
    "fs.extract_done_body": {
        "es": "Fichero: {name}\nDestino: {dest}\n\nSalida del plugin:\n{output}",
        "en": "File: {name}\nDestination: {dest}\n\nPlugin output:\n{output}",
    },
    "fs.default_extract_name": {"es": "extraido.bin", "en": "extracted.bin"},
    "fs.default_preview_name": {"es": "previsualizacion.bin", "en": "preview.bin"},
    "fs.dumping_preview": {
        "es": "Volcando {name} (temporal) para previsualizar...",
        "en": "Dumping {name} (temporary) for preview...",
    },
    "fs.previewing": {
        "es": "Previsualizando {name} (bytes en memoria).",
        "en": "Previewing {name} (bytes in memory).",
    },
    "fs.preview_failed": {"es": "No se pudo previsualizar.", "en": "Could not preview."},

    # ------------------------------------------------------- salida de plugin --
    "plugin.run_btn": {"es": "Ejecutar  {plugin}", "en": "Run  {plugin}"},
    "plugin.filter_placeholder": {"es": "Filtrar resultados...", "en": "Filter results..."},
    "plugin.view_raw": {"es": "Ver raw", "en": "View raw"},
    "plugin.export": {"es": "Exportar", "en": "Export"},
    "plugin.status_initial": {
        "es": "Pulsa «Ejecutar» para lanzar el plugin.",
        "en": "Click \"Run\" to launch the plugin.",
    },
    "plugin.running": {"es": "Ejecutando {plugin}...", "en": "Running {plugin}..."},
    "plugin.rows": {"es": "{plugin}: {count} fila(s).", "en": "{plugin}: {count} row(s)."},
    "plugin.no_table": {
        "es": "{plugin}: sin resultados tabulares (usa «Ver raw»).",
        "en": "{plugin}: no tabular results (use \"View raw\").",
    },
    "plugin.export_title": {"es": "Exportar resultados", "en": "Export results"},
    "plugin.exported_to": {"es": "Exportado a {path}", "en": "Exported to {path}"},
    "plugin.export_error": {"es": "Error al exportar", "en": "Export error"},
    "plugin.raw_title": {"es": "Salida cruda - {plugin}", "en": "Raw output - {plugin}"},

    # ------------------------------------------------------------- búsqueda --
    "search.label": {"es": "Buscar:", "en": "Search:"},
    "search.placeholder": {
        "es": "Cadena de texto a buscar en memoria...",
        "en": "Text string to search in memory...",
    },
    "search.mode_text": {"es": "Texto", "en": "Text"},
    "search.mode_hex": {"es": "Hex", "en": "Hex"},
    "search.mode_yara": {"es": "Regla YARA (-y fichero)", "en": "YARA rule (-y file)"},
    "search.btn": {"es": "Buscar", "en": "Search"},
    "search.cancel_btn": {"es": "Cancelar", "en": "Cancel"},
    "search.hint": {
        "es": (
            "Texto: busca una cadena literal. Hex: bytes en hexadecimal. "
            "Regla YARA: ruta a un fichero .yar."
        ),
        "en": (
            "Text: search a literal string. Hex: bytes in hexadecimal. "
            "YARA rule: path to a .yar file."
        ),
    },
    "search.empty_title": {"es": "Patrón vacío", "en": "Empty pattern"},
    "search.empty_msg": {"es": "Introduce algo que buscar.", "en": "Enter something to search."},
    "search.searching": {"es": "Buscando...", "en": "Searching..."},
    "search.cancelled": {"es": "Búsqueda cancelada.", "en": "Search cancelled."},
    "search.no_matches": {"es": "(sin coincidencias)", "en": "(no matches)"},
    "search.error": {
        "es": "Error en {plugin}:\n{message}",
        "en": "Error in {plugin}:\n{message}",
    },

    # ------------------------------------------------------------- auto-scan --
    "autoscan.title": {
        "es": "Auto-scan de malware y rootkits",
        "en": "Malware and rootkit auto-scan",
    },
    "autoscan.desc": {
        "es": (
            "Ejecuta en lote los plugins de detección de inyección de código, "
            "hooks y artefactos ocultos. Al terminar puedes guardar un informe HTML."
        ),
        "en": (
            "Runs in batch the detection plugins for code injection, hooks and "
            "hidden artifacts. When finished you can save an HTML report."
        ),
    },
    "autoscan.start_btn": {"es": "Iniciar auto-scan", "en": "Start auto-scan"},
    "autoscan.save_report_btn": {"es": "Guardar informe HTML", "en": "Save HTML report"},
    "autoscan.no_plugins_title": {"es": "Sin plugins", "en": "No plugins"},
    "autoscan.no_plugins_msg": {
        "es": "No hay plugins de scan para este SO.",
        "en": "There are no scan plugins for this OS.",
    },
    "autoscan.running": {
        "es": "Ejecutando {plugin} ({label})...",
        "en": "Running {plugin} ({label})...",
    },
    "autoscan.completed": {"es": "Auto-scan completado.", "en": "Auto-scan completed."},
    "autoscan.save_report_title": {
        "es": "Guardar informe de auto-scan",
        "en": "Save auto-scan report",
    },
    "autoscan.report_saved": {"es": "Informe guardado: {path}", "en": "Report saved: {path}"},
    "autoscan.report_html_title": {
        "es": "Informe de auto-scan",
        "en": "Auto-scan report",
    },
    "autoscan.report_html_heading": {
        "es": "Informe de auto-scan de malware",
        "en": "Malware auto-scan report",
    },
    "autoscan.report_image": {"es": "Imagen", "en": "Image"},
    "autoscan.report_profile": {"es": "Perfil", "en": "Profile"},
    "autoscan.report_generated": {"es": "Generado", "en": "Generated"},

    # autoscan plugin labels (windows)
    "autoscan.win.malfind": {
        "es": "Inyección de código (malfind)",
        "en": "Code injection (malfind)",
    },
    "autoscan.win.ldrmodules": {
        "es": "Módulos ocultos (ldrmodules)",
        "en": "Hidden modules (ldrmodules)",
    },
    "autoscan.win.apihooks": {"es": "API hooks (apihooks)", "en": "API hooks (apihooks)"},
    "autoscan.win.ssdt": {"es": "Hooks SSDT (ssdt)", "en": "SSDT hooks (ssdt)"},
    "autoscan.win.callbacks": {"es": "Callbacks del sistema", "en": "System callbacks"},
    "autoscan.win.psxview": {
        "es": "Procesos ocultos (psxview)",
        "en": "Hidden processes (psxview)",
    },
    # autoscan plugin labels (linux)
    "autoscan.linux.syscall": {"es": "Hooks de syscalls", "en": "Syscall hooks"},
    "autoscan.linux.hidden_modules": {"es": "Módulos ocultos", "en": "Hidden modules"},
    "autoscan.linux.creds": {
        "es": "Credenciales sospechosas",
        "en": "Suspicious credentials",
    },
    "autoscan.linux.fop": {"es": "Hooks de fops", "en": "fops hooks"},
    "autoscan.linux.tty": {"es": "TTY hooks", "en": "TTY hooks"},
    # autoscan plugin labels (mac)
    "autoscan.mac.syscall": {"es": "Hooks de syscalls", "en": "Syscall hooks"},
    "autoscan.mac.trustedbsd": {"es": "TrustedBSD", "en": "TrustedBSD"},
    "autoscan.mac.sysctl": {"es": "Hooks de sysctl", "en": "sysctl hooks"},
    "autoscan.mac.trap_table": {"es": "Trap table", "en": "Trap table"},
    "autoscan.mac.notifiers": {"es": "Notifiers", "en": "Notifiers"},

    # ------------------------------------------------------- artefactos win --
    "art.win.hivelist.label": {"es": "Registro (hives)", "en": "Registry (hives)"},
    "art.win.hivelist.desc": {
        "es": "Lista de hives del registro cargados en memoria.",
        "en": "List of registry hives loaded in memory.",
    },
    "art.win.svcscan.label": {"es": "Servicios", "en": "Services"},
    "art.win.svcscan.desc": {
        "es": "Servicios de Windows registrados (svcscan).",
        "en": "Registered Windows services (svcscan).",
    },
    "art.win.netscan.label": {"es": "Conexiones de red", "en": "Network connections"},
    "art.win.netscan.desc": {
        "es": "Conexiones y sockets de red (netscan).",
        "en": "Network connections and sockets (netscan).",
    },
    "art.win.cmdline.label": {"es": "Cmdline", "en": "Cmdline"},
    "art.win.cmdline.desc": {
        "es": "Argumentos de línea de comandos por proceso.",
        "en": "Command-line arguments per process.",
    },
    "art.win.cmdscan.label": {"es": "Historial CMD", "en": "CMD history"},
    "art.win.cmdscan.desc": {
        "es": "Comandos escritos en consolas (cmdscan).",
        "en": "Commands typed in consoles (cmdscan).",
    },
    "art.win.consoles.label": {"es": "Consolas", "en": "Consoles"},
    "art.win.consoles.desc": {
        "es": "Contenido de buffers de consola (consoles).",
        "en": "Console buffer contents (consoles).",
    },
    "art.win.dlllist.label": {"es": "DLLs cargadas", "en": "Loaded DLLs"},
    "art.win.dlllist.desc": {
        "es": "DLLs cargadas por cada proceso.",
        "en": "DLLs loaded by each process.",
    },
    "art.win.ldrmodules.label": {"es": "Módulos (ldrmodules)", "en": "Modules (ldrmodules)"},
    "art.win.ldrmodules.desc": {
        "es": "Compara módulos cargados vs ocultos (rootkits).",
        "en": "Compares loaded vs hidden modules (rootkits).",
    },
    "art.win.malfind.label": {"es": "Malfind (inyección)", "en": "Malfind (injection)"},
    "art.win.malfind.desc": {
        "es": "Detección de código inyectado / shellcode en memoria.",
        "en": "Detection of injected code / shellcode in memory.",
    },
    "art.win.hashdump.label": {"es": "Hashes (hashdump)", "en": "Hashes (hashdump)"},
    "art.win.hashdump.desc": {
        "es": "Hashes NTLM de cuentas locales (SAM).",
        "en": "NTLM hashes of local accounts (SAM).",
    },
    "art.win.cachedump.label": {"es": "Cached hashes", "en": "Cached hashes"},
    "art.win.cachedump.desc": {
        "es": "Hashes de dominio cacheados.",
        "en": "Cached domain hashes.",
    },
    "art.win.shimcache.label": {"es": "Shimcache", "en": "Shimcache"},
    "art.win.shimcache.desc": {
        "es": "Artefactos de ejecución (Application Compatibility Cache).",
        "en": "Execution artifacts (Application Compatibility Cache).",
    },
    "art.win.userassist.label": {"es": "UserAssist", "en": "UserAssist"},
    "art.win.userassist.desc": {
        "es": "Programas ejecutados por el usuario (UserAssist).",
        "en": "Programs run by the user (UserAssist).",
    },
    "art.win.amcache.label": {"es": "Amcache", "en": "Amcache"},
    "art.win.amcache.desc": {
        "es": "Información de ejecución desde Amcache.",
        "en": "Execution information from Amcache.",
    },
    "art.win.clipboard.label": {"es": "Portapapeles", "en": "Clipboard"},
    "art.win.clipboard.desc": {
        "es": "Contenido del portapapeles en memoria.",
        "en": "Clipboard contents in memory.",
    },
    "art.win.mftparser.label": {"es": "MFT (mftparser)", "en": "MFT (mftparser)"},
    "art.win.mftparser.desc": {
        "es": "Tabla maestra de ficheros (MFT) completa.",
        "en": "Full Master File Table (MFT).",
    },
    "art.win.callbacks.label": {"es": "Callbacks", "en": "Callbacks"},
    "art.win.callbacks.desc": {
        "es": "Rutinas de notificación del sistema (posibles hooks).",
        "en": "System notification routines (possible hooks).",
    },
    "art.win.ssdt.label": {"es": "SSDT", "en": "SSDT"},
    "art.win.ssdt.desc": {
        "es": "Tabla de descriptores de servicios del sistema (hooks SSDT).",
        "en": "System Service Descriptor Table (SSDT hooks).",
    },
    "art.win.modscan.label": {"es": "Drivers (modscan)", "en": "Drivers (modscan)"},
    "art.win.modscan.desc": {
        "es": "Módulos del kernel / drivers cargados.",
        "en": "Loaded kernel modules / drivers.",
    },

    # ----------------------------------------------------- artefactos linux --
    "art.linux.bash.label": {"es": "Historial bash", "en": "Bash history"},
    "art.linux.bash.desc": {
        "es": "Historial de comandos bash recuperado de memoria.",
        "en": "Bash command history recovered from memory.",
    },
    "art.linux.psaux.label": {"es": "Procesos (psaux)", "en": "Processes (psaux)"},
    "art.linux.psaux.desc": {
        "es": "Procesos con su línea de comandos completa.",
        "en": "Processes with their full command line.",
    },
    "art.linux.netstat.label": {"es": "Conexiones (netstat)", "en": "Connections (netstat)"},
    "art.linux.netstat.desc": {
        "es": "Conexiones de red activas.",
        "en": "Active network connections.",
    },
    "art.linux.ifconfig.label": {"es": "Interfaces (ifconfig)", "en": "Interfaces (ifconfig)"},
    "art.linux.ifconfig.desc": {
        "es": "Configuración de interfaces de red.",
        "en": "Network interface configuration.",
    },
    "art.linux.lsmod.label": {"es": "Módulos kernel (lsmod)", "en": "Kernel modules (lsmod)"},
    "art.linux.lsmod.desc": {
        "es": "Módulos del kernel cargados.",
        "en": "Loaded kernel modules.",
    },
    "art.linux.check_syscall.label": {"es": "Syscall hooks", "en": "Syscall hooks"},
    "art.linux.check_syscall.desc": {
        "es": "Detección de hooks en la tabla de syscalls (rootkits).",
        "en": "Detection of hooks in the syscall table (rootkits).",
    },
    "art.linux.check_creds.label": {"es": "Creds sospechosas", "en": "Suspicious creds"},
    "art.linux.check_creds.desc": {
        "es": "Procesos que comparten credenciales (posible escalada).",
        "en": "Processes sharing credentials (possible escalation).",
    },
    "art.linux.mount.label": {"es": "Puntos de montaje", "en": "Mount points"},
    "art.linux.mount.desc": {
        "es": "Sistemas de ficheros montados.",
        "en": "Mounted filesystems.",
    },
    "art.linux.dmesg.label": {"es": "dmesg", "en": "dmesg"},
    "art.linux.dmesg.desc": {
        "es": "Buffer de mensajes del kernel (dmesg).",
        "en": "Kernel message buffer (dmesg).",
    },
    "art.linux.lsof.label": {"es": "Ficheros abiertos", "en": "Open files"},
    "art.linux.lsof.desc": {
        "es": "Descriptores de fichero abiertos por proceso.",
        "en": "Open file descriptors per process.",
    },
    "art.linux.proc_maps.label": {"es": "Librerías (proc_maps)", "en": "Libraries (proc_maps)"},
    "art.linux.proc_maps.desc": {
        "es": "Regiones de memoria mapeadas por proceso.",
        "en": "Memory regions mapped per process.",
    },
    "art.linux.hidden_modules.label": {"es": "Módulos ocultos", "en": "Hidden modules"},
    "art.linux.hidden_modules.desc": {
        "es": "Módulos del kernel ocultos (rootkits).",
        "en": "Hidden kernel modules (rootkits).",
    },
    "art.linux.route_cache.label": {"es": "ARP / Route", "en": "ARP / Route"},
    "art.linux.route_cache.desc": {
        "es": "Caché de rutas de red.",
        "en": "Network route cache.",
    },
    "art.linux.psenv.label": {"es": "Variables de entorno", "en": "Environment variables"},
    "art.linux.psenv.desc": {
        "es": "Variables de entorno por proceso.",
        "en": "Environment variables per process.",
    },

    # ------------------------------------------------------- artefactos mac --
    "art.mac.bash.label": {"es": "Historial bash", "en": "Bash history"},
    "art.mac.bash.desc": {
        "es": "Historial de comandos bash en memoria.",
        "en": "Bash command history in memory.",
    },
    "art.mac.netstat.label": {"es": "Conexiones (netstat)", "en": "Connections (netstat)"},
    "art.mac.netstat.desc": {
        "es": "Conexiones de red activas.",
        "en": "Active network connections.",
    },
    "art.mac.ifconfig.label": {"es": "Interfaces (ifconfig)", "en": "Interfaces (ifconfig)"},
    "art.mac.ifconfig.desc": {
        "es": "Configuración de interfaces de red.",
        "en": "Network interface configuration.",
    },
    "art.mac.lsmod.label": {"es": "Extensiones kernel", "en": "Kernel extensions"},
    "art.mac.lsmod.desc": {
        "es": "Extensiones del kernel cargadas (kext).",
        "en": "Loaded kernel extensions (kext).",
    },
    "art.mac.check_syscall.label": {"es": "Syscall hooks", "en": "Syscall hooks"},
    "art.mac.check_syscall.desc": {
        "es": "Detección de hooks en la tabla de syscalls.",
        "en": "Detection of hooks in the syscall table.",
    },
    "art.mac.trustedbsd.label": {"es": "TrustedBSD", "en": "TrustedBSD"},
    "art.mac.trustedbsd.desc": {
        "es": "Hooks de política de seguridad TrustedBSD (rootkits).",
        "en": "TrustedBSD security policy hooks (rootkits).",
    },
    "art.mac.dyld_maps.label": {"es": "Mapas dyld", "en": "dyld maps"},
    "art.mac.dyld_maps.desc": {
        "es": "Librerías dinámicas cargadas por proceso.",
        "en": "Dynamic libraries loaded per process.",
    },
    "art.mac.lsof.label": {"es": "Ficheros abiertos", "en": "Open files"},
    "art.mac.lsof.desc": {
        "es": "Descriptores de fichero abiertos por proceso.",
        "en": "Open file descriptors per process.",
    },
    "art.mac.psenv.label": {"es": "Variables de entorno", "en": "Environment variables"},
    "art.mac.psenv.desc": {
        "es": "Variables de entorno por proceso.",
        "en": "Environment variables per process.",
    },
    "art.mac.list_files.label": {"es": "Lista de ficheros", "en": "File list"},
    "art.mac.list_files.desc": {
        "es": "Ficheros referenciados en el caché de la imagen.",
        "en": "Files referenced in the image cache.",
    },
    "art.mac.arp.label": {"es": "ARP", "en": "ARP"},
    "art.mac.arp.desc": {"es": "Tabla ARP.", "en": "ARP table."},
    "art.mac.route.label": {"es": "Rutas de red", "en": "Network routes"},
    "art.mac.route.desc": {"es": "Tabla de rutas de red.", "en": "Network route table."},
    "art.mac.notifiers.label": {"es": "Notifiers", "en": "Notifiers"},
    "art.mac.notifiers.desc": {
        "es": "Notification callbacks (posibles hooks).",
        "en": "Notification callbacks (possible hooks).",
    },

    # ----------------------------------------------------------- exportación --
    "export.format_label": {"es": "Formato:", "en": "Format:"},
    "export.dest_label": {"es": "Destino:", "en": "Destination:"},
    "export.default_name": {"es": "resultado", "en": "result"},
    "export.rows_to_export": {"es": "{count} fila(s) a exportar.", "en": "{count} row(s) to export."},
    "export.save_as": {"es": "Guardar como", "en": "Save as"},
    "export.empty_dest_title": {"es": "Destino vacío", "en": "Empty destination"},
    "export.empty_dest_msg": {
        "es": "Indica una ruta de destino.",
        "en": "Provide a destination path.",
    },
    "export.html_title": {"es": "Resultado", "en": "Result"},
    "export.html_generated": {"es": "Generado", "en": "Generated"},
    "export.filter": {
        "es": "CSV (*.csv);;JSON (*.json);;HTML (*.html);;Texto (*.txt)",
        "en": "CSV (*.csv);;JSON (*.json);;HTML (*.html);;Text (*.txt)",
    },

    # ------------------------------------------------------------ hex viewer --
    "hex.no_content": {"es": "Sin contenido", "en": "No content"},
    "hex.view_label": {"es": "Vista:", "en": "View:"},
    "hex.mode_hex": {"es": "Hexadecimal", "en": "Hexadecimal"},
    "hex.mode_strings": {"es": "Texto (strings)", "en": "Text (strings)"},
    "hex.mode_both": {"es": "Ambos", "en": "Both"},
    "hex.no_name": {"es": "(sin nombre)", "en": "(no name)"},
    "hex.bytes_shown": {
        "es": "{name}  -  {size} bytes mostrados{suffix}",
        "en": "{name}  -  {size} bytes shown{suffix}",
    },
    "hex.truncated": {"es": " (truncado)", "en": " (truncated)"},
    "hex.read_error": {"es": "Error al leer: {error}", "en": "Read error: {error}"},
    "hex.no_readable_dump": {
        "es": "El volcado no produjo un fichero legible.",
        "en": "The dump did not produce a readable file.",
    },
    "hex.dump_read_error": {
        "es": "No se pudo leer el fichero volcado: {error}",
        "en": "Could not read the dumped file: {error}",
    },
    "hex.empty": {"es": "(vacío)", "en": "(empty)"},
    "hex.no_printable": {
        "es": "(sin cadenas imprimibles)",
        "en": "(no printable strings)",
    },
    "hex.section_hex": {"es": "=== HEXADECIMAL ===", "en": "=== HEXADECIMAL ==="},
    "hex.section_strings": {
        "es": "=== CADENAS (strings) ===",
        "en": "=== STRINGS ===",
    },

    # ---------------------------------------------------------------- perfil --
    "os.windows": {"es": "Windows", "en": "Windows"},
    "os.linux": {"es": "Linux", "en": "Linux"},
    "os.mac": {"es": "Mac", "en": "Mac"},
    "os.unknown": {"es": "Desconocido", "en": "Unknown"},
    "profile.os_detected": {
        "es": "Sistema operativo detectado: {os}",
        "en": "Detected operating system: {os}",
    },
    "profile.suggested": {"es": "Perfiles sugeridos: {profiles}", "en": "Suggested profiles: {profiles}"},
    "profile.selected": {"es": "Perfil seleccionado: {profile}", "en": "Selected profile: {profile}"},
    "profile.none_applied": {
        "es": "Ningún perfil aplicado.",
        "en": "No profile applied.",
    },
    "profile.none_suggested": {
        "es": "Sin perfil sugerido (puede requerir selección manual).",
        "en": "No suggested profile (manual selection may be required).",
    },

    # ---------------------------------------------------------------- runner --
    "runner.binary_not_found": {
        "es": "No se encontró el binario: {path}",
        "en": "Binary not found: {path}",
    },
    "runner.cannot_run": {
        "es": "No se pudo ejecutar el binario: {error}",
        "en": "Could not run the binary: {error}",
    },
    "runner.timeout": {
        "es": "El plugin '{plugin}' superó el tiempo límite ({timeout}s).",
        "en": "Plugin '{plugin}' exceeded the time limit ({timeout}s).",
    },
    "runner.unexpected": {
        "es": "Error inesperado: {error}",
        "en": "Unexpected error: {error}",
    },
}


# --------------------------------------------------------------------- API ----
def supported_languages() -> Tuple[str, ...]:
    """Códigos de idioma soportados."""
    return SUPPORTED_LANGS


def language_name(lang: str) -> str:
    """Nombre legible (en su propio idioma) de un código de idioma."""
    return LANGUAGE_NAMES.get(lang, lang)


def detect_system_language() -> str:
    """Detecta el idioma del sistema; devuelve ``es`` o ``en``.

    Si el sistema no usa un idioma soportado, cae a ``DEFAULT_LANG``.
    """
    try:
        code, _enc = locale.getdefaultlocale()
    except (ValueError, TypeError):
        code = None
    if code:
        prefix = code.split("_", 1)[0].lower()
        if prefix in SUPPORTED_LANGS:
            return prefix
    return DEFAULT_LANG


def set_language(lang: str) -> None:
    """Fija el idioma activo del proceso (si está soportado)."""
    global _current_lang
    if lang in SUPPORTED_LANGS:
        _current_lang = lang


def get_language() -> str:
    """Idioma activo actual."""
    return _current_lang

# important settings key
_SETTINGS_KEY = "ui/language"


def load_saved_language() -> str:
    """Idioma persistido en sesiones previas; si no hay, el del sistema.

    La importación de ``QSettings`` es diferida para no exigir PyQt5 cuando el
    módulo se usa fuera de la interfaz (por ejemplo en pruebas).
    """
    try:
        from PyQt5.QtCore import QSettings
    except ImportError:
        return detect_system_language()
    saved = QSettings("vol2gui", "vol2gui").value(_SETTINGS_KEY, "")
    if isinstance(saved, str) and saved in SUPPORTED_LANGS:
        return saved
    return detect_system_language()


def save_language(lang: str) -> None:
    """Persiste el idioma elegido para la próxima sesión."""
    if lang not in SUPPORTED_LANGS:
        return
    try:
        from PyQt5.QtCore import QSettings
    except ImportError:
        return
    QSettings("vol2gui", "vol2gui").setValue(_SETTINGS_KEY, lang)


def init_language() -> str:
    """Carga y fija el idioma inicial (persistido o del sistema). Lo devuelve."""
    lang = load_saved_language()
    set_language(lang)
    return lang


def t(key: str, **kwargs) -> str:
    """Traduce ``key`` al idioma activo, rellenando marcadores ``{...}``.

    Hace *fallback* al español y, si la clave no existe, devuelve la propia
    clave (útil para detectar traducciones que falten durante el desarrollo).
    """
    entry = _TRANSLATIONS.get(key)
    if entry is None:
        return key.format(**kwargs) if kwargs else key
    text = entry.get(_current_lang) or entry.get(DEFAULT_LANG) or key
    if kwargs:
        try:
            return text.format(**kwargs)
        except (KeyError, IndexError):
            return text
    return text
