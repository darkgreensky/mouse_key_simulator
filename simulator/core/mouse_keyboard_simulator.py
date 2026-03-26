from simulator.core.base_simulator import BaseSimulator
from simulator.core.input_api import MouseAPI, KeyboardAPI

VK_SPACE = 0x20  # 虚拟键码

class MouseKeyboardSimulator(BaseSimulator):
    def __init__(self, interval=0.0005, press_time=0.0002):
        """
        interval: 按键间隔（秒）
        press_time: 每次按下持续时间（秒）
        """
        super().__init__(interval=interval)
        self.press_time = press_time
        self.mouse = MouseAPI()
        self.keyboard = KeyboardAPI()

    def _task(self):
        self.keyboard.tap_key(VK_SPACE, duration=self.press_time)
        self.mouse.click(press_time=self.press_time)


