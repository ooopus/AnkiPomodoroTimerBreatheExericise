import sys
from pathlib import Path

# Add the 'vendor' directory to Python's path
vendor_dir = Path(__file__).resolve().parent.parent / "vendor"
if str(vendor_dir) not in sys.path:
    sys.path.insert(0, str(vendor_dir))
# 由于anki使用自带的python，必须先导入外部依赖


import dataclasses
import json
import shutil
from enum import Enum
from pathlib import Path
from typing import Any

from koda_validate import Valid

from .enums import CircularTimerStyle, StatusBarFormat, TimerPosition
from .types import AppConfig, config_validator

# Path(__file__).resolve() 获取此文件的绝对路径
# .parent 指向包含此文件的目录 (config/)
# .parent.parent 指向上一级目录 (项目根目录)
# 然后与 "config.json" 文件名结合
CONFIG_PATH = Path(__file__).resolve().parent.parent / "config.json"


class EnhancedJSONEncoder(json.JSONEncoder):
    """一个增强的JSON编码器,可以处理枚举类型。"""

    def default(self, o: Any):
        if isinstance(o, Enum):
            return o.value
        return super().default(o)


def deep_compare(item1, item2):
    """递归比较两个项目，将列表和元组视为等同。"""
    # 如果类型不同，但不是列表/元组对，则认为不同
    if (
        not isinstance(item1, type(item2))
        and not isinstance(item2, type(item1))
        and not (isinstance(item1, list | tuple) and isinstance(item2, list | tuple))
    ):
        return False

    if isinstance(item1, dict) and isinstance(item2, dict):
        if set(item1.keys()) != set(item2.keys()):
            return False
        return all(deep_compare(item1[k], item2[k]) for k in item1)

    # Compare lists and tuples
    if isinstance(item1, list | tuple) and isinstance(item2, list | tuple):
        if len(item1) != len(item2):
            return False
        return all(deep_compare(i1, i2) for i1, i2 in zip(item1, item2, strict=False))

    else:
        return item1 == item2


def get_default_config() -> AppConfig:
    """方便地获取一个包含所有默认值的 AppConfig 实例。"""
    return AppConfig()


def save_config(config: AppConfig):
    """
    将一个 AppConfig 实例保存到固定的 JSON 文件路径。
    """
    try:
        # 确保配置文件所在的目录存在
        CONFIG_PATH.parent.mkdir(parents=True, exist_ok=True)
        with CONFIG_PATH.open("w", encoding="utf-8") as f:
            config_dict = dataclasses.asdict(config)
            json.dump(
                config_dict, f, indent=4, ensure_ascii=False, cls=EnhancedJSONEncoder
            )
    except OSError as e:
        print(f"错误: 无法写入配置文件 '{CONFIG_PATH}': {e}")


def _migrate_config_data(data: dict[str, Any]) -> dict[str, Any]:
    """
    迁移旧的配置数据格式到新的枚举类型。
    """
    # 迁移 circular_timer_style
    if "circular_timer_style" in data and isinstance(data["circular_timer_style"], str):
        try:
            data["circular_timer_style"] = CircularTimerStyle(
                data["circular_timer_style"]
            )
        except ValueError:
            print(
                f"警告: 无效的 circular_timer_style '{data['circular_timer_style']}', "
                f"使用默认值 '{CircularTimerStyle.DEFAULT.value}'."
            )
            data["circular_timer_style"] = CircularTimerStyle.DEFAULT

    # 迁移 statusbar_format
    if "statusbar_format" in data and isinstance(data["statusbar_format"], str):
        try:
            data["statusbar_format"] = StatusBarFormat(data["statusbar_format"])
        except ValueError:
            print(
                f"警告: 无效的 statusbar_format '{data['statusbar_format']}', "
                "使用默认值"
                f"'{StatusBarFormat.ICON_COUNTDOWN_PROGRESS_WITH_TOTAL_TIME.value}'."
            )
            data["statusbar_format"] = (
                StatusBarFormat.ICON_COUNTDOWN_PROGRESS_WITH_TOTAL_TIME
            )

    # 迁移 timer_position
    if "timer_position" in data and isinstance(data["timer_position"], str):
        try:
            data["timer_position"] = TimerPosition(data["timer_position"])
        except ValueError:
            print(
                f"警告: 无效的 timer_position '{data['timer_position']}', "
                f"使用默认值 '{TimerPosition.TOP_RIGHT.value}'."
            )
            data["timer_position"] = TimerPosition.TOP_RIGHT

    # 迁移 language
    if "language" in data and isinstance(data["language"], str):
        from .languages import LanguageCode

        try:
            data["language"] = LanguageCode(data["language"])
        except ValueError:
            print(
                f"警告: 无效的 language '{data['language']}', "
                f"使用默认值 '{LanguageCode.AUTO.value}'."
            )
            data["language"] = LanguageCode.AUTO

    return data


def _read_config_file(path: Path) -> dict[str, Any]:
    """从指定路径读取并解析 JSON 文件内容。"""
    with path.open("r", encoding="utf-8") as f:
        content = f.read()
        if not content:
            raise json.JSONDecodeError("File is empty", "", 0)
        return json.loads(content)


def _backup_corrupted_config(path: Path):
    """备份损坏的配置文件。"""
    backup_path = path.with_suffix(".json.bak")
    try:
        if path.exists():
            shutil.move(str(path), str(backup_path))
            print(f"已将损坏的配置文件备份到: '{backup_path}'")
    except OSError as backup_error:
        print(f"警告: 备份损坏的配置文件失败: {backup_error}")


def _create_default_config_file(path: Path):
    """创建新的默认配置文件。"""
    print(f"提示: 配置文件 '{path}' 不存在。")
    print("正在使用默认设置创建新的配置文件...")
    default_config = get_default_config()
    save_config(default_config)
    print(f"成功创建默认配置文件: '{path}'")
    return default_config


def load_user_config() -> AppConfig:
    """
    从固定的路径加载、验证并返回用户配置。
    - 如果配置文件不存在，则创建一个包含默认值的配置文件。
    - 如果配置文件损坏，则将其备份并创建一个新的默认配置文件。
    - 如果配置文件缺少字段，则使用默认值填充。

    Returns:
        一个经过验证和完全填充的 AppConfig 实例。
    """
    # 定义需要忽略的运行时状态字段列表
    # 这些字段通常在运行时动态更新，不应触发配置更新提示
    IGNORED_STATE_FIELDS = [
        "is_timer_active",
        "is_break_active",
        "remaining_time",
        "current_round",
        "timer_end_time",
        "last_focus_timestamp",
        "last_review_timestamp",
        "next_review_interval",
        "last_state",
    ]

    if not CONFIG_PATH.exists():
        return _create_default_config_file(CONFIG_PATH)

    try:
        loaded_data = _read_config_file(CONFIG_PATH)

        # 在验证之前进行数据迁移
        loaded_data = _migrate_config_data(loaded_data)

        # 使用从 types.py 导入的验证器进行验证和填充
        result = config_validator(loaded_data)

        if isinstance(result, Valid):
            config = result.val
            # 将可能已更新的配置回写到文件
            updated_dict = dataclasses.asdict(config)

            # 移除运行时状态字段，只比较非状态字段的差异
            comparison_updated = {
                k: v for k, v in updated_dict.items() if k not in IGNORED_STATE_FIELDS
            }
            comparison_loaded = {
                k: v for k, v in loaded_data.items() if k not in IGNORED_STATE_FIELDS
            }

            if not deep_compare(comparison_updated, comparison_loaded):
                print("提示: 配置已使用新添加的默认值更新。正在回写配置文件...")
                save_config(config)
            return config
        else:
            raise ValueError(f"配置验证失败: {result}")

    except (json.JSONDecodeError, ValueError, TypeError) as e:
        print(f"错误: 配置文件 '{CONFIG_PATH}' 已损坏或格式无效。")
        print(f"详细信息: {e}")

        _backup_corrupted_config(CONFIG_PATH)

        # 创建一个新的默认配置
        print("正在创建全新的默认配置文件...")
        default_config = get_default_config()
        save_config(default_config)
        print("已成功创建新的默认配置文件。程序将使用默认设置继续运行。")
        return default_config
