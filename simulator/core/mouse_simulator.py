from simulator.core.base_simulator import BaseSimulator
from simulator.core.input_api import MouseAPI

class MouseSimulator(BaseSimulator):
    def __init__(self, interval=0.05, press_time=0.01):
        super().__init__(interval)
        self.press_time = press_time
        self.api = MouseAPI()

    def _task(self):
        self.api.click(press_time=self.press_time)
