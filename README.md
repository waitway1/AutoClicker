# AutoClicker Pro

一款功能丰富的 Windows 自动连点器，支持多种点击模式、范围点击、模拟人类行为等功能。使用 Python + PySide6 开发，界面美观易用。

## 功能特性

- **多种点击模式**：左键、右键、双击、长按
- **可调节 CPS**：1 ~ 100 次/秒，滑块实时调节
- **范围点击**：设定圆形区域，鼠标在区域内随机点击，避免固定位置
- **模拟人类行为**：开启后自动加入随机抖动、微停顿，点击更自然
- **定时器**：支持持续运行、倒计时自动停止、延迟启动三种模式
- **全局快捷键**：自定义开始/暂停、显示/隐藏范围圈、紧急停止的快捷键
- **配置方案**：保存和加载不同的参数方案，快速切换
- **暗色主题**：深色界面，长时间使用不刺眼

## 默认快捷键

| 功能 | 快捷键 |
|------|--------|
| 开始 / 暂停 | F6 |
| 停止 | F8 |

> 快捷键可在程序内自定义修改

## 安装运行

### 方式一：直接运行源码

```bash
# 安装依赖
pip install -r requirements.txt

# 运行程序
python main.py
```

### 方式二：打包成 exe

```bash
# 双击运行 build.bat，或手动执行：
pyinstaller AutoClickerPro.spec
```

打包完成后，exe 文件在 `dist/` 目录中。

## 系统要求

- Windows 10 / 11
- Python 3.9+

## 技术栈

- **PySide6**：Qt for Python，构建桌面界面
- **pynput**：监听全局键盘输入
- **ctypes (SendInput)**：调用 Windows API 实现低延迟点击
- **PyInstaller**：打包为独立 exe

## 项目结构

```
├── main.py                 # 程序入口
├── requirements.txt        # Python 依赖
├── build.bat               # 一键打包脚本
├── core/                   # 核心逻辑
│   ├── click_engine.py     # 点击引擎
│   ├── click_simulator.py  # 人类行为模拟
│   ├── config_manager.py   # 配置管理
│   └── hotkey_manager.py   # 快捷键管理
└── ui/                     # 界面组件
    ├── main_window.py      # 主窗口
    ├── overlay.py          # 范围圈覆盖层
    ├── styles.py           # 暗色主题样式
    └── widgets.py          # 自定义控件
```
