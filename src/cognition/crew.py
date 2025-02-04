from cognition.svc.config_service import ConfigManager
from cognition.svc.memory_service import MemoryService
from crewai.project import CrewBase, agent, crew, task
from crewai import Agent, Crew, Process, Task


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
        self.agents_config = self.config_manager.get_config("agents")
        self.tasks_config = self.config_manager.get_config("tasks")
        self.crew_config = self.config_manager.get_config("crew")

    @agent
    def researcher(self) -> Agent:
        agent = Agent(config=self.agents_config["researcher"], verbose=True)
        # print(self.agents_config)
        print(self.crew_config)

        # Print all properties of the agent
        # for key, value in vars(agent).items():
        #     print(f"{key}: {value}")

        # exit(0)  # Remove this if you want the program to continue
        return agent

    @agent
    def reporting_analyst(self) -> Agent:
        agent = Agent(config=self.agents_config["reporting_analyst"], verbose=True)

        # Print all properties of the agent
        # for key, value in vars(agent).items():
        #     print(f"{key}: {value}")

        # exit(0)  # Remove this if you want the program to continue
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
        )

        # for key, value in vars(crew).items():
        #     print(f"{key}: {value}")

        exit(0)
        return crew
