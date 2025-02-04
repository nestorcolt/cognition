from cognition.svc.config_service import ConfigManager
from cognition.svc.memory_service import MemoryService
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task
from cognition.llm import init_portkey_llm
from pathlib import Path


@CrewBase
class Cognition:
    """Cognition crew"""

    def __init__(self):
        super().__init__()
        # Initialize config manager with config directory
        self.config_manager = ConfigManager()

        # Initialize memory service with config manager
        self.memory_service = MemoryService(self.config_manager)

        # Get configs using ConfigManager
        self.agents_config = str(Path(self.config_manager.config_dir) / "agents.yaml")
        self.tasks_config = str(Path(self.config_manager.config_dir) / "tasks.yaml")
        self.crew_config = str(Path(self.config_manager.config_dir) / "crew.yaml")

        # LLM GATEWAY CONFIG
        self.portkey_config = self.config_manager.get_portkey_config()

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
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            memory=True,
            memory_config={"provider": "custom", "service": self.memory_service},
            embedder={
                "provider": "ollama",  # Using Ollama as it's free and local
                "config": {
                    "model": "nomic-embed-text"  # A good default embedding model
                },
            },
        )

        # for key, value in vars(crew).items():
        #     print(f"{key}: {value}")

        return crew
