# mouse_key_simulator

pip install pyqt5 pyautogui keyboard pynput -i https://pypi.tuna.tsinghua.edu.cn/simple

python -m simulator.main

Features:
- Build a custom workflow with multiple keyboard or mouse steps
- Control each step's hold time and delay
- Export or import JSON templates for reusable automation flows
- Toggle the workflow with the UI button or `F8`

内置预设:
- 鼠标左键连点
- 空格连按
- 空格加左键
- WASD 巡环
- QWER 技能轮播
- F 键交互
- 右键瞄准加左键射击
- 方向键巡逻
- 数字键 1-5 轮换
- F1-F4 功能测试

图标:
- 程序运行时会自动加载 `assets/mouse_key_simulator.ico`
- 打包后的 exe 也会使用同一个图标

Windows 打包:
- 安装打包工具: `.\\.venv\\Scripts\\pip install pyinstaller`
- 执行打包脚本: `powershell -ExecutionPolicy Bypass -File .\\build_windows.ps1`
- 打包结果默认在 `dist\\MouseKeySimulator.exe`
