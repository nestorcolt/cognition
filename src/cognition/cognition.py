from cognition_core.crew import CognitionCoreCrewBase
from cognition_core.agent import CognitionAgent
from cognition_core.task import CognitionTask
from cognition_core.crew import CognitionCrew
from cognition_core.api import CoreAPIService
from crewai.project import agent, crew, task
from crewai import Process


@CognitionCoreCrewBase
class Cognition:
    """Base Cognition implementation - Virtual Interface"""

    def __init__(self):
        # Initialize FastAPI
        self.api = CoreAPIService()
        self.app = self.api.get_app()

        super().__init__()

    @agent
    def manager(self) -> CognitionAgent:
        return self.get_cognition_agent(config=self.agents_config["manager"])

    @agent
    def analyzer(self) -> CognitionAgent:
        return self.get_cognition_agent(config=self.agents_config["analyzer"])

    @task
    def analysis_task(self) -> CognitionTask:
        """Input analysis task"""
        task_config = self.tasks_config["analysis_task"]
        return CognitionTask(
            name="analysis_task",
            config=task_config,
            tool_names=self.list_tools(),
            tool_service=self.tool_service,
        )

    @crew
    def crew(self) -> CognitionCrew:

        manager = self.manager()
        agents = [itm for itm in self.agents if itm != manager]

        return CognitionCrew(
            agents=agents,
            tasks=self.tasks,
            # manager_agent=manager,
            # process=Process.hierarchical,
            # memory=True,
            verbose=True,
            # embedder=self.memory_service.embedder,
            # tool_service=self.tool_service,
            # short_term_memory=self.memory_service.get_short_term_memory(),
            # entity_memory=self.memory_service.get_entity_memory(),
            # long_term_memory=self.memory_service.get_long_term_memory(),
            # chat_llm="claude-3-5-haiku-20241022",
        )

    def chat(self, input_text: str):
        """Process message input through the crew"""
        print(f"Chat input: {input_text}")
        return self.crew().kickoff(inputs={"message": input_text})

    # @flow
    # def code_review_flow(self) -> CognitionFlow:
    #     """Code review automation flow"""
    #     return CodeReviewFlow.from_config(
    #         self.flows_config["code_review"]
    #     )


###############################################################################################
# Run as API chat interface


def run_api():
    import uvicorn

    cognition = Cognition()
    app = cognition.get_app()
    uvicorn.run(app, host="0.0.0.0", port=8000)


if __name__ == "__main__":
    run_api()

###############################################################################################
