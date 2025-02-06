from cognition_api.service import create_app, CrewAIBackend
from fastapi import APIRouter, Request
from cognition.crew import Cognition
from cognition_api.main import app
from datetime import datetime
from typing import Dict, Any
from pydantic import BaseModel


# Create request/response models
class AgentRequest(BaseModel):
    topic: str = "AI LLMs"
    current_year: str = str(datetime.now().year)


class AgentResponse(BaseModel):
    task: str
    result: Any


# Create router for our endpoints
router = APIRouter()


# Create a CrewAI backend implementation
class CognitionBackend(CrewAIBackend):
    def __init__(self):
        self.cognition = Cognition()

    async def run_task(self, task: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(f"DEBUG: Inside run_task with inputs: {inputs}")
        crew = self.cognition.crew()
        result = crew.kickoff(inputs=inputs)
        print(f"DEBUG: Crew result: {result}")
        return {"task": task, "result": result}


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
