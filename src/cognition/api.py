from cognition_api.service import create_app
from cognition_api.routes.agent import router
from cognition.crew import Cognition

# Create base app
app = create_app()


@router.post("/run")
async def run_agent(request):
    crew = Cognition().crew()
    result = crew.kickoff(inputs=request.inputs)
    return {"task": request.task, "result": result}


# Add your specific routes
app.include_router(router, prefix="/v1/agent", tags=["agent"])
