# AutoClicker Pro

[![中文](https://img.shields.io/badge/中文-当前-1677ff)](README.md)
[![English](https://img.shields.io/badge/English-README-111111)](README_en.md)

一款 Windows 自动连点器，支持 CPS 调节、范围点击、倒计时/延迟启动、模拟人类点击和全局快捷键。界面支持 **跟随系统 / 白天 / 黑夜** 三种外观，并支持 **默认 / 中文 / English** 三种语言设置。

## 界面预览

| 白天中文 | 黑夜中文 | English |
| --- | --- | --- |
| <img src="resources/readme/app-light.png" alt="AutoClicker Pro 白天中文界面" width="260"> | <img src="resources/readme/app-dark.png" alt="AutoClicker Pro 黑夜中文界面" width="260"> | <img src="resources/readme/app-english.png" alt="AutoClicker Pro English UI" width="260"> |

## 快速使用

### 1. 选择外观和语言

<img src="resources/readme/tutorial-theme-selector.png" alt="外观和语言选择器" width="620">

标题栏右侧可以切换外观和语言。外观默认 `跟随系统`；语言默认 `默认`，会根据用户系统语言自动选择中文或英文。

### 2. 设置点击方式

<img src="resources/readme/light-tutorial-click-settings.png" alt="点击设置" width="520">

- `模式`：选择左键、右键、双击或长按。
- `CPS`：调整每秒点击次数。
- `间隔`：需要更自然的点击时，可保留最小/最大间隔。
- `开始 (F6)` / `停止 (F8)`：直接控制连点状态。

### 3. 设置点击范围

<img src="resources/readme/light-tutorial-click-range.png" alt="点击范围设置" width="520">

- `半径`：控制随机点击范围大小。
- `显示范围圈`：在屏幕上显示点击区域。
- `编辑位置`：打开后可以拖动范围圈位置。
- `坐标`：也可以直接输入 X / Y 坐标。

### 4. 使用快捷键

<img src="resources/readme/light-tutorial-hotkeys.png" alt="快捷键设置" width="520">

| 功能 | 默认快捷键 |
| --- | --- |
| 开始 / 暂停 | F6 |
| 显示 / 隐藏范围圈 | F7 |
| 紧急停止 | F8 |

快捷键可以在程序内点击对应按钮后重新录制。

## 安装运行

```bash
pip install -r requirements.txt
python main.py
```

## 打包 exe

```bash
pyinstaller AutoClickerPro.spec
```

也可以直接双击运行 `build.bat`。打包完成后，exe 文件会生成在 `dist/` 目录中。

## 系统要求

- Windows 10 / 11
- Python 3.9+

## 技术栈

- **PySide6**：桌面界面
- **pynput**：全局键盘监听
- **ctypes (SendInput)**：Windows 低延迟点击
- **PyInstaller**：打包独立 exe

## 项目结构

```
├── main.py                 # 程序入口
├── README_en.md            # English README
├── requirements.txt        # Python 依赖
├── build.bat               # 一键打包脚本
├── resources/              # README 图片资源
├── core/                   # 核心逻辑
│   ├── click_engine.py     # 点击引擎
│   ├── click_simulator.py  # 人类行为模拟
│   ├── config_manager.py   # 配置管理
│   └── hotkey_manager.py   # 快捷键管理
└── ui/                     # 界面组件
    ├── i18n.py             # 中英文界面文案
    ├── main_window.py      # 主窗口
    ├── overlay.py          # 范围圈覆盖层
    ├── styles.py           # 白天/黑夜主题
    └── widgets.py          # 自定义控件
```
