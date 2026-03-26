import json
import time
import unittest

from simulator.core.workflow import WorkflowStep, WorkflowTemplate, default_templates, resolve_vk_code
from simulator.core.workflow_simulator import WorkflowSimulator


class WorkflowTests(unittest.TestCase):
    def test_resolve_vk_code_supports_common_keys(self):
        self.assertEqual(resolve_vk_code("space"), 0x20)
        self.assertEqual(resolve_vk_code("A"), 0x41)
        self.assertEqual(resolve_vk_code("f8"), 0x77)
        self.assertIsNone(resolve_vk_code("unknown_key"))

    def test_template_round_trip_json(self):
        template = WorkflowTemplate(
            name="Combo",
            description="demo",
            repeat=False,
            start_delay=1.5,
            cycle_interval=0.25,
            stop_mode="duration",
            stop_value=30,
            steps=[
                WorkflowStep("key_down", "ctrl", duration=0.0),
                WorkflowStep("keyboard", "a", duration=0.1),
                WorkflowStep("key_up", "ctrl", duration=0.0),
                WorkflowStep("delay", "", duration=0.2),
                WorkflowStep("mouse", "right", duration=0.05),
            ],
        ).validate()

        restored = WorkflowTemplate.from_json(template.to_json())

        self.assertEqual(restored.name, "Combo")
        self.assertFalse(restored.repeat)
        self.assertEqual(restored.start_delay, 1.5)
        self.assertEqual(restored.stop_mode, "duration")
        self.assertEqual(restored.stop_value, 30)
        self.assertEqual(len(restored.steps), 5)
        self.assertEqual(restored.steps[0].action_type, "key_down")
        self.assertEqual(restored.steps[1].target, "a")
        self.assertEqual(restored.steps[3].action_type, "delay")
        self.assertEqual(restored.steps[4].target, "right")

    def test_template_validation_rejects_invalid_step(self):
        with self.assertRaises(ValueError):
            WorkflowTemplate(
                name="Broken",
                steps=[WorkflowStep("keyboard", "not_a_key", duration=0.1)],
            ).validate()

    def test_template_validation_rejects_invalid_delay_step(self):
        with self.assertRaises(ValueError):
            WorkflowTemplate(
                name="BrokenDelay",
                steps=[WorkflowStep("delay", "", duration=0.0)],
            ).validate()

    def test_template_validation_rejects_invalid_stop_mode(self):
        with self.assertRaises(ValueError):
            WorkflowTemplate(
                name="BrokenStop",
                stop_mode="unknown",
                steps=[WorkflowStep("keyboard", "a", duration=0.1)],
            ).validate()

    def test_template_validation_requires_stop_value(self):
        with self.assertRaises(ValueError):
            WorkflowTemplate(
                name="BrokenStopValue",
                stop_mode="cycles",
                stop_value=0,
                steps=[WorkflowStep("keyboard", "a", duration=0.1)],
            ).validate()

    def test_default_templates_are_valid(self):
        templates = default_templates()
        self.assertGreaterEqual(len(templates), 9)
        encoded = [json.loads(template.to_json()) for template in templates]
        self.assertEqual(encoded[0]["name"], "鼠标左键连点")

    def test_workflow_simulator_cycle_stop_condition(self):
        template = WorkflowTemplate(
            name="CycleStop",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.0,
            stop_mode="cycles",
            stop_value=2,
            steps=[WorkflowStep("keyboard", "a", duration=0.0)],
        ).validate()
        simulator = WorkflowSimulator(template)
        simulator.keyboard.tap_key = lambda *args, **kwargs: None
        simulator.start()
        time.sleep(0.05)
        self.assertFalse(simulator.is_running())
        self.assertEqual(simulator.completed_cycles, 2)

    def test_legacy_step_shape_still_imports(self):
        template = WorkflowTemplate.from_dict(
            {
                "name": "Legacy",
                "steps": [
                    {"action_type": "keyboard", "target": "a", "hold_time": 0.1, "post_delay": 0.2}
                ],
            }
        )
        self.assertEqual(template.steps[0].duration, 0.1)


if __name__ == "__main__":
    unittest.main()
