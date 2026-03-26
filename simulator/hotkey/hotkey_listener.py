from PyQt5.QtCore import QObject, pyqtSignal
from pynput import keyboard


class HotkeyListener(QObject):
    hotkeyPressed = pyqtSignal()

    def __init__(self, hotkey="F8"):
        super().__init__()
        self.hotkey = hotkey
        self.listener = None
        self._pressed = set()

    def start(self):
        if self.listener is not None:
            return
        self.listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
        )
        self.listener.daemon = True
        self.listener.start()

    def _normalize_key(self, key):
        if hasattr(key, "vk") and key.vk is not None:
            return str(key.vk)
        if hasattr(key, "char") and key.char:
            return key.char.lower()
        return str(key)

    def _matches_hotkey(self, key):
        hotkey_name = self.hotkey.strip().lower()
        if hotkey_name.startswith("f") and hotkey_name[1:].isdigit():
            return key == getattr(keyboard.Key, hotkey_name, None)
        return self._normalize_key(key) == hotkey_name

    def _on_press(self, key):
        normalized = self._normalize_key(key)
        if normalized in self._pressed:
            return
        self._pressed.add(normalized)
        if self._matches_hotkey(key):
            self.hotkeyPressed.emit()

    def _on_release(self, key):
        normalized = self._normalize_key(key)
        if normalized in self._pressed:
            self._pressed.remove(normalized)
