from simulator.core.base_simulator import BaseSimulator
from simulator.core.input_api import KeyboardAPI

VK_SPACE = 0x20  # 虚拟键码

class KeyboardSimulator(BaseSimulator):
    def __init__(self, interval=0.01, press_time=0.005):
        super().__init__(interval)
        self.press_time = press_time
        self.api = KeyboardAPI()

    def _task(self):
        self.api.tap_key(VK_SPACE, duration=self.press_time)
