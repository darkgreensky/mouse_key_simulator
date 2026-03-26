import time

from simulator.core.base_simulator import BaseSimulator
from simulator.core.input_api import KeyboardAPI, MouseAPI
from simulator.core.workflow import WorkflowTemplate, resolve_vk_code


class WorkflowSimulator(BaseSimulator):
    def __init__(self, template: WorkflowTemplate):
        validated = template.validate()
        super().__init__(interval=validated.cycle_interval)
        self.template = validated
        self.keyboard = KeyboardAPI()
        self.mouse = MouseAPI()
        self.completed_cycles = 0
        self.started_at = None

    def _run(self):
        self.started_at = time.time()
        if self.template.start_delay > 0:
            delay_end = self.started_at + self.template.start_delay
            while self._running.is_set() and time.time() < delay_end:
                time.sleep(min(0.05, max(0.0, delay_end - time.time())))

        while self._running.is_set():
            self._task()
            self.completed_cycles += 1
            if self._should_stop():
                self._running.clear()
                break
            if not self.template.repeat:
                self._running.clear()
                break
            if self.interval > 0:
                time.sleep(self.interval)

    def _task(self):
        for step in self.template.steps:
            if not self._running.is_set():
                break
            self._execute_step(step)

    def _execute_step(self, step):
        if step.action_type == "keyboard":
            vk_code = resolve_vk_code(step.target)
            if vk_code is None:
                raise ValueError(f"Unsupported keyboard key: {step.target}")
            self.keyboard.tap_key(vk_code, duration=step.duration)
        elif step.action_type == "mouse":
            self.mouse.click(button=step.target, press_time=step.duration)
        elif step.action_type == "delay":
            time.sleep(step.duration)
        elif step.action_type == "key_down":
            vk_code = resolve_vk_code(step.target)
            if vk_code is None:
                raise ValueError(f"Unsupported keyboard key: {step.target}")
            self.keyboard.press_key(vk_code)
        elif step.action_type == "key_up":
            vk_code = resolve_vk_code(step.target)
            if vk_code is None:
                raise ValueError(f"Unsupported keyboard key: {step.target}")
            self.keyboard.release_key(vk_code)
        else:
            raise ValueError(f"Unsupported action type: {step.action_type}")

    def _should_stop(self):
        if self.template.stop_mode == "manual":
            return False
        if self.template.stop_mode == "duration":
            if self.started_at is None:
                return False
            return (time.time() - self.started_at) >= self.template.stop_value
        if self.template.stop_mode == "cycles":
            return self.completed_cycles >= int(self.template.stop_value)
        return False
