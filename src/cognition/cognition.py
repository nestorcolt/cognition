from cognition_core.crew import CognitionCoreCrewBase
from cognition_core.base import CognitionComponent
from cognition_core.llm import init_portkey_llm
from cognition_core.agent import CognitionAgent
from cognition_core.task import CognitionTask
from cognition_core.crew import CognitionCrew
from crewai.project import agent, crew, task
from typing import Dict, List
from crewai import Process


@CognitionCoreCrewBase
class Cognition:
    """Base Cognition implementation - Virtual Interface"""

    def __init__(self):
        super().__init__()
        self.available_components = {
            "agents": [a for a in self.agents if a.is_available],
            "tasks": [t for t in self.tasks if t.is_available],
        }

    @agent
    def manager(self) -> CognitionAgent:
        """Initialize the manager agent"""
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

    def _discover_components(self) -> Dict[str, List[CognitionComponent]]:
        """Discover all available components"""
        return {
            "agents": self.get_available_agents(),
            "tasks": self.get_available_tasks(),
        }

    def activate_component(self, component_type: str, name: str):
        """Activate a specific component"""
        if component_type in self.available_components:
            for component in self.available_components[component_type]:
                if component.name == name:
                    component.enabled = True
                    return True
        return False

    def deactivate_component(self, component_type: str, name: str):
        """Deactivate a specific component"""
        if component_type in self.available_components:
            for component in self.available_components[component_type]:
                if component.name == name:
                    component.enabled = False
                    return True
        return False

    def register_agent(self, agent: CognitionAgent):
        """Register a new agent"""
        self.available_components["agents"].append(agent)

    def register_task(self, task: CognitionTask):
        """Register a new task"""
        self.available_components["tasks"].append(task)

    def get_active_workflow(self) -> Dict[str, List[str]]:
        """Get currently active workflow components"""
        return {
            "agents": [a.name for a in self.get_available_agents()],
            "tasks": [t.name for t in self.get_available_tasks()],
        }

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
