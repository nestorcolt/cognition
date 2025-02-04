from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators


@CrewBase
class Cognition:
    """Cognition crew"""

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    agents_config = "config/agents.yaml"
    tasks_config = "config/tasks.yaml"
    crew_config = "config/crew.yaml"

    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
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

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
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
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge
        # print(self.crew_config)

        crew = Crew(
            agents=self.agents,  # Automatically created by the @agent decorator
            tasks=self.tasks,  # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # config=self.crew_config[0],
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )

        # for key, value in vars(crew).items():
        #     print(f"{key}: {value}")

        exit(0)
        return crew
