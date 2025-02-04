from watchdog.events import FileSystemEventHandler
from pydantic import BaseModel, ValidationError
from watchdog.observers import Observer
from contextlib import contextmanager
from typing import Dict, Any, Type
from pathlib import Path
import yaml
import os


class ConfigValidationError(Exception):
    pass


class ConfigSchema(BaseModel):
    version: str
    environment: str


class ConfigManager:
    def __init__(self):
        self.config_dir = os.environ.get("CONFIG_DIR") or "./config"

        if not os.path.exists(self.config_dir):
            raise FileNotFoundError(f"Config directory not found: {self.config_dir}")

        self._cache = {}
        self._setup_hot_reload()
        self._load_configs()

    def _setup_hot_reload(self):
        event_handler = ConfigReloader(self)
        self.observer = Observer()
        self.observer.schedule(event_handler, str(self.config_dir), recursive=False)
        self.observer.start()

    def __del__(self):
        if hasattr(self, "observer"):
            self.observer.stop()
            self.observer.join()

    def _load_configs(self):
        for config_file in self.config_dir.glob("*.yaml"):
            self._load_file(config_file)

    def _load_file(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            raise FileNotFoundError(f"Config file not found: {file_path}")

        try:
            with open(file_path) as f:
                config = yaml.safe_load(f)
                if not isinstance(config, dict):
                    raise ValueError(f"Invalid YAML structure in {file_path}")
                self._cache[file_path.stem] = config
        except yaml.YAMLError as e:
            raise ConfigValidationError(f"YAML parsing error in {file_path}: {str(e)}")

    def validate_config(self, config_name: str, schema: Type[BaseModel]) -> None:
        try:
            schema(**self.get_config(config_name))
        except ValidationError as e:
            raise ConfigValidationError(f"Invalid config {config_name}: {str(e)}")

    def get_config(self, name: str, validate: bool = True) -> Dict[str, Any]:
        """Get config with optional validation"""
        config = self._cache.get(name)
        if config is None:
            raise KeyError(f"Configuration '{name}' not found")

        if validate:
            config = EnvManager.override_config(config)
        return config

    def get_nested_value(self, config_name: str, path: str, default: Any = None) -> Any:
        """Get nested config value using dot notation (e.g. 'database.host')"""
        config = self.get_config(config_name)
        keys = path.split(".")

        for key in keys:
            if not isinstance(config, dict):
                return default
            config = config.get(key, default)
        return config

    @contextmanager
    def config_scope(self):
        """Context manager for safe config handling"""
        try:
            yield self
        finally:
            self.observer.stop()
            self.observer.join()

    def get_memory_config(self) -> Dict[str, Any]:
        """Get memory-specific configuration"""
        memory_config = self.get_config("memory", validate=False)
        if not memory_config:
            return {"active_provider": "default"}

        # Override with environment variables
        return EnvManager.override_config(memory_config, prefix="CREW_MEMORY_")

    def get_mem0_config(self) -> Dict[str, Any]:
        """Get Mem0-specific configuration"""
        mem0_config = self.get_config("mem0", validate=False)
        if not mem0_config:
            return {
                "storage_path": "./data/mem0",
                "embedder": {
                    "provider": "openai",
                    "config": {"model": "text-embedding-3-small"},
                },
            }

        # Override with environment variables
        return EnvManager.override_config(mem0_config, prefix="CREW_MEM0_")


class EnvManager:
    @staticmethod
    def get_env_value(key: str, default: Any = None) -> Any:
        return os.environ.get(key, default)

    @staticmethod
    def override_config(config: dict, prefix: str = "CREW_") -> dict:
        for key in config:
            env_key = f"{prefix}{key.upper()}"
            if env_key in os.environ:
                config[key] = os.environ[env_key]
        return config


class ConfigReloader(FileSystemEventHandler):
    def __init__(self, config_manager):
        self.config_manager = config_manager

    def on_modified(self, event):
        if event.src_path.endswith(".yaml"):
            self.config_manager._load_file(Path(event.src_path))
