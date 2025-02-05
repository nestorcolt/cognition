from crewai.memory.long_term.long_term_memory_item import LongTermMemoryItem
from crewai.memory.long_term.long_term_memory import LongTermMemory
from sqlalchemy import create_engine, text
from typing import Dict, List, Optional
from datetime import datetime
from crewai import Crew
import json


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
        self.engine = create_engine(self.connection_string)
        self.pool = self.engine.pool

    def save(self, task_description: str, metadata: dict, datetime: str, score: float):
        """Save memory to database"""
        with self.engine.connect() as conn:
            # Convert Unix timestamp to proper datetime
            timestamp = datetime if isinstance(datetime, str) else str(datetime)
            formatted_datetime = text("to_timestamp(:dt)")

            conn.execute(
                text(
                    """
                    INSERT INTO long_term_memories 
                    (task_description, metadata, datetime, score)
                    VALUES (:task, :meta, """
                    + formatted_datetime.text
                    + """, :score)
                    """
                ),
                {
                    "task": task_description,
                    "meta": json.dumps(metadata),
                    "dt": timestamp,
                    "score": score,
                },
            )
            conn.commit()

    def load(self, task_description: str, latest_n: int) -> List[Dict]:
        """Load the latest n memories related to the task description"""
        with self.engine.connect() as conn:
            result = conn.execute(
                text(
                    """
                    SELECT task_description, metadata, datetime, score
                    FROM long_term_memories
                    WHERE task_description LIKE :task
                    ORDER BY datetime DESC
                    LIMIT :n
                    """
                ),
                {"task": f"%{task_description}%", "n": latest_n},
            )

            memories = []
            for row in result:
                memories.append(
                    {
                        "task": row.task_description,
                        "metadata": json.loads(row.metadata),
                        "datetime": row.datetime,
                        "score": row.score,
                    }
                )

            return memories


# Step 3: Custom Long Term Memory
class CustomLongTermMemory(LongTermMemory):
    def __init__(self, storage: BaseStorageHandler, *args, **kwargs):
        super(CustomLongTermMemory, self).__init__(*args, **kwargs)
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
