import ctypes
import time

# ===============================
# Windows API 常量
# ===============================
user32 = ctypes.windll.user32

KEYEVENTF_KEYUP = 0x0002
VK_SPACE = 0x20  # 空格虚拟键码

MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_RIGHTDOWN = 0x0008
MOUSEEVENTF_RIGHTUP = 0x0010
MOUSEEVENTF_MIDDLEDOWN = 0x0020
MOUSEEVENTF_MIDDLEUP = 0x0040

# ===============================
# 键盘结构体定义
# ===============================
class KEYBDINPUT(ctypes.Structure):
    _fields_ = [
        ("wVk", ctypes.c_ushort),
        ("wScan", ctypes.c_ushort),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT_KEYBOARD(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("ki", KEYBDINPUT)]

# ===============================
# 鼠标结构体定义
# ===============================
class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT_MOUSE(ctypes.Structure):
    _fields_ = [("type", ctypes.c_ulong), ("mi", MOUSEINPUT)]

# ===============================
# KeyboardAPI
# ===============================
class KeyboardAPI:
    def press_key(self, vk_code):
        user32.keybd_event(vk_code, 0, 0, 0)

    def release_key(self, vk_code):
        user32.keybd_event(vk_code, 0, KEYEVENTF_KEYUP, 0)

    def tap_key(self, vk_code, duration=0.01):
        self.press_key(vk_code)
        if duration > 0:
            time.sleep(duration)
        self.release_key(vk_code)

# ===============================
# MouseAPI
# ===============================
class MouseAPI:
    def __init__(self):
        self.SendInput = ctypes.windll.user32.SendInput

    def click(self, button="left", press_time=0.01):
        extra = ctypes.c_ulong(0)
        button_map = {
            "left": (MOUSEEVENTF_LEFTDOWN, MOUSEEVENTF_LEFTUP),
            "right": (MOUSEEVENTF_RIGHTDOWN, MOUSEEVENTF_RIGHTUP),
            "middle": (MOUSEEVENTF_MIDDLEDOWN, MOUSEEVENTF_MIDDLEUP),
        }
        if button not in button_map:
            raise ValueError(f"Unsupported mouse button: {button}")
        down_flag, up_flag = button_map[button]

        down = MOUSEINPUT(0, 0, 0, down_flag, 0, ctypes.pointer(extra))
        up = MOUSEINPUT(0, 0, 0, up_flag, 0, ctypes.pointer(extra))

        self.SendInput(1, ctypes.byref(INPUT_MOUSE(0, down)), ctypes.sizeof(INPUT_MOUSE))
        time.sleep(press_time)
        self.SendInput(1, ctypes.byref(INPUT_MOUSE(0, up)), ctypes.sizeof(INPUT_MOUSE))
