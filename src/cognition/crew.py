from crewai.project import agent, crew, task, CrewBase
from cognition_core.crew import CognitionCoreCrewBase
from cognition_core.llm import init_portkey_llm
from cognition_core.agent import CognitionAgent
from cognition_core.task import CognitionTask
from cognition_core.crew import CognitionCrew
from crewai import Process


@CrewBase
class Cognition(CognitionCoreCrewBase):
    """Cognition crew"""

    @agent
    def researcher(self) -> CognitionAgent:
        llm = init_portkey_llm(
            model=self.agents_config["researcher"]["llm"],
            portkey_config=self.portkey_config,
        )

        return self.get_cognition_agent(
            config=self.agents_config["researcher"], llm=llm
        )

    @agent
    def reporting_analyst(self) -> CognitionAgent:
        llm = init_portkey_llm(
            model=self.agents_config["reporting_analyst"]["llm"],
            portkey_config=self.portkey_config,
        )

        return self.get_cognition_agent(
            config=self.agents_config["reporting_analyst"], llm=llm
        )

    @task
    def research_task(self) -> CognitionTask:
        return CognitionTask(
            config=self.tasks_config["research_task"],
            tool_names=self.list_tools(),
            tool_service=self.tool_service,
        )

    @task
    def reporting_task(self) -> CognitionTask:
        return CognitionTask(
            config=self.tasks_config["reporting_task"], output_file="report.md"
        )

    @crew
    def crew(self) -> CognitionCrew:
        """Creates the Cognition crew with tool integration"""
        return CognitionCrew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            verbose=True,
            tool_service=self.tool_service,
            short_term_memory=self.memory_service.get_short_term_memory(),
            entity_memory=self.memory_service.get_entity_memory(),
            long_term_memory=self.memory_service.get_long_term_memory(),
            embedder=self.memory_service.embedder,
        )
