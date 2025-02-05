from crewai.memory.long_term.long_term_memory import LongTermMemory
from cognition.service.memory.long_term import CustomLongTermMemory
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
        logger.debug(f"Storage Path Requested: {self.storage_path}")
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

            # replace the password with the actual password
            connection_string = connection_string.replace(
                "your_password", self.config_manager.get_db_password()
            )

            memory = CustomLongTermMemory(connection_string)
            logger.debug(f"Long term memory: {memory.__class__.__name__}")
            return memory

        if is_active and not is_external:
            # downstream sqlite storage
            logger.debug("Long term memory default configuration activated")
            return self.__init_default_long_term_memory()
