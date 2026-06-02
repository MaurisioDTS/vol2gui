"""Exportación de tablas de resultados a CSV, JSON y HTML."""

from __future__ import annotations

import csv
import html
import json
from datetime import datetime
from typing import List


def export_csv(path: str, headers: List[str], rows: List[List[str]]) -> None:
    with open(path, "w", newline="", encoding="utf-8") as fh:
        writer = csv.writer(fh)
        if headers:
            writer.writerow(headers)
        writer.writerows(rows)


def export_json(path: str, headers: List[str], rows: List[List[str]]) -> None:
    if headers:
        data = [
            {headers[i] if i < len(headers) else f"col{i}": cell for i, cell in enumerate(row)}
            for row in rows
        ]
    else:
        data = [{"col0": "  ".join(row)} for row in rows]
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, ensure_ascii=False, indent=2)


def export_html(path: str, headers: List[str], rows: List[List[str]], title: str = "Resultado") -> None:
    parts: List[str] = [
        "<!DOCTYPE html>",
        "<html lang='es'><head><meta charset='utf-8'>",
        f"<title>{html.escape(title)}</title>",
        "<style>",
        "body{font-family:Segoe UI,Arial,sans-serif;background:#1e1e1e;color:#ddd;margin:24px;}",
        "h1{color:#4ec9b0;font-size:18px;}",
        ".meta{color:#888;font-size:12px;margin-bottom:16px;}",
        "table{border-collapse:collapse;width:100%;}",
        "th,td{border:1px solid #3c3c3c;padding:6px 10px;text-align:left;font-size:13px;}",
        "th{background:#252526;color:#4ec9b0;}",
        "tr:nth-child(even){background:#252526;}",
        "</style></head><body>",
        f"<h1>{html.escape(title)}</h1>",
        f"<div class='meta'>Generado: {datetime.now().isoformat(timespec='seconds')}</div>",
        "<table>",
    ]
    if headers:
        parts.append("<tr>" + "".join(f"<th>{html.escape(str(h))}</th>" for h in headers) + "</tr>")
    for row in rows:
        parts.append("<tr>" + "".join(f"<td>{html.escape(str(c))}</td>" for c in row) + "</tr>")
    parts.append("</table></body></html>")
    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(parts))


def file_filter() -> str:
    """Filtro para QFileDialog con los formatos soportados."""
    return "CSV (*.csv);;JSON (*.json);;HTML (*.html);;Texto (*.txt)"
