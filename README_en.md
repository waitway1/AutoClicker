# AutoClicker Pro

[![中文](https://img.shields.io/badge/中文-README-1677ff)](README.md)
[![English](https://img.shields.io/badge/English-Current-111111)](README_en.md)

AutoClicker Pro is a Windows auto clicker with CPS control, random range clicking, countdown/delayed start, human-like clicking, and global hotkeys. The interface supports **System / Light / Dark** appearance modes and **Default / 中文 / English** language modes.

## Preview

| Light Chinese | Dark Chinese | English |
| --- | --- | --- |
| <img src="resources/readme/app-light.png" alt="AutoClicker Pro light Chinese UI" width="260"> | <img src="resources/readme/app-dark.png" alt="AutoClicker Pro dark Chinese UI" width="260"> | <img src="resources/readme/app-english.png" alt="AutoClicker Pro English UI" width="260"> |

## Quick Guide

### 1. Choose Appearance And Language

<img src="resources/readme/tutorial-theme-selector.png" alt="Appearance and language selector" width="620">

Use the controls in the title bar to switch appearance and language. Appearance defaults to `System`; language defaults to `Default`, which follows the user's system language.

### 2. Configure Clicks

<img src="resources/readme/light-tutorial-click-settings.png" alt="Click settings" width="520">

- `Mode`: choose left click, right click, double click, or hold.
- `CPS`: adjust clicks per second.
- `Interval`: keep min/max intervals when you want more natural clicks.
- `Start (F6)` / `Stop (F8)`: control the clicker directly.

### 3. Configure Click Range

<img src="resources/readme/light-tutorial-click-range.png" alt="Click range settings" width="520">

- `Radius`: controls the random click area size.
- `Show circle`: displays the click area on screen.
- `Edit position`: allows dragging the range circle.
- `Position`: enter X / Y coordinates directly.

### 4. Use Hotkeys

<img src="resources/readme/light-tutorial-hotkeys.png" alt="Hotkey settings" width="520">

| Action | Default hotkey |
| --- | --- |
| Start / Pause | F6 |
| Show / Hide circle | F7 |
| Emergency stop | F8 |

Click a hotkey button in the app to record a new key.

## Run From Source

```bash
pip install -r requirements.txt
python main.py
```

## Build Exe

```bash
pyinstaller AutoClickerPro.spec
```

You can also run `build.bat`. The built executable is generated under `dist/`.

## Requirements

- Windows 10 / 11
- Python 3.9+

## Tech Stack

- **PySide6**: desktop UI
- **pynput**: global keyboard listener
- **ctypes (SendInput)**: low-latency Windows clicks
- **PyInstaller**: standalone exe packaging

## Project Structure

```
├── main.py                 # App entry
├── README_en.md            # English README
├── requirements.txt        # Python dependencies
├── build.bat               # One-click build script
├── resources/              # README image assets
├── core/                   # Core logic
│   ├── click_engine.py     # Click engine
│   ├── click_simulator.py  # Human-like behavior
│   ├── config_manager.py   # Config management
│   └── hotkey_manager.py   # Hotkey management
└── ui/                     # UI components
    ├── i18n.py             # Chinese/English UI text
    ├── main_window.py      # Main window
    ├── overlay.py          # Range circle overlay
    ├── styles.py           # Light/dark themes
    └── widgets.py          # Custom widgets
```
