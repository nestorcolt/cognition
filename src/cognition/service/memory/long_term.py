import json
from crewai.memory.long_term.long_term_memory_item import LongTermMemoryItem
from crewai.memory.memory import Memory
from sqlalchemy import create_engine, text
from typing import Dict, List, Optional
from datetime import datetime
from crewai import Crew


# Step 1: Create Base Storage Handler
class BaseStorageHandler:
    def connect(self):
        raise NotImplementedError

    def disconnect(self):
        raise NotImplementedError

    def save(self, task_description: str, metadata: dict, datetime: str, score: float):
        raise NotImplementedError

    def load(self, task_description: str, latest_n: int) -> List[Dict]:
        raise NotImplementedError

    def reset(self):
        raise NotImplementedError


# Step 2: Implement External SQL Handler
class ExternalSQLHandler(BaseStorageHandler):
    def __init__(self, connection_string: str, pool_size: int = 5):
        self.connection_string = connection_string
        self.pool_size = pool_size
        self.pool = None

    def connect(self):
        """Initialize connection pool"""
        self.pool = create_engine(self.connection_string).pool()

    def save(self, task_description: str, metadata: dict, datetime: str, score: float):
        with self.pool.connect() as conn:
            conn.execute(
                text(
                    """
                    INSERT INTO long_term_memories 
                    (task_description, metadata, datetime, score)
                    VALUES (:task, :meta, :dt, :score)
                """
                ),
                {
                    "task": task_description,
                    "meta": json.dumps(metadata),
                    "dt": datetime,
                    "score": score,
                },
            )


# Step 3: Custom Long Term Memory
class CustomLongTermMemory(Memory):
    def __init__(self, storage: BaseStorageHandler):
        self.storage = storage
        self.storage.connect()

    def save(self, item: LongTermMemoryItem):
        metadata = item.metadata
        metadata.update({"agent": item.agent, "expected_output": item.expected_output})

        self.storage.save(
            task_description=item.task,
            metadata=metadata,
            datetime=item.datetime,
            score=metadata["quality"],
        )

    def search(self, task: str, latest_n: int = 3) -> List[Dict]:
        return self.storage.load(task, latest_n)
