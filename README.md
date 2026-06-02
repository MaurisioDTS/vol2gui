# volatility2gui

simple gui wrapper (pyqt5) for the **volatility 2.6 standalone** binary, aimed
at memory forensics on ram images.

(este readme en ingles porque me lo quiero tomar más en serio)

## features

- **automatic report** when loading an image: md5/sha256 hashes (evidence
  integrity) + `imageinfo` with os/profile detection.
- **processes**: `pslist` (table) and `pstree` (hierarchical tree). double click
  a process to open details (cmdline, dlls, handles).
- **in-memory filesystem explorer**: navigable tree of file paths seen in memory.
  **it does not extract anything automatically**: the analyst chooses what to
  extract and where to dump it using the native os file dialog.
- **os-specific artifacts** (windows / linux / macos): registry, services, network,
  command history, injection/rootkit detection, hashes, etc.
- **search** for strings/patterns in memory with `yarascan`.
- **malware auto-scan**: runs detection plugins in batch and generates an html
  report.
- **audit log** (`audit.log`): every action (plugin run, extraction, export) is
  timestamped for chain-of-custody traceability.

## requirements

- python 3.8+
- pyqt5
- the `volatility` binary (volatility 2.6 standalone) in the project root.

## install

remember, YOU NEED TO volatility2standalone binary from the official repo, go get it.
then rename it just to "volatility" and finally paste it into the project root.

```bash
pip install -r requirements.txt
```
---
problemo my friendo? then just: 

```bash
python3 -m venv vol2gui
source vol2gui/bin/activate
```

now install requirements.


## run

```bash
python3 main.py
```

on startup it asks for the volatility binary path (defaults to `./volatility`),
the ram image to analyze, and optionally a profile. for linux/macos images you
usually need to set the profile manually.

## layout

```text
volatility2gui/
├── volatility           # ULTRA IMPORTANT, GO GET THIS NOW!
├── main.py              # entry point
├── core/                # execution + parsing
│   ├── runner.py        # subprocess wrapper (sync + qthread)
│   ├── parser.py        # volatility 2 text output parsers
│   └── profile.py       # os/profile detection from imageinfo
├── ui/                  # pyqt5 ui
│   ├── main_window.py
│   ├── image_loader.py
│   ├── process_view.py
│   ├── filesystem_view.py
│   ├── theme.py
│   ├── artifacts/       # os-specific artifact tabs
│   └── widgets/         # reusable widgets
└── utils/               # export + audit log
```

## forensics note

volatility reads the image (read-only). file extraction and result export always
write to a location chosen by the analyst, never to the original evidence.

## legal disclaimer

esta herramienta se entrega **TAL Y COMO ESTÁ**. **no me responsabilizo de ninguna evidencia dañada o cadena de custodia rota**. *hubieras estudiado*.