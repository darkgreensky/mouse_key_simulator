# simulator/core/base_simulator.py
import threading
import time


class BaseSimulator:
    def __init__(self, interval=1.0):
        self.interval = interval
        self._running = threading.Event()
        self._thread = None

    def start(self):
        if not self._running.is_set():
            self._running.set()
            self._thread = threading.Thread(target=self._run, daemon=True)
            self._thread.start()

    def stop(self):
        self._running.clear()
        if self._thread and self._thread.is_alive():
            self._thread.join(timeout=1.0)  # ✅ 多等一点，确保退出干净

    def _run(self):
        while self._running.is_set():
            self._task()
            time.sleep(self.interval)

    def is_running(self):
        return self._running.is_set()

    def _task(self):
        raise NotImplementedError
