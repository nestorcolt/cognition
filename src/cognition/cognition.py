from cognition_core.crew import CognitionCoreCrewBase
from cognition_core.base import ComponentManager
from cognition_core.llm import init_portkey_llm
from cognition_core.agent import CognitionAgent
from cognition_core.task import CognitionTask
from cognition_core.crew import CognitionCrew
from crewai.project import agent, crew, task
from crewai import Process
import asyncio


@CognitionCoreCrewBase
class Cognition(ComponentManager):
    """Base Cognition implementation - Virtual Interface"""

    def __init__(self):
        # Initialize empty components first
        self.available_components = {"agents": [], "tasks": []}
        # Call parent so CrewBase processes @agent/@task decorators
        super().__init__()
        # Try deferring the update until an event loop is available
        try:
            loop = asyncio.get_running_loop()
            loop.call_soon(self._update_components)
        except RuntimeError:
            # No running loop - update components immediately
            self._update_components()

    # Now these methods implement the abstract interface
    def _update_components(self) -> None:
        """Implements ComponentManager.update_components"""
        agents = getattr(self, "agents", [])
        tasks = getattr(self, "tasks", [])
        self.available_components = {
            "agents": [a for a in agents if a.is_available],
            "tasks": [t for t in tasks if t.is_available],
        }

    def activate_component(self, component_type: str, name: str) -> bool:
        """Implements ComponentManager.activate_component"""
        if component_type in self.available_components:
            for component in self.available_components[component_type]:
                if component.name == name:
                    component.enabled = True
                    return True
        return False

    def deactivate_component(self, component_type: str, name: str) -> bool:
        """Implements ComponentManager.deactivate_component"""
        if component_type in self.available_components:
            for component in self.available_components[component_type]:
                if component.name == name:
                    component.enabled = False
                    return True
        return False

    def get_active_workflow(self) -> dict:
        """Implements ComponentManager.get_active_workflow"""
        return {
            "agents": [a.name for a in self.available_components["agents"]],
            "tasks": [t.name for t in self.available_components["tasks"]],
        }

    # Public kickoff method: delegate to the crew's public kickoff method
    def kickoff(self, inputs=None):
        """Kick off the crew execution using the crew's kickoff method."""
        crew_obj = self.crew()  # Get the crew
        return crew_obj.kickoff(inputs)  # Use the public 'kickoff' method

    # Agent definitions
    @agent
    def manager(self) -> CognitionAgent:
        llm = init_portkey_llm(
            model=self.agents_config["manager"]["llm"],
            portkey_config=self.portkey_config,
        )
        return self.get_cognition_agent(config=self.agents_config["manager"], llm=llm)

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

    # Task definitions
    @task
    def research_task(self) -> CognitionTask:
        # Extract task name from config
        task_config = self.tasks_config["research_task"]
        task_name = task_config.get("name", "research_task")

        return CognitionTask(
            name=task_name,  # Pass name from config
            config=task_config,
            tool_names=self.list_tools(),
            tool_service=self.tool_service,
        )

    @task
    def reporting_task(self) -> CognitionTask:
        # Extract task name from config
        task_config = self.tasks_config["reporting_task"]
        task_name = task_config.get("name", "reporting_task")

        return CognitionTask(
            name=task_name,  # Pass name from config
            config=task_config,
        )

    @crew
    def crew(self) -> CognitionCrew:
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
