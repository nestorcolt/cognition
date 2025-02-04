import time
import random
from typing import Dict, Any, Optional
from src.cognition.svc.mem0_service import Mem0Service


# Define a common interface for memory operations
class MemoryProvider:
    def connect(self):
        raise NotImplementedError("Method 'connect' must be implemented.")

    def set(self, key: str, value: Any):
        raise NotImplementedError("Method 'set' must be implemented.")

    def get(self, key: str) -> Any:
        raise NotImplementedError("Method 'get' must be implemented.")


# Default memory provider using in-memory caching (CrewAI default)
class DefaultMemoryProvider(MemoryProvider):
    def __init__(self):
        self.cache = {}

    def connect(self):
        # No actual connection is needed for in-memory caching
        print("DefaultMemoryProvider: Using in-memory caching.")

    def set(self, key: str, value: Any):
        self.cache[key] = value
        print(f"DefaultMemoryProvider: Stored key '{key}' with value '{value}'.")

    def get(self, key: str) -> Any:
        value = self.cache.get(key)
        print(f"DefaultMemoryProvider: Retrieved key '{key}' with value '{value}'.")
        return value


# Cloud memory provider for cloud-based or external memory backends.
class CloudMemoryProvider(MemoryProvider):
    def __init__(self, config: dict):
        self.config = config
        self.connected = False
        self.connection = (
            None  # In a real provider, this would be the database connection object
        )

    def connect(self):
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

    def set(self, key: str, value: Any):
        if not self.connected:
            raise ConnectionError("CloudMemoryProvider: Not connected.")
        # Dummy implementation: In production, replace with actual database set operation
        print(
            f"CloudMemoryProvider: Setting key '{key}' to '{value}' in cloud storage."
        )

    def get(self, key: str) -> Any:
        if not self.connected:
            raise ConnectionError("CloudMemoryProvider: Not connected.")
        # Dummy implementation: In production, replace with actual database get operation
        print(f"CloudMemoryProvider: Getting key '{key}' from cloud storage.")
        return None


# Main MemoryService class that selects and manages the appropriate memory provider.
class MemoryService:
    def __init__(self, memory_config: Optional[Dict[str, Any]] = None):
        self.memory_config = memory_config or {}
        self.provider = self._initialize_provider()

    def _initialize_provider(self) -> MemoryProvider:
        provider_name = self.memory_config.get("provider")
        config = self.memory_config.get("config", {})
        if provider_name:
            # For demonstration, treat any specified provider as a cloud-based provider.
            print(
                f"MemoryService: Initializing cloud memory provider '{provider_name}'."
            )
            return CloudMemoryProvider(config)
        else:
            # Fallback to the default in-memory provider if no cloud configuration is provided.
            print(
                "MemoryService: No provider configuration found. Using default in-memory caching."
            )
            return DefaultMemoryProvider()

    def connect(self):
        print("MemoryService: Connecting to the memory provider...")
        self.provider.connect()

    def get_provider(self) -> MemoryProvider:
        return self.provider

    def switch_provider(self, new_memory_config: Dict[str, Any]):
        """
        Allows dynamic switching of the memory provider by updating the configuration
        and reinitializing the provider.
        """
        print("MemoryService: Switching memory provider...")
        self.memory_config = new_memory_config
        self.provider = self._initialize_provider()
        self.connect()


# # Initialize both services
# memory_service = MemoryService(config)  # Your existing service
# mem0_service = Mem0Service(config)  # New Mem0 service

# # Use in your crew setup
# crew = Crew(
#     agents=[...],
#     tasks=[...],
#     memory=True,
#     memory_config={
#         "provider": "custom",
#         "memory_service": memory_service,
#         "mem0_service": mem0_service,
#     },
# )
