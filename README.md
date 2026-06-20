# Lester-VER3.0

GTA Online heist hacking minigame macro.

This is Hingdragon417's fork of Lester, based on the original project by JUSTDIE. It keeps the existing heist helpers and adds quality-of-life updates, BruteForce matcher work, and a rebuilt Windows executable.

Special thanks to [RedHeadEmile](https://github.com/RedHeadEmile/GTA-V-Heist-Help) for `Fingerprint Scanner` and `Retro Fingerprint Scanner`.

## What's New In This Fork

- `/` shows a small top-right keybind reminder overlay.
- `F10` BruteForce Matcher now detects the active moving column instead of relying only on a fixed column order.
- BruteForce timing now tracks the falling red letter and predicts when it will hit the blue bar.
- Startup update check asks before updating when a newer GitHub version is available.
- Project cleanup removed generated caches and unused development tools.
- A rebuilt Windows exe is included at `dist/Lester-Ver3.0.exe`.

## Keybinds

- `/` - Show keybind reminder overlay
- `F4` - Exit
- `F5` - Fingerprint Scanner
- `F6` - Keypad Cracker
- `F7` - Retro Fingerprint Scanner
- `F8` - Voltage Hack
- `F9` - Host Number Matcher
- `F10` - BruteForce Matcher

## Setup

### Run The Exe

Download or clone the repository, then run:

```text
dist/Lester-Ver3.0.exe
```

### Run From Source

Python 3.8 is recommended.

```text
pip install -r requirements.txt
python main.py
```

### Rebuild The Exe

```text
pyinstaller --clean --noconfirm Lester-Ver3.0.spec
```

The rebuilt exe will be written to `dist/Lester-Ver3.0.exe`.

## Auto Updates

On startup, Lester checks the latest push on `Hingdragon417/Lester-Ver3.0`.

- If you are running the packaged exe and the repo has a newer `dist/Lester-Ver3.0.exe`, Lester asks before downloading it.
- If you are running from a Git checkout, Lester asks before running `git pull --ff-only origin main`.
- If the update is accepted, Lester updates and restarts itself.
- If GitHub or the network is unavailable, the update check is skipped and the app continues normally.

## Notes

- The app waits for a window named `Grand Theft Auto V` before enabling hotkeys.
- `1920x1080` is recommended. Other resolutions might work, but some matchers depend on screen coordinates.
- On `Keypad Cracker`, press `F6` on the latest pattern.
- The overlay may not appear over exclusive fullscreen games. Borderless/windowed fullscreen is recommended.

## Showcase

[Fingerprint Scanner](https://youtu.be/3I9eYxjDiOk?t=7)

[Keypad Cracker](https://youtu.be/3I9eYxjDiOk?t=44)

[Retro Fingerprint Scanner](https://youtu.be/3I9eYxjDiOk?t=137)

[Voltage Hack](https://youtu.be/3I9eYxjDiOk?t=177)
