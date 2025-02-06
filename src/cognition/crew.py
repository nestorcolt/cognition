from cognition_core.crew import CognitionCoreCrewBase
from cognition_core.llm import init_portkey_llm
from crewai import Agent, Crew, Process, Task
from crewai.project import agent, crew, task


class Cognition(CognitionCoreCrewBase):
    """Cognition crew"""

    def __init__(self):
        super(Cognition).__init__()

    @agent
    def researcher(self) -> Agent:
        # Get raw config for LLM initialization
        raw_config = self.config_manager.get_config("agents")["researcher"]
        # Initialize LLM with config settings and portkey config
        llm = init_portkey_llm(
            model=raw_config["llm"],
            portkey_config=self.portkey_config,
        )
        # Pass file path to Agent for CrewAI's config loading
        agent = Agent(config=self.agents_config["researcher"], llm=llm, verbose=True)
        return agent

    @agent
    def reporting_analyst(self) -> Agent:
        # Get raw config for LLM initialization
        raw_config = self.config_manager.get_config("agents")["reporting_analyst"]
        # Initialize LLM with config settings and portkey config
        llm = init_portkey_llm(
            model=raw_config["llm"],
            portkey_config=self.portkey_config,
        )
        # Pass file path to Agent for CrewAI's config loading
        agent = Agent(
            config=self.agents_config["reporting_analyst"], llm=llm, verbose=True
        )
        return agent

    @task
    def research_task(self) -> Task:
        task = Task(config=self.tasks_config["research_task"])

        # Print all properties of the task
        # for key, value in vars(task).items():
        #     print(f"{key}: {value}")

        # exit(0)  # Remove this if you want the program to continue
        return task

    def search_web(self, query: str) -> str:
        return f"Searching the web for {query}"

    @task
    def reporting_task(self) -> Task:
        task = Task(config=self.tasks_config["reporting_task"], output_file="report.md")

        # Print all properties of the task
        # for key, value in vars(task).items():
        #     print(f"{key}: {value}")

        # exit(0)  # Remove this if you want the program to continue
        return task

    @crew
    def crew(self) -> Crew:
        """Creates the Cognition crew"""
        crew = Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            memory=True,
            verbose=True,
            short_term_memory=self.memory_service.get_short_term_memory(),
            entity_memory=self.memory_service.get_entity_memory(),
            long_term_memory=self.memory_service.get_long_term_memory(),
            embedder=self.memory_service.embedder,
        )
        # exit(0)
        return crew
