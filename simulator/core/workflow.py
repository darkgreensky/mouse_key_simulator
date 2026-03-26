import json
from dataclasses import asdict, dataclass
from typing import List, Optional


VK_CODE_MAP = {
    "backspace": 0x08,
    "tab": 0x09,
    "clear": 0x0C,
    "enter": 0x0D,
    "shift": 0x10,
    "ctrl": 0x11,
    "alt": 0x12,
    "pause": 0x13,
    "capslock": 0x14,
    "ime_kana": 0x15,
    "ime_hangul": 0x15,
    "ime_junja": 0x17,
    "ime_final": 0x18,
    "ime_hanja": 0x19,
    "ime_kanji": 0x19,
    "esc": 0x1B,
    "ime_convert": 0x1C,
    "ime_nonconvert": 0x1D,
    "ime_accept": 0x1E,
    "ime_modechange": 0x1F,
    "space": 0x20,
    "pageup": 0x21,
    "pagedown": 0x22,
    "end": 0x23,
    "home": 0x24,
    "left": 0x25,
    "up": 0x26,
    "right": 0x27,
    "down": 0x28,
    "select": 0x29,
    "print": 0x2A,
    "execute": 0x2B,
    "printscreen": 0x2C,
    "insert": 0x2D,
    "delete": 0x2E,
    "help": 0x2F,
    "0": 0x30,
    "1": 0x31,
    "2": 0x32,
    "3": 0x33,
    "4": 0x34,
    "5": 0x35,
    "6": 0x36,
    "7": 0x37,
    "8": 0x38,
    "9": 0x39,
    "a": 0x41,
    "b": 0x42,
    "c": 0x43,
    "d": 0x44,
    "e": 0x45,
    "f": 0x46,
    "g": 0x47,
    "h": 0x48,
    "i": 0x49,
    "j": 0x4A,
    "k": 0x4B,
    "l": 0x4C,
    "m": 0x4D,
    "n": 0x4E,
    "o": 0x4F,
    "p": 0x50,
    "q": 0x51,
    "r": 0x52,
    "s": 0x53,
    "t": 0x54,
    "u": 0x55,
    "v": 0x56,
    "w": 0x57,
    "x": 0x58,
    "y": 0x59,
    "z": 0x5A,
    "left_win": 0x5B,
    "right_win": 0x5C,
    "apps": 0x5D,
    "sleep": 0x5F,
    "numpad0": 0x60,
    "numpad1": 0x61,
    "numpad2": 0x62,
    "numpad3": 0x63,
    "numpad4": 0x64,
    "numpad5": 0x65,
    "numpad6": 0x66,
    "numpad7": 0x67,
    "numpad8": 0x68,
    "numpad9": 0x69,
    "multiply": 0x6A,
    "add": 0x6B,
    "separator": 0x6C,
    "subtract": 0x6D,
    "decimal": 0x6E,
    "divide": 0x6F,
    "f1": 0x70,
    "f2": 0x71,
    "f3": 0x72,
    "f4": 0x73,
    "f5": 0x74,
    "f6": 0x75,
    "f7": 0x76,
    "f8": 0x77,
    "f9": 0x78,
    "f10": 0x79,
    "f11": 0x7A,
    "f12": 0x7B,
    "f13": 0x7C,
    "f14": 0x7D,
    "f15": 0x7E,
    "f16": 0x7F,
    "f17": 0x80,
    "f18": 0x81,
    "f19": 0x82,
    "f20": 0x83,
    "f21": 0x84,
    "f22": 0x85,
    "f23": 0x86,
    "f24": 0x87,
    "numlock": 0x90,
    "scrolllock": 0x91,
    ";": 0xBA,
    "=": 0xBB,
    ",": 0xBC,
    "-": 0xBD,
    ".": 0xBE,
    "/": 0xBF,
    "`": 0xC0,
    "[": 0xDB,
    "\\": 0xDC,
    "]": 0xDD,
    "'": 0xDE,
}

MOUSE_BUTTONS = {"left", "right", "middle"}
ACTION_TYPES = {"keyboard", "mouse"}


@dataclass
class WorkflowStep:
    action_type: str
    target: str
    hold_time: float = 0.05
    post_delay: float = 0.1

    def normalized(self) -> "WorkflowStep":
        return WorkflowStep(
            action_type=self.action_type.strip().lower(),
            target=self.target.strip().lower(),
            hold_time=max(0.0, float(self.hold_time)),
            post_delay=max(0.0, float(self.post_delay)),
        )

    def validate(self) -> "WorkflowStep":
        step = self.normalized()
        if step.action_type not in ACTION_TYPES:
            raise ValueError(f"Unsupported action type: {self.action_type}")
        if step.action_type == "keyboard" and resolve_vk_code(step.target) is None:
            raise ValueError(f"Unsupported keyboard key: {self.target}")
        if step.action_type == "mouse" and step.target not in MOUSE_BUTTONS:
            raise ValueError(f"Unsupported mouse button: {self.target}")
        return step


@dataclass
class WorkflowTemplate:
    name: str = "Custom Template"
    description: str = ""
    repeat: bool = True
    start_delay: float = 0.0
    cycle_interval: float = 0.0
    stop_mode: str = "manual"
    stop_value: float = 0.0
    steps: Optional[List[WorkflowStep]] = None

    def validate(self) -> "WorkflowTemplate":
        normalized_steps = [step.validate() for step in (self.steps or [])]
        if not normalized_steps:
            raise ValueError("Template must contain at least one workflow step")
        stop_mode = (self.stop_mode or "manual").strip().lower()
        if stop_mode not in {"manual", "duration", "cycles"}:
            raise ValueError(f"Unsupported stop mode: {self.stop_mode}")
        stop_value = max(0.0, float(self.stop_value))
        if stop_mode in {"duration", "cycles"} and stop_value <= 0:
            raise ValueError("Stop value must be greater than 0 for the selected stop mode")
        return WorkflowTemplate(
            name=(self.name or "Custom Template").strip(),
            description=(self.description or "").strip(),
            repeat=bool(self.repeat),
            start_delay=max(0.0, float(self.start_delay)),
            cycle_interval=max(0.0, float(self.cycle_interval)),
            stop_mode=stop_mode,
            stop_value=stop_value,
            steps=normalized_steps,
        )

    def to_dict(self) -> dict:
        template = self.validate()
        return {
            "name": template.name,
            "description": template.description,
            "repeat": template.repeat,
            "start_delay": template.start_delay,
            "cycle_interval": template.cycle_interval,
            "stop_mode": template.stop_mode,
            "stop_value": template.stop_value,
            "steps": [asdict(step) for step in template.steps],
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=2, ensure_ascii=False)

    @classmethod
    def from_dict(cls, data: dict) -> "WorkflowTemplate":
        steps = [WorkflowStep(**step) for step in data.get("steps", [])]
        return cls(
            name=data.get("name", "Custom Template"),
            description=data.get("description", ""),
            repeat=data.get("repeat", True),
            start_delay=data.get("start_delay", 0.0),
            cycle_interval=data.get("cycle_interval", 0.0),
            stop_mode=data.get("stop_mode", "manual"),
            stop_value=data.get("stop_value", 0.0),
            steps=steps,
        ).validate()

    @classmethod
    def from_json(cls, text: str) -> "WorkflowTemplate":
        return cls.from_dict(json.loads(text))


def resolve_vk_code(key_name: str) -> Optional[int]:
    if key_name is None:
        return None
    return VK_CODE_MAP.get(str(key_name).strip().lower())


def default_templates() -> List[WorkflowTemplate]:
    return [
        WorkflowTemplate(
            name="鼠标左键连点",
            description="持续点击鼠标左键，适合基础连点场景。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.0,
            stop_mode="manual",
            stop_value=0.0,
            steps=[WorkflowStep("mouse", "left", hold_time=0.01, post_delay=0.0)],
        ).validate(),
        WorkflowTemplate(
            name="空格连按",
            description="持续按下空格键。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.0,
            stop_mode="manual",
            stop_value=0.0,
            steps=[WorkflowStep("keyboard", "space", hold_time=0.005, post_delay=0.0)],
        ).validate(),
        WorkflowTemplate(
            name="空格加左键",
            description="先按空格，再点击鼠标左键。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.0,
            stop_mode="manual",
            stop_value=0.0,
            steps=[
                WorkflowStep("keyboard", "space", hold_time=0.005, post_delay=0.0),
                WorkflowStep("mouse", "left", hold_time=0.005, post_delay=0.0),
            ],
        ).validate(),
        WorkflowTemplate(
            name="WASD 巡环",
            description="依次按下 W、A、S、D，适合基础移动测试。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.2,
            stop_mode="manual",
            stop_value=0.0,
            steps=[
                WorkflowStep("keyboard", "w", hold_time=0.05, post_delay=0.05),
                WorkflowStep("keyboard", "a", hold_time=0.05, post_delay=0.05),
                WorkflowStep("keyboard", "s", hold_time=0.05, post_delay=0.05),
                WorkflowStep("keyboard", "d", hold_time=0.05, post_delay=0.05),
            ],
        ).validate(),
        WorkflowTemplate(
            name="QWER 技能轮播",
            description="依次释放 Q、W、E、R 技能键。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.3,
            stop_mode="manual",
            stop_value=0.0,
            steps=[
                WorkflowStep("keyboard", "q", hold_time=0.03, post_delay=0.08),
                WorkflowStep("keyboard", "w", hold_time=0.03, post_delay=0.08),
                WorkflowStep("keyboard", "e", hold_time=0.03, post_delay=0.08),
                WorkflowStep("keyboard", "r", hold_time=0.03, post_delay=0.08),
            ],
        ).validate(),
        WorkflowTemplate(
            name="F 键交互",
            description="持续触发 F 键，适合拾取或交互。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.12,
            stop_mode="manual",
            stop_value=0.0,
            steps=[WorkflowStep("keyboard", "f", hold_time=0.03, post_delay=0.0)],
        ).validate(),
        WorkflowTemplate(
            name="右键瞄准加左键射击",
            description="先点右键再点左键，适合双键联动场景。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.15,
            stop_mode="manual",
            stop_value=0.0,
            steps=[
                WorkflowStep("mouse", "right", hold_time=0.02, post_delay=0.03),
                WorkflowStep("mouse", "left", hold_time=0.02, post_delay=0.0),
            ],
        ).validate(),
        WorkflowTemplate(
            name="方向键巡逻",
            description="依次按上右下左方向键。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.2,
            stop_mode="manual",
            stop_value=0.0,
            steps=[
                WorkflowStep("keyboard", "up", hold_time=0.04, post_delay=0.05),
                WorkflowStep("keyboard", "right", hold_time=0.04, post_delay=0.05),
                WorkflowStep("keyboard", "down", hold_time=0.04, post_delay=0.05),
                WorkflowStep("keyboard", "left", hold_time=0.04, post_delay=0.05),
            ],
        ).validate(),
        WorkflowTemplate(
            name="数字键 1-5 轮换",
            description="依次按下 1 到 5，适合技能栏测试。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.35,
            stop_mode="manual",
            stop_value=0.0,
            steps=[
                WorkflowStep("keyboard", "1", hold_time=0.03, post_delay=0.05),
                WorkflowStep("keyboard", "2", hold_time=0.03, post_delay=0.05),
                WorkflowStep("keyboard", "3", hold_time=0.03, post_delay=0.05),
                WorkflowStep("keyboard", "4", hold_time=0.03, post_delay=0.05),
                WorkflowStep("keyboard", "5", hold_time=0.03, post_delay=0.05),
            ],
        ).validate(),
        WorkflowTemplate(
            name="F1-F4 功能测试",
            description="依次触发 F1 到 F4 功能键。",
            repeat=True,
            start_delay=0.0,
            cycle_interval=0.4,
            stop_mode="manual",
            stop_value=0.0,
            steps=[
                WorkflowStep("keyboard", "f1", hold_time=0.03, post_delay=0.05),
                WorkflowStep("keyboard", "f2", hold_time=0.03, post_delay=0.05),
                WorkflowStep("keyboard", "f3", hold_time=0.03, post_delay=0.05),
                WorkflowStep("keyboard", "f4", hold_time=0.03, post_delay=0.05),
            ],
        ).validate(),
    ]
