from cognition.svc.provider_base import MemoryProvider
from cognition.logger import logger
from typing import Dict, Any
from mem0 import MemoryClient


logger = logger.getChild(__name__)


class Mem0Service:
    """
    Core Mem0 service implementation handling memory operations using the official Mem0 client
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config

        # Initialize Mem0 client
        self.client = MemoryClient()
        self.logger = logger

    async def store(self, key: str, value: Any):
        """Store data in Mem0"""
        try:
            # Convert to message format expected by Mem0
            messages = [
                {"role": "system", "content": f"Storing data for key: {key}"},
                {"role": "user", "content": str(value)},
            ]
            self.client.add(messages, user_id=key)
            self.logger.info(f"Stored key '{key}'")
        except Exception as e:
            self.logger.error(f"Failed to store data in Mem0: {str(e)}")
            raise

    async def retrieve(self, key: str) -> Any:
        """Retrieve data from Mem0"""
        try:
            # Retrieve conversation history for the given key/user_id
            history = self.client.get(user_id=key)
            self.logger.info(f"Retrieved key '{key}'")
            return history
        except Exception as e:
            self.logger.error(f"Failed to retrieve data from Mem0: {str(e)}")
            raise

    async def retrieve_all(self) -> Dict[str, Any]:
        """Retrieve all data from Mem0"""
        # Note: Mem0 doesn't have a direct method to retrieve all data
        # This would need to be implemented based on your specific needs
        return {}


class Mem0Provider(MemoryProvider):
    """
    Mem0 provider that implements the MemoryProvider interface
    """

    def __init__(self, config: Dict[str, Any]):
        self.mem0 = Mem0Service(config)
        self.logger = logger

    async def connect(self):
        """Connect to Mem0"""
        # Mem0 connects during initialization
        pass

    async def set(self, key: str, value: Any):
        """Store memory using Mem0"""
        await self.mem0.store(key, value)

    async def get(self, key: str) -> Any:
        """Retrieve memory using Mem0"""
        return await self.mem0.retrieve(key)

    async def search(self, query: str) -> Dict[str, Any]:
        """Search memories using Mem0"""
        # Note: Implement if Mem0 provides search capabilities
        return {"results": []}

    async def get_context(self, context_type: str) -> Dict[str, Any]:
        """Get context from Mem0"""
        # This could be implemented based on how you want to organize different types of memory
        return {"type": context_type, "data": None}
