# profiles

drop your **volatility 2 custom profiles** here (`.zip` files) and the gui will
pick them up automatically.

## how it works

- on startup the app launches volatility with `--plugins=profiles`, so every
  profile in this folder becomes usable for the analysis.
- the real profile names are read from `volatility --info` and added to the
  profile dropdown (both in the startup dialog and in the "Reporte" tab), so you
  can select them for future investigations without typing them by hand.
- only linux/macos profiles are listed in the dropdown (windows ships hundreds
  of built-in profiles, so those are not duplicated here).

## getting profiles

linux/macos profiles are not shipped with volatility. you build them yourself
from the target kernel (with `dwarfdump` + the kernel `System.map`) or grab a
prebuilt one. once you have the `.zip`, just copy it into this folder.

```text
profiles/
├── MountainLion_10.8.1_AMD.zip
├── Ubuntu1804x64.zip
└── ...
```

no need to rename anything: volatility derives the profile name from the
archive contents, and the app reads it back from `--info`.
