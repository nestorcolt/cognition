from src.cognition.svc.mem0_service import Mem0Provider
from typing import Dict, Any
import random
import time


# Define a common interface for memory operations
class MemoryProvider:
    async def connect(self):
        raise NotImplementedError("Method 'connect' must be implemented.")

    async def set(self, key: str, value: Any):
        raise NotImplementedError("Method 'set' must be implemented.")

    async def get(self, key: str) -> Any:
        raise NotImplementedError("Method 'get' must be implemented.")

    async def search(self, query: str) -> Dict[str, Any]:
        raise NotImplementedError("Method 'search' must be implemented.")

    async def get_context(self, context_type: str) -> Dict[str, Any]:
        raise NotImplementedError("Method 'get_context' must be implemented.")


# Default memory provider using in-memory caching (CrewAI default)
class DefaultMemoryProvider(MemoryProvider):
    def __init__(self):
        self.cache = {}

    async def connect(self):
        print("DefaultMemoryProvider: Using in-memory caching.")

    async def set(self, key: str, value: Any):
        self.cache[key] = value
        print(f"DefaultMemoryProvider: Stored key '{key}' with value '{value}'.")

    async def get(self, key: str) -> Any:
        value = self.cache.get(key)
        print(f"DefaultMemoryProvider: Retrieved key '{key}' with value '{value}'.")
        return value

    async def search(self, query: str) -> Dict[str, Any]:
        return {"results": [v for k, v in self.cache.items() if query in k]}

    async def get_context(self, context_type: str) -> Dict[str, Any]:
        return {"type": context_type, "data": self.cache}


# Cloud memory provider for cloud-based or external memory backends.
class CloudMemoryProvider(MemoryProvider):
    def __init__(self, config: dict):
        self.config = config
        self.connected = False
        self.connection = (
            None  # In a real provider, this would be the database connection object
        )

    async def connect(self):
        # Implements a simple incremental backoff retry mechanism
        retry_config = self.config.get("retry", {})
        max_attempts = retry_config.get("max_attempts", 3)
        backoff_factor = retry_config.get("backoff_factor", 1)
        attempt = 0

        print("CloudMemoryProvider: Attempting to connect...")
        while attempt < max_attempts:
            try:
                # Here we simulate a connection attempt.
                # Introduce a random chance of failure to simulate transient issues
                if random.random() < 0.7:
                    raise ConnectionError("Simulated connection failure.")
                # Simulate a successful connection
                self.connection = "CloudConnectionObject"  # Dummy connection object
                self.connected = True
                print(
                    "CloudMemoryProvider: Successfully connected to cloud memory provider."
                )
                return
            except ConnectionError as e:
                attempt += 1
                sleep_time = backoff_factor * attempt
                print(
                    f"CloudMemoryProvider: Attempt {attempt} failed: {e}. Retrying in {sleep_time} second(s)..."
                )
                time.sleep(sleep_time)
        raise ConnectionError(
            "CloudMemoryProvider: Maximum retry attempts exceeded. Could not connect."
        )

    async def set(self, key: str, value: Any):
        if not self.connected:
            raise ConnectionError("CloudMemoryProvider: Not connected.")
        # Dummy implementation: In production, replace with actual database set operation
        print(
            f"CloudMemoryProvider: Setting key '{key}' to '{value}' in cloud storage."
        )

    async def get(self, key: str) -> Any:
        if not self.connected:
            raise ConnectionError("CloudMemoryProvider: Not connected.")
        # Dummy implementation: In production, replace with actual database get operation
        print(f"CloudMemoryProvider: Getting key '{key}' from cloud storage.")
        return None

    async def search(self, query: str) -> Dict[str, Any]:
        # Cloud provider does not support search
        raise NotImplementedError(
            "CloudMemoryProvider: Search operation not supported."
        )

    async def get_context(self, context_type: str) -> Dict[str, Any]:
        # Cloud provider does not support get_context
        raise NotImplementedError(
            "CloudMemoryProvider: get_context operation not supported."
        )


# Main MemoryService class that selects and manages the appropriate memory provider.
class MemoryService:
    """
    Memory Service that routes memory operations to appropriate providers
    based on configuration.
    """

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.providers: Dict[str, MemoryProvider] = {}
        self._initialize_providers()

    def _initialize_providers(self):
        """Initialize configured memory providers"""
        # Always initialize default provider
        self.providers["default"] = DefaultMemoryProvider()

        # Initialize Mem0 if configured
        if self.config.get("mem0"):
            self.providers["mem0"] = Mem0Provider(self.config["mem0"])

        # Set active provider
        self.active_provider = self.providers.get(
            self.config.get("active_provider", "default"), self.providers["default"]
        )

    def switch_provider(self, provider_name: str):
        """Switch to a different memory provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider '{provider_name}' not configured")
        self.active_provider = self.providers[provider_name]

    async def set(self, key: str, value: Any):
        """Store memory using active provider"""
        return await self.active_provider.set(key, value)

    async def get(self, key: str) -> Any:
        """Retrieve memory using active provider"""
        return await self.active_provider.get(key)

    async def search(self, query: str) -> Dict[str, Any]:
        """Search memories using active provider"""
        return await self.active_provider.search(query)

    async def get_context(self, context_type: str) -> Dict[str, Any]:
        """Get context using active provider"""
        return await self.active_provider.get_context(context_type)

    def get_provider(self, name: str = None) -> MemoryProvider:
        """Get specific provider or active provider"""
        if name:
            return self.providers.get(name)
        return self.active_provider
