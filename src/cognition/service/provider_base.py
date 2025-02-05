from typing import Dict, Any


class MemoryProvider:
    """Base class for memory providers"""

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
