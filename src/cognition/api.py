from cognition_api.service import create_app, CrewAIBackend
from cognition.crew import Cognition
from fastapi import APIRouter, Request
from typing import Dict, Any

# Create router for our endpoints
router = APIRouter()


# Create a CrewAI backend implementation
class CognitionBackend(CrewAIBackend):
    def __init__(self):
        self.cognition = Cognition()

    async def run_task(self, task: str, inputs: Dict[str, Any]) -> Dict[str, Any]:
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


# Create base app with our backend
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
