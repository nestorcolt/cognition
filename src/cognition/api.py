from cognition_api.routes.agent import set_agent_handler
from cognition_api.models import AgentRequest
from cognition.crew import Cognition


async def my_agent_handler(request: AgentRequest):
    crew = Cognition().crew()
    result = crew.kickoff(inputs=request.inputs)
    return {"task": request.task, "result": result}


# Register your handler
set_agent_handler(my_agent_handler)
