from cognition_api.service import create_app, CrewAIBackend
from concurrent.futures import ThreadPoolExecutor
from fastapi import APIRouter, Request
from cognition.crew import Cognition
from cognition_api.main import app
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel
import asyncio
import uuid


# Create request/response models
class AgentRequest(BaseModel):
    topic: str = "AI LLMs"
    current_year: str = str(datetime.now().year)


class AgentResponse(BaseModel):
    task_id: str
    status: str
    message: str


# Create router for our endpoints
router = APIRouter()


# Create a CrewAI backend implementation
class CognitionBackend(CrewAIBackend):
    def __init__(self):
        self.cognition = Cognition()
        self.tasks = {}  # In-memory storage
        self.executor = ThreadPoolExecutor()

    async def run_task(self, task: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        task_id = str(uuid.uuid4())

        # Start task in background
        asyncio.create_task(self._process_task(task_id, inputs))

        # Return immediately
        return {
            "task_id": task_id,
            "status": "processing",
            "message": "Task started successfully",
        }

    @staticmethod
    def task_completed_callback(task_id, result):
        print(f"Task {task_id} completed with result: {result}")
        """
        
        I need to send to an external queue - 
        - the task_id
        - the result
        - the input
        
        also need to make and internal queu or store the task id so I can ask the agent
        about the task results in a different message.
        """

    async def _process_task(self, task_id: str, inputs: Dict):
        try:
            result = await asyncio.get_event_loop().run_in_executor(
                self.executor, lambda: self.cognition.crew().kickoff(inputs=inputs)
            )
            self.tasks[task_id] = {"status": "completed", "result": result}
            self.task_completed_callback(task_id, result)
        except Exception as e:
            self.tasks[task_id] = {"status": "failed", "error": str(e)}
            print(f"Task {task_id} failed with error: {e}")

# Add your specific routes
@router.post("/run", response_model=AgentResponse)
async def run_agent(request: Request, agent_request: AgentRequest):
    """Direct endpoint for running the Cognition agent"""
    backend = request.app.state.agent_backend
    result = await backend.run_task(task="direct_run", inputs=agent_request.dict())
    return result


# Create the app with your backend
app = create_app(agent_backend=CognitionBackend())

# Include our routes - add a print to verify registration
print("Registering routes at /v1/agent")
app.include_router(router, prefix="/v1/agent", tags=["agent"])

# Print all registered routes for debugging
for route in app.routes:
    print(f"Registered route: {route.path} [{route.methods}]")

# Make sure we have a proper __name__ == "__main__" block
if __name__ == "__main__":
    import uvicorn

    uvicorn.run("cognition.api:app", host="127.0.0.1", port=8000, reload=True)
