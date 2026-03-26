import winsound

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import (
    QAbstractItemView,
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QDoubleSpinBox,
    QTableWidget,
    QTableWidgetItem,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

from simulator.core.workflow import WorkflowStep, WorkflowTemplate, default_templates
from simulator.core.workflow_simulator import WorkflowSimulator
from simulator.hotkey.hotkey_listener import HotkeyListener


class MainWindow(QMainWindow):
    KEY_PRESETS = [
        "space", "enter", "tab", "esc", "backspace", "delete", "insert",
        "home", "end", "pageup", "pagedown", "up", "down", "left", "right",
        "shift", "ctrl", "alt", "capslock", "numlock", "scrolllock",
        "left_win", "right_win", "apps", "printscreen", "pause",
        "0", "1", "2", "3", "4", "5", "6", "7", "8", "9",
        "a", "b", "c", "d", "e", "f", "g", "h", "i", "j", "k", "l", "m",
        "n", "o", "p", "q", "r", "s", "t", "u", "v", "w", "x", "y", "z",
        "f1", "f2", "f3", "f4", "f5", "f6", "f7", "f8", "f9", "f10", "f11", "f12",
        "numpad0", "numpad1", "numpad2", "numpad3", "numpad4",
        "numpad5", "numpad6", "numpad7", "numpad8", "numpad9",
        "multiply", "add", "subtract", "decimal", "divide",
        ";", "=", ",", "-", ".", "/", "`", "[", "\\", "]", "'",
    ]
    STOP_MODE_LABELS = {
        "manual": "手动停止",
        "duration": "按运行时长停止",
        "cycles": "按循环次数停止",
    }
    STOP_MODE_VALUES = {label: key for key, label in STOP_MODE_LABELS.items()}

    def __init__(self):
        super().__init__()
        self.setWindowTitle("鼠标键盘流程模拟器")

        self.simulator = None
        self.is_running = False
        self.templates = {template.name: template for template in default_templates()}

        self._build_ui()
        self.load_template(self.templates["鼠标左键连点"])

        self.listener = HotkeyListener("F8")
        self.listener.hotkeyPressed.connect(self.toggle_simulation)
        self.listener.start()

        self.status_timer = QTimer(self)
        self.status_timer.timeout.connect(self.sync_simulator_state)
        self.status_timer.start(200)

    def _build_ui(self):
        central_widget = QWidget()
        root_layout = QVBoxLayout()
        root_layout.setSpacing(10)

        intro_label = QLabel("编辑自动化流程后，点击“开始”或按 F8 即可运行。")
        intro_label.setWordWrap(True)
        root_layout.addWidget(intro_label)

        preset_layout = QHBoxLayout()
        preset_layout.addWidget(QLabel("预设模板"))
        self.preset_combo = QComboBox()
        self.preset_combo.addItems(self.templates.keys())
        preset_layout.addWidget(self.preset_combo)

        load_preset_button = QPushButton("加载预设")
        load_preset_button.clicked.connect(self.load_selected_preset)
        preset_layout.addWidget(load_preset_button)
        root_layout.addLayout(preset_layout)

        form_layout = QFormLayout()
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.description_input.setFixedHeight(60)

        self.repeat_checkbox = QCheckBox("循环执行流程")
        self.repeat_checkbox.setChecked(True)

        self.start_delay_input = QDoubleSpinBox()
        self.start_delay_input.setDecimals(2)
        self.start_delay_input.setSingleStep(0.5)
        self.start_delay_input.setRange(0.0, 3600.0)
        self.start_delay_input.setSuffix(" 秒")

        self.cycle_interval_input = QDoubleSpinBox()
        self.cycle_interval_input.setDecimals(4)
        self.cycle_interval_input.setSingleStep(0.01)
        self.cycle_interval_input.setRange(0.0, 9999.0)
        self.cycle_interval_input.setSuffix(" 秒")

        self.stop_mode_combo = QComboBox()
        self.stop_mode_combo.addItems(self.STOP_MODE_LABELS.values())
        self.stop_mode_combo.currentTextChanged.connect(self.update_stop_value_state)

        self.stop_value_input = QDoubleSpinBox()
        self.stop_value_input.setDecimals(2)
        self.stop_value_input.setSingleStep(1.0)
        self.stop_value_input.setRange(0.0, 999999.0)
        self.stop_value_input.setSuffix(" 秒")

        form_layout.addRow("模板名称", self.name_input)
        form_layout.addRow("模板说明", self.description_input)
        form_layout.addRow("", self.repeat_checkbox)
        form_layout.addRow("启动延时", self.start_delay_input)
        form_layout.addRow("循环间隔", self.cycle_interval_input)
        form_layout.addRow("终止条件", self.stop_mode_combo)
        form_layout.addRow("终止数值", self.stop_value_input)
        root_layout.addLayout(form_layout)

        self.step_table = QTableWidget(0, 4)
        self.step_table.setHorizontalHeaderLabels(["类型", "目标键", "按住时长(秒)", "步骤延迟(秒)"])
        self.step_table.horizontalHeader().setStretchLastSection(True)
        self.step_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.step_table.setSelectionMode(QAbstractItemView.SingleSelection)
        root_layout.addWidget(QLabel("流程步骤"))
        root_layout.addWidget(self.step_table)

        editor_layout = QHBoxLayout()
        self.action_type_combo = QComboBox()
        self.action_type_combo.addItems(["keyboard", "mouse"])

        self.target_combo = QComboBox()
        self.target_combo.setEditable(True)
        self.action_type_combo.currentTextChanged.connect(self.refresh_target_options)

        self.hold_input = QDoubleSpinBox()
        self.hold_input.setDecimals(4)
        self.hold_input.setRange(0.0, 999.0)
        self.hold_input.setSingleStep(0.01)
        self.hold_input.setValue(0.05)

        self.delay_input = QDoubleSpinBox()
        self.delay_input.setDecimals(4)
        self.delay_input.setRange(0.0, 999.0)
        self.delay_input.setSingleStep(0.01)
        self.delay_input.setValue(0.1)

        editor_layout.addWidget(QLabel("类型"))
        editor_layout.addWidget(self.action_type_combo)
        editor_layout.addWidget(QLabel("目标键"))
        editor_layout.addWidget(self.target_combo)
        editor_layout.addWidget(QLabel("按住"))
        editor_layout.addWidget(self.hold_input)
        editor_layout.addWidget(QLabel("延迟"))
        editor_layout.addWidget(self.delay_input)
        root_layout.addLayout(editor_layout)

        step_button_layout = QHBoxLayout()
        add_step_button = QPushButton("添加步骤")
        add_step_button.clicked.connect(self.add_step)
        update_step_button = QPushButton("更新选中项")
        update_step_button.clicked.connect(self.update_selected_step)
        remove_step_button = QPushButton("删除选中项")
        remove_step_button.clicked.connect(self.remove_selected_step)
        move_up_button = QPushButton("上移")
        move_up_button.clicked.connect(lambda: self.move_selected_step(-1))
        move_down_button = QPushButton("下移")
        move_down_button.clicked.connect(lambda: self.move_selected_step(1))

        step_button_layout.addWidget(add_step_button)
        step_button_layout.addWidget(update_step_button)
        step_button_layout.addWidget(remove_step_button)
        step_button_layout.addWidget(move_up_button)
        step_button_layout.addWidget(move_down_button)
        root_layout.addLayout(step_button_layout)

        template_button_layout = QHBoxLayout()
        export_button = QPushButton("导出模板")
        export_button.clicked.connect(self.export_template)
        import_button = QPushButton("导入模板")
        import_button.clicked.connect(self.import_template)
        template_button_layout.addWidget(export_button)
        template_button_layout.addWidget(import_button)
        root_layout.addLayout(template_button_layout)

        self.start_button = QPushButton("开始")
        self.start_button.clicked.connect(self.toggle_simulation)
        root_layout.addWidget(self.start_button)

        hint = QLabel("支持常见键盘按键、方向键、功能键、小键盘和鼠标左/右/中键，也可以手动输入自定义键名。")
        hint.setWordWrap(True)
        hint.setAlignment(Qt.AlignLeft)
        root_layout.addWidget(hint)

        self.refresh_target_options(self.action_type_combo.currentText())
        self.update_stop_value_state(self.stop_mode_combo.currentText())
        self.step_table.itemSelectionChanged.connect(self.load_selected_step_into_editor)

        central_widget.setLayout(root_layout)
        self.setCentralWidget(central_widget)

    def refresh_target_options(self, action_type):
        current_text = self.target_combo.currentText()
        self.target_combo.clear()
        if action_type == "keyboard":
            self.target_combo.addItems(self.KEY_PRESETS)
        else:
            self.target_combo.addItems(["left", "right", "middle"])
        if current_text:
            self.target_combo.setEditText(current_text)

    def load_selected_preset(self):
        self.load_template(self.templates[self.preset_combo.currentText()])

    def load_template(self, template):
        template = template.validate()
        self.name_input.setText(template.name)
        self.description_input.setPlainText(template.description)
        self.repeat_checkbox.setChecked(template.repeat)
        self.start_delay_input.setValue(template.start_delay)
        self.cycle_interval_input.setValue(template.cycle_interval)
        self.stop_mode_combo.setCurrentText(self.STOP_MODE_LABELS.get(template.stop_mode, "手动停止"))
        self.stop_value_input.setValue(template.stop_value)
        self.step_table.setRowCount(0)
        for step in template.steps:
            self.append_step_row(step)

    def build_template_from_ui(self):
        steps = []
        for row in range(self.step_table.rowCount()):
            steps.append(
                WorkflowStep(
                    action_type=self.step_table.item(row, 0).text(),
                    target=self.step_table.item(row, 1).text(),
                    hold_time=float(self.step_table.item(row, 2).text()),
                    post_delay=float(self.step_table.item(row, 3).text()),
                )
            )
        return WorkflowTemplate(
            name=self.name_input.text(),
            description=self.description_input.toPlainText(),
            repeat=self.repeat_checkbox.isChecked(),
            start_delay=self.start_delay_input.value(),
            cycle_interval=self.cycle_interval_input.value(),
            stop_mode=self.STOP_MODE_VALUES[self.stop_mode_combo.currentText()],
            stop_value=self.stop_value_input.value(),
            steps=steps,
        ).validate()

    def build_step_from_editor(self):
        return WorkflowStep(
            action_type=self.action_type_combo.currentText(),
            target=self.target_combo.currentText(),
            hold_time=self.hold_input.value(),
            post_delay=self.delay_input.value(),
        ).validate()

    def append_step_row(self, step):
        row = self.step_table.rowCount()
        self.step_table.insertRow(row)
        self.step_table.setItem(row, 0, QTableWidgetItem(step.action_type))
        self.step_table.setItem(row, 1, QTableWidgetItem(step.target))
        self.step_table.setItem(row, 2, QTableWidgetItem(f"{step.hold_time:.4f}"))
        self.step_table.setItem(row, 3, QTableWidgetItem(f"{step.post_delay:.4f}"))

    def add_step(self):
        try:
            step = self.build_step_from_editor()
        except ValueError as exc:
            self.show_error(str(exc))
            return
        self.append_step_row(step)

    def update_selected_step(self):
        row = self.step_table.currentRow()
        if row < 0:
            self.show_error("请先选中一个要更新的步骤。")
            return
        try:
            step = self.build_step_from_editor()
        except ValueError as exc:
            self.show_error(str(exc))
            return
        self.step_table.item(row, 0).setText(step.action_type)
        self.step_table.item(row, 1).setText(step.target)
        self.step_table.item(row, 2).setText(f"{step.hold_time:.4f}")
        self.step_table.item(row, 3).setText(f"{step.post_delay:.4f}")

    def remove_selected_step(self):
        row = self.step_table.currentRow()
        if row >= 0:
            self.step_table.removeRow(row)

    def move_selected_step(self, offset):
        row = self.step_table.currentRow()
        target_row = row + offset
        if row < 0 or target_row < 0 or target_row >= self.step_table.rowCount():
            return
        values = [self.step_table.item(row, col).text() for col in range(4)]
        target_values = [self.step_table.item(target_row, col).text() for col in range(4)]
        for col, value in enumerate(target_values):
            self.step_table.item(row, col).setText(value)
        for col, value in enumerate(values):
            self.step_table.item(target_row, col).setText(value)
        self.step_table.selectRow(target_row)

    def load_selected_step_into_editor(self):
        row = self.step_table.currentRow()
        if row < 0:
            return
        action_type = self.step_table.item(row, 0).text()
        self.action_type_combo.setCurrentText(action_type)
        self.refresh_target_options(action_type)
        self.target_combo.setEditText(self.step_table.item(row, 1).text())
        self.hold_input.setValue(float(self.step_table.item(row, 2).text()))
        self.delay_input.setValue(float(self.step_table.item(row, 3).text()))

    def update_stop_value_state(self, stop_mode_label):
        stop_mode = self.STOP_MODE_VALUES[stop_mode_label]
        enabled = stop_mode != "manual"
        self.stop_value_input.setEnabled(enabled)
        if stop_mode == "duration":
            self.stop_value_input.setDecimals(2)
            self.stop_value_input.setSingleStep(1.0)
            self.stop_value_input.setSuffix(" 秒")
            if self.stop_value_input.value() <= 0:
                self.stop_value_input.setValue(10.0)
        elif stop_mode == "cycles":
            self.stop_value_input.setDecimals(0)
            self.stop_value_input.setSingleStep(1.0)
            self.stop_value_input.setSuffix(" 次")
            if self.stop_value_input.value() <= 0:
                self.stop_value_input.setValue(10.0)
        else:
            self.stop_value_input.setValue(0.0)
            self.stop_value_input.setSuffix("")

    def export_template(self):
        try:
            template = self.build_template_from_ui()
        except ValueError as exc:
            self.show_error(str(exc))
            return

        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "导出流程模板",
            f"{template.name}.json",
            "JSON Files (*.json)",
        )
        if not file_path:
            return

        with open(file_path, "w", encoding="utf-8") as file:
            file.write(template.to_json())

    def import_template(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "导入流程模板",
            "",
            "JSON Files (*.json)",
        )
        if not file_path:
            return

        try:
            with open(file_path, "r", encoding="utf-8") as file:
                template = WorkflowTemplate.from_json(file.read())
        except (OSError, ValueError) as exc:
            self.show_error(f"导入模板失败：{exc}")
            return

        self.templates[template.name] = template
        if self.preset_combo.findText(template.name) == -1:
            self.preset_combo.addItem(template.name)
        self.preset_combo.setCurrentText(template.name)
        self.load_template(template)

    def toggle_simulation(self):
        if not self.is_running:
            try:
                template = self.build_template_from_ui()
            except ValueError as exc:
                self.show_error(str(exc))
                return

            self.simulator = WorkflowSimulator(template)
            self.play_start_sound()
            self.simulator.start()
            self.start_button.setText("停止")
            self.is_running = True
        else:
            self.stop_simulation()

    def play_start_sound(self):
        try:
            winsound.Beep(880, 90)
            winsound.Beep(1175, 120)
        except RuntimeError:
            try:
                winsound.MessageBeep(winsound.MB_OK)
            except RuntimeError:
                pass

    def play_stop_sound(self):
        try:
            winsound.Beep(784, 90)
            winsound.Beep(523, 140)
        except RuntimeError:
            try:
                winsound.MessageBeep(winsound.MB_ICONEXCLAMATION)
            except RuntimeError:
                pass

    def stop_simulation(self):
        if self.simulator:
            self.simulator.stop()
            self.play_stop_sound()
        self.simulator = None
        self.start_button.setText("开始")
        self.is_running = False

    def closeEvent(self, event):
        self.stop_simulation()
        super().closeEvent(event)

    def sync_simulator_state(self):
        if self.is_running and self.simulator and not self.simulator.is_running():
            self.stop_simulation()

    def show_error(self, message):
        QMessageBox.warning(self, "流程配置错误", message)
