import ctypes
import time

# Windows API
user32 = ctypes.windll.user32

# 常量
KEYEVENTF_KEYUP = 0x0002
VK_SPACE = 0x20  # 空格虚拟键码

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


# ================
# 测试
# ================
if __name__ == "__main__":
    kb = KeyboardAPI()
    print("测试空格 5 次...")
    for i in range(5):
        kb.tap_key(VK_SPACE, duration=0.05)
        time.sleep(0.2)
