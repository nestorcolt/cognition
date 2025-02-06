from cognition_api.service import CrewAIBackend
from fastapi import APIRouter, Request
from cognition.crew import Cognition
from cognition_api.main import app  # Import the base app from cognition-api!
from datetime import datetime
from typing import Dict, Any

# Create router for our endpoints
router = APIRouter()


# Create a CrewAI backend implementation
class CognitionBackend(CrewAIBackend):
    def __init__(self):
        self.cognition = Cognition()

    async def run_task(self, task: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
        print(f"Running task: {task} with inputs: {inputs}")
        # TODO: Remove this once we have a proper way to handle inputs
        # Ensure required inputs are present
        if "topic" not in inputs:
            inputs["topic"] = inputs.get("query", "AI LLMs")  # fallback value
        if "current_year" not in inputs:
            inputs["current_year"] = str(datetime.now().year)

        crew = self.cognition.crew()
        result = crew.kickoff(inputs=inputs)
        return {"task": task, "result": result}


# Add your specific routes
@router.post("/run")
async def run_agent(request: Request):
    """Direct endpoint for running the Cognition agent"""
    data = await request.json()
    backend = request.app.state.agent_backend
    result = await backend.run_task(task="direct_run", inputs=data)
    return result


# Configure the backend
app.state.agent_backend = CognitionBackend()

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
