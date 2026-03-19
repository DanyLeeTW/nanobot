"""Configuration loading utilities."""

import copy
import json
from pathlib import Path
from typing import Any

from nanobot.config.schema import Config
from nanobot.config.secret_resolver import resolve_config, _REF_PATTERN


# Global variable to store current config path (for multi-instance support)
_current_config_path: Path | None = None


def set_config_path(path: Path) -> None:
    """Set the current config path (used to derive data directory)."""
    global _current_config_path
    _current_config_path = path


def get_config_path() -> Path:
    """Get the configuration file path."""
    if _current_config_path:
        return _current_config_path
    return Path.home() / ".nanobot" / "config.json"


def load_config(config_path: Path | None = None) -> Config:
    """
    Load configuration from file or create default.

    Args:
        config_path: Optional path to config file. Uses default if not provided.

    Returns:
        Loaded configuration object.
    """
    path = config_path or get_config_path()

    if path.exists():
        try:
            with open(path, encoding="utf-8") as f:
                raw_data = json.load(f)
            raw_data = _migrate_config(raw_data)

            # Record original values of fields containing {env:VAR} references
            env_refs: dict[str, Any] = {}
            _collect_env_refs(raw_data, "", env_refs)

            resolved_data = resolve_config(copy.deepcopy(raw_data))  # Resolve {env:VAR} references
            config = Config.model_validate(resolved_data)
            config._env_refs = env_refs  # Preserve original {env:VAR} values for save_config
            return config
        except (json.JSONDecodeError, ValueError) as e:
            print(f"Warning: Failed to load config from {path}: {e}")
            print("Using default configuration.")

    return Config()


def save_config(config: Config, config_path: Path | None = None) -> None:
    """
    Save configuration to file.

    Args:
        config: Configuration to save.
        config_path: Optional path to save to. Uses default if not provided.
    """
    path = config_path or get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    # Use raw unresolved data if available to preserve {env:VAR} placeholders
    # Use model_dump as base, but restore {env:VAR} references from original values
    data = config.model_dump(by_alias=True)
    if config._env_refs:
        _restore_env_refs(data, config._env_refs)

    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def _migrate_config(data: dict) -> dict:
    """Migrate old config formats to current."""
    # Move tools.exec.restrictToWorkspace → tools.restrictToWorkspace
    tools = data.get("tools", {})
    exec_cfg = tools.get("exec", {})
    if "restrictToWorkspace" in exec_cfg and "restrictToWorkspace" not in tools:
        tools["restrictToWorkspace"] = exec_cfg.pop("restrictToWorkspace")
    return data


def _collect_env_refs(obj: Any, path: str, refs: dict[str, Any]) -> None:
    """Collect field paths and original values for fields containing {env:VAR}."""
    if isinstance(obj, dict):
        for key, value in obj.items():
            child_path = f"{path}.{key}" if path else key
            _collect_env_refs(value, child_path, refs)
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            _collect_env_refs(item, f"{path}[{idx}]", refs)
    elif isinstance(obj, str) and _REF_PATTERN.search(obj):
        refs[path] = obj


def _restore_env_refs(data: dict, refs: dict[str, Any]) -> None:
    """Restore original {env:VAR} values into data dict."""
    for path, original_value in refs.items():
        _set_by_path(data, path, original_value)


def _set_by_path(data: dict, path: str, value: Any) -> None:
    """Set a value in nested dict by dot-notation path like 'providers.zhipu.apiKey'."""
    parts = path.split(".")
    current = data
    for part in parts[:-1]:
        if part not in current:
            return
        current = current[part]
    last_key = parts[-1]
    if isinstance(current, dict) and last_key in current:
        current[last_key] = value
