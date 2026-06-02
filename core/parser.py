"""Parsers de la salida de texto de Volatility 2.x.

La mayoría de los plugins de Volatility 2 imprimen una tabla con una fila de
cabecera seguida de una fila de guiones que indica el ancho de cada columna,
por ejemplo::

    Offset(V)   Name        PID    PPID
    ----------  ----------  -----  -----
    0x12345678  System      4      0

A partir de la fila de guiones se pueden recortar las columnas con precisión.
Cuando no hay fila de guiones, se recurre a un parseo por espacios.
"""

from __future__ import annotations

import re
from typing import Dict, List, Tuple

# Fila compuesta sólo por guiones y espacios (delimita anchos de columna).
_DASH_ROW = re.compile(r"^[\s-]*-{2,}[\s-]*$")


def _column_spans(dash_line: str) -> List[Tuple[int, int]]:
    """Devuelve los rangos (inicio, fin) de cada columna a partir de guiones."""
    spans: List[Tuple[int, int]] = []
    for match in re.finditer(r"-+", dash_line):
        spans.append((match.start(), match.end()))
    return spans


def _slice_row(line: str, spans: List[Tuple[int, int]]) -> List[str]:
    """Recorta una línea según los rangos de columnas.

    La última columna se extiende hasta el final de la línea para no truncar
    valores largos (rutas, líneas de comando, etc.).
    """
    cells: List[str] = []
    for idx, (start, end) in enumerate(spans):
        if idx == len(spans) - 1:
            cells.append(line[start:].strip())
        else:
            # Extiende hasta el inicio de la siguiente columna para capturar
            # valores que se desbordan ligeramente del ancho del guion.
            next_start = spans[idx + 1][0]
            cells.append(line[start:next_start].strip())
    return cells


def parse_table(output: str) -> Tuple[List[str], List[List[str]]]:
    """Parsea una salida tabular genérica de Volatility 2.

    Devuelve ``(cabeceras, filas)``. Si no se reconoce el formato tabular,
    devuelve cabeceras vacías y cada línea como una fila de una sola celda.
    """
    lines = [ln.rstrip("\n") for ln in output.splitlines()]
    # Descarta líneas de banner/avisos típicas de Volatility.
    cleaned = [
        ln
        for ln in lines
        if ln.strip()
        and not ln.startswith("Volatility Foundation")
    ]
    if not cleaned:
        return [], []

    # Busca la fila de guiones; la cabecera es la línea inmediatamente anterior.
    dash_idx = None
    for i, ln in enumerate(cleaned):
        if _DASH_ROW.match(ln) and "-" * 2 in ln:
            dash_idx = i
            break

    if dash_idx is not None and dash_idx >= 1:
        spans = _column_spans(cleaned[dash_idx])
        header = _slice_row(cleaned[dash_idx - 1], spans)
        rows: List[List[str]] = []
        for ln in cleaned[dash_idx + 1:]:
            if _DASH_ROW.match(ln):
                continue
            if not ln.strip():
                continue
            rows.append(_slice_row(ln, spans))
        return header, rows

    # Fallback: intenta separar la cabecera por 2+ espacios.
    header = re.split(r"\s{2,}", cleaned[0].strip())
    if len(header) > 1:
        rows = []
        for ln in cleaned[1:]:
            if _DASH_ROW.match(ln):
                continue
            rows.append(re.split(r"\s{2,}", ln.strip()))
        return header, rows

    # Sin estructura reconocible: una columna por línea.
    return [], [[ln] for ln in cleaned]


def parse_imageinfo(output: str) -> Dict[str, str]:
    """Parsea la salida de ``imageinfo`` en un diccionario clave -> valor."""
    info: Dict[str, str] = {}
    for line in output.splitlines():
        if ":" not in line:
            continue
        key, _, value = line.partition(":")
        key = key.strip()
        value = value.strip()
        if key and value:
            info[key] = value
    return info


def parse_pstree(output: str) -> List[Dict]:
    """Parsea ``pstree`` preservando la jerarquía padre/hijo.

    Volatility indica la profundidad con puntos al inicio del nombre, p. ej.
    ``. System`` o ``.. smss.exe``. Devuelve una lista de nodos con campos
    ``name``, ``pid``, ``ppid``, ``depth`` en orden de aparición.
    """
    header, rows = parse_table(output)
    if not header:
        return []

    # Localiza índices de columnas relevantes de forma tolerante.
    def find_col(*candidates: str) -> int:
        for cand in candidates:
            for idx, col in enumerate(header):
                if cand.lower() in col.lower():
                    return idx
        return -1

    name_idx = find_col("Name")
    pid_idx = find_col("Pid", "PID")
    ppid_idx = find_col("PPid", "PPID")

    nodes: List[Dict] = []
    for row in rows:
        if name_idx < 0 or name_idx >= len(row):
            continue
        raw_name = row[name_idx]
        depth = 0
        stripped = raw_name
        # Cuenta los puntos/espacios iniciales que marcan profundidad.
        while stripped.startswith((".", " ")):
            if stripped.startswith("."):
                depth += 1
            stripped = stripped[1:]
        nodes.append(
            {
                "name": stripped.strip(),
                "pid": row[pid_idx].strip() if 0 <= pid_idx < len(row) else "",
                "ppid": row[ppid_idx].strip() if 0 <= ppid_idx < len(row) else "",
                "depth": depth,
                "raw": row,
            }
        )
    return nodes


def parse_mftparser(output: str) -> List[Dict]:
    """Extrae rutas de ficheros de la salida de ``mftparser``.

    ``mftparser`` produce bloques por entrada MFT. Las rutas de fichero
    aparecen tras campos como ``$FILE_NAME``. Esta función recoge cualquier
    ruta plausible para alimentar el árbol del explorador de ficheros.
    """
    entries: List[Dict] = []
    current_record = None
    for line in output.splitlines():
        stripped = line.strip()
        if stripped.startswith("MFT entry found at offset"):
            current_record = stripped.split("offset")[-1].strip()
            continue
        # Las líneas de $FILE_NAME suelen terminar con la ruta del fichero.
        if "FILE_NAME" in line or re.search(r"[A-Za-z]:?\\|/", line):
            path = _extract_path_from_mft_line(line)
            if path:
                entries.append({"path": path, "record": current_record, "raw": line})
    return entries


def _extract_path_from_mft_line(line: str) -> str:
    """Heurística para extraer una ruta de fichero de una línea de mftparser."""
    # Busca rutas tipo Windows (\Users\...\file.ext) al final de la línea.
    match = re.search(r"((?:[A-Za-z]:)?\\[^\t]+)$", line)
    if match:
        return match.group(1).strip()
    return ""
