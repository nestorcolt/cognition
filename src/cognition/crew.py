from crewai.project import agent, crew, task, CrewBase
from cognition_core.crew import CognitionCoreCrewBase
from cognition_core.llm import init_portkey_llm
from cognition_core.agent import CognitionAgent
from cognition_core.task import CognitionTask
from cognition_core.crew import CognitionCrew
from crewai import Process
import asyncio


@CrewBase
class Cognition(CognitionCoreCrewBase):
    """Cognition crew"""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._initialized = False

    async def setup(self):
        """Ensure services are initialized"""
        if not self._initialized:
            await super().setup()
            self._initialized = True

    @agent
    def researcher(self) -> CognitionAgent:
        # Get raw config for LLM initialization
        raw_config = self.config_manager.get_config("agents")["researcher"]
        # Initialize LLM with config settings and portkey config
        llm = init_portkey_llm(
            model=raw_config["llm"],
            portkey_config=self.portkey_config,
        )

        # Create CognitionAgent with tool service
        agent = CognitionAgent(
            config=self.agents_config["researcher"],
            llm=llm,
            verbose=True,
            tool_names=self.list_tools(),  # Pass tool names
            tool_service=self.tool_service,  # Pass tool service
        )
        return agent

    @agent
    def reporting_analyst(self) -> CognitionAgent:
        # Get raw config for LLM initialization
        raw_config = self.config_manager.get_config("agents")["reporting_analyst"]
        # Initialize LLM with config settings and portkey config
        llm = init_portkey_llm(
            model=raw_config["llm"],
            portkey_config=self.portkey_config,
        )
        # Pass file path to Agent for CrewAI's config loading
        agent = CognitionAgent(
            config=self.agents_config["reporting_analyst"], llm=llm, verbose=True
        )
        return agent

    @task
    def research_task(self) -> CognitionTask:
        # Create CognitionTask with tool service
        task = CognitionTask(
            config=self.tasks_config["research_task"],
            tool_names=self.list_tools(),  # Pass tool names
            tool_service=self.tool_service,  # Pass tool service
        )

        # Print all properties of the task
        # for key, value in vars(task).items():
        #     print(f"{key}: {value}")

        # exit(0)  # Remove this if you want the program to continue
        return task

    def search_web(self, query: str) -> str:
        return f"Searching the web for {query}"

    @task
    def reporting_task(self) -> CognitionTask:
        task = CognitionTask(
            config=self.tasks_config["reporting_task"], output_file="report.md"
        )

        # Print all properties of the task
        # for key, value in vars(task).items():
        #     print(f"{key}: {value}")

        # exit(0)  # Remove this if you want the program to continue
        return task

    @crew
    def crew(self) -> CognitionCrew:
        """Creates the Cognition crew with tool integration"""
        if not self._initialized:
            asyncio.create_task(self.setup())

        crew = CognitionCrew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            verbose=True,
            tool_service=self.tool_service,  # Pass tool service to CognitionCrew
            short_term_memory=self.memory_service.get_short_term_memory(),
            entity_memory=self.memory_service.get_entity_memory(),
            long_term_memory=self.memory_service.get_long_term_memory(),
            embedder=self.memory_service.embedder,
        )
        # exit(0)
        return crew
