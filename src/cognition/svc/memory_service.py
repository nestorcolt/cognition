from cognition.svc.config_service import ConfigManager
from typing import Dict, Any
from crewai.memory import (
    EnhanceLongTermMemory,
    EnhanceShortTermMemory,
    EnhanceEntityMemory,
    LTMSQLiteStorage,
    CustomRAGStorage,
)


class MemoryService:
    """
    Memory Service that provides CrewAI memory configuration with all memory components
    """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self._initialize_config()

    def _initialize_config(self):
        """Initialize memory configuration"""
        self.memory_config = self.config_manager.get_memory_config()
        self.storage_path = self.memory_config.get("storage_path", "./data/memory")

        # Configure embeddings
        self.embedder = {"model": "nomic-embed-text", "dimension": 768}

    def get_crew_memory_config(self) -> Dict[str, Any]:
        """Get comprehensive memory configuration for CrewAI crew"""
        return {
            "memory": True,
            "long_term_memory": EnhanceLongTermMemory(
                storage=LTMSQLiteStorage(
                    db_path=f"{self.storage_path}/long_term_memory_storage.db"
                )
            ),
            "short_term_memory": EnhanceShortTermMemory(
                storage=CustomRAGStorage(
                    crew_name="cognition",
                    storage_type="short_term",
                    data_dir=self.storage_path,
                    model=self.embedder["model"],
                    dimension=self.embedder["dimension"],
                ),
            ),
            "entity_memory": EnhanceEntityMemory(
                storage=CustomRAGStorage(
                    crew_name="cognition",
                    storage_type="entities",
                    data_dir=self.storage_path,
                    model=self.embedder["model"],
                    dimension=self.embedder["dimension"],
                ),
            ),
            "verbose": True,
        }

    def get_storage_path(self) -> str:
        """Get the storage path for memory data"""
        return self.storage_path
