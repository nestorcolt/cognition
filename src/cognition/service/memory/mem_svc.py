from cognition.service.memory.long_term import CustomLongTermMemory, ExternalSQLHandler
from crewai.memory.long_term.long_term_memory import LongTermMemory
from cognition.service.config_service import ConfigManager
from cognition import logger

logger = logger.logger.getChild(__name__)


class MemoryService:
    """
    Memory Service that provides CrewAI memory configuration with all memory components
    """

    def __init__(self, config_manager: ConfigManager):
        self.config_manager = config_manager
        self.memory_config = {}
        self.embedder = (
            {
                "provider": "ollama",
                "config": {
                    "model": "nomic-embed-text",
                    "vector_dimension": 384,
                },
            },
        )

        self._initialize_config()

    def get_storage_path(self) -> str:
        """Get the storage path for memory data"""
        return self.storage_path

    def _initialize_config(self):
        """Initialize memory configuration"""
        self.memory_config = self.config_manager.get_memory_config()
        self.storage_path = self.config_manager.storage_dir
        logger.debug(f"Memory Storage Path: {self.storage_path}")

        if self.memory_config is None:
            return

        self.embedder = self.memory_config.get("embedder", self.embedder)
        logger.debug(f"Embedder: {self.embedder}")

    def __init_default_long_term_memory(self) -> LongTermMemory:
        """Initialize default long term memory configuration"""
        return LongTermMemory()

    def get_long_term_memory(self):
        """Get long term memory configuration"""
        settings = self.memory_config.get("long_term_memory", {})

        if settings is None:
            logger.debug("Long term memory configuration deactivated")
            return

        is_active = settings.get("enabled", False)
        is_external = settings.get("external", False)

        if is_active and is_external:
            # upstream connection string
            connection_string = settings.get("connection_string", None)

            if connection_string is None:
                logger.error(
                    "Connection string for external long term memory not found"
                )
                return

            storage = ExternalSQLHandler(connection_string)
            memory = CustomLongTermMemory(storage)
            return memory

        if is_active and not is_external:
            # downstream sqlite storage
            logger.debug("Long term memory default configuration activated")
            return self.__init_default_long_term_memory()

    # def get_crew_memory_config(self) -> Dict[str, Any]:
    #     """Get comprehensive memory configuration for CrewAI crew"""
    #     return {
    #         "memory": True,
    #         "long_term_memory": EnhanceLongTermMemory(
    #             storage=LTMSQLiteStorage(
    #                 db_path=f"{self.storage_path}/long_term_memory_storage.db"
    #             )
    #         ),
    #         "short_term_memory": EnhanceShortTermMemory(
    #             storage=CustomRAGStorage(
    #                 crew_name="cognition",
    #                 storage_type="short_term",
    #                 data_dir=self.storage_path,
    #                 model=self.embedder["model"],
    #                 dimension=self.embedder["dimension"],
    #             ),
    #         ),
    #         "entity_memory": EnhanceEntityMemory(
    #             storage=CustomRAGStorage(
    #                 crew_name="cognition",
    #                 storage_type="entities",
    #                 data_dir=self.storage_path,
    #                 model=self.embedder["model"],
    #                 dimension=self.embedder["dimension"],
    #             ),
    #         ),
    #         "verbose": True,
    #     }
