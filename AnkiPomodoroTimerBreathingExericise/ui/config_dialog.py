from aqt import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGroupBox,
    QLabel,
    QVBoxLayout,
    mw,
)
from aqt.utils import tooltip

from ..config.config import save_config
from ..constants import STATUSBAR_FORMAT_NAMES, Defaults
from ..state import get_config, get_pomodoro_timer
from ..translator import _
from .config_components import BreathingSettings, GeneralSettings


class ConfigDialog(QDialog):
    """Configuration dialog for Pomodoro and Breathing settings."""

    def __init__(self, parent=None):
        super().__init__(parent or mw)

        # Use our config system instead of Anki's
        self.config = get_config()  # Store config as instance attribute

        self.setWindowTitle(_("番茄钟/呼吸训练设置"))
        self._main_layout = QVBoxLayout(self)

        # Initialize settings components
        self.general_settings = GeneralSettings(self.config)
        self.breathing_settings = BreathingSettings(self.config)

        # Add general settings component
        self._main_layout.addWidget(self.general_settings.create_ui(self))

        # Add status bar format selection
        self.statusbar_format_group = QGroupBox(_("状态栏显示设置"))
        self.statusbar_format_layout = QVBoxLayout()

        self.statusbar_format_combo = QComboBox()
        for format_key, format_name in STATUSBAR_FORMAT_NAMES.items():
            self.statusbar_format_combo.addItem(format_name, format_key)

        # Set currently selected format
        current_format = self.config.get("statusbar_format", Defaults.StatusBar.FORMAT)
        index = self.statusbar_format_combo.findData(current_format)
        if index >= 0:
            self.statusbar_format_combo.setCurrentIndex(index)

        self.statusbar_format_layout.addWidget(QLabel(_("选择状态栏显示格式：")))
        self.statusbar_format_layout.addWidget(self.statusbar_format_combo)
        self.statusbar_format_group.setLayout(self.statusbar_format_layout)

        # Add status bar settings to main layout
        self._main_layout.addWidget(self.statusbar_format_group)

        # Add breathing exercises component
        self._main_layout.addWidget(self.breathing_settings.create_ui(self))

        # --- Dialog Buttons (Save/Cancel) ---
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save
            | QDialogButtonBox.StandardButton.Cancel,
            self,
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        self._main_layout.addWidget(button_box)

        self.setLayout(self._main_layout)

        # Set initial estimated time based on loaded config
        self._update_estimated_time()

        # Connect breathing settings changes to update estimated time
        for phase in self.breathing_settings.phase_widgets.values():
            phase["checkbox"].toggled.connect(self._update_estimated_time)
            phase["spinbox"].valueChanged.connect(self._update_estimated_time)
        self.breathing_settings.widgets["cycles"].valueChanged.connect(
            self._update_estimated_time
        )

    def _update_estimated_time(self):
        """Calculates and updates the estimated breathing time label."""
        try:
            breathing_values = self.breathing_settings.get_values()
            target_cycles = breathing_values["breathing_cycles"]
            single_cycle_duration = 0
            any_phase_active = False

            # Calculate duration of one cycle based on *currently selected* values
            for key in self.breathing_settings.phase_widgets:
                if breathing_values.get(f"{key}_enabled", False):
                    single_cycle_duration += breathing_values.get(f"{key}_duration", 0)
                    any_phase_active = True

            if not any_phase_active or target_cycles <= 0:
                self.breathing_settings.widgets["estimated_time"].setText(
                    _("预计时间: --:-- (未启用任何阶段或目标周期数为0)")
                )
                return

            total_seconds = single_cycle_duration * target_cycles
            mins, secs = divmod(total_seconds, 60)
            self.breathing_settings.widgets["estimated_time"].setText(
                _("预计时间: {mins:02d}:{secs:02d}").format(mins=mins, secs=secs)
            )

        except Exception as e:
            tooltip(f"Error updating estimated time: {e}")
            self.breathing_settings.widgets["estimated_time"].setText(
                _("预计时间: 计算错误")
            )

    def accept(self):
        """Saves the configuration and closes the dialog."""
        try:
            self.config = get_config()

            # Get values from component classes
            general_values = self.general_settings.get_values()
            breathing_values = self.breathing_settings.get_values()

            # Update config with component values
            self.config.update(general_values)
            self.config.update(breathing_values)
            self.config["statusbar_format"] = self.statusbar_format_combo.currentData()

            save_config(self.config)
            tooltip(_("配置已保存"))

            # Update display immediately
            timer = get_pomodoro_timer()

            if timer:
                timer.update_display()

            super().accept()
        except Exception as e:
            tooltip(_("保存配置时出错: {}").format(e))
