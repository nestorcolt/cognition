from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field
import httpx
import functools
from crewai.tools.structured_tool import CrewStructuredTool


class ToolDefinition(BaseModel):
    """Schema for tool definitions received from API"""

    name: str = Field(..., description="Name of the tool")
    description: str = Field(..., description="Tool description")
    endpoint: str = Field(..., description="API endpoint for the tool")
    parameters: Dict[str, Any] = Field(
        default_factory=dict, description="Parameter definitions"
    )
    cache_enabled: bool = Field(default=False, description="Whether caching is enabled")
    cache_rules: Optional[Dict[str, Any]] = Field(
        default=None, description="Custom caching rules"
    )


class ToolService:
    def __init__(self, api_base_url: str, cache_enabled: bool = True):
        self.api_base_url = api_base_url
        self.cache_enabled = cache_enabled
        self.tools: Dict[str, CrewStructuredTool] = {}
        self._http_client = httpx.AsyncClient()

    async def fetch_tool_definitions(self) -> List[ToolDefinition]:
        """Fetch tool definitions from the API"""
        try:
            response = await self._http_client.get(f"{self.api_base_url}/tools")
            response.raise_for_status()
            return [ToolDefinition(**tool_data) for tool_data in response.json()]
        except Exception as e:
            raise Exception(f"Failed to fetch tool definitions: {str(e)}")

    def _create_tool_executor(self, tool_def: ToolDefinition):
        """Creates the actual function that will execute the tool"""

        async def execute_tool(**kwargs):
            try:
                response = await self._http_client.post(tool_def.endpoint, json=kwargs)
                response.raise_for_status()
                return response.json()
            except Exception as e:
                raise Exception(f"Tool execution failed: {str(e)}")

        return execute_tool

    def _create_cache_function(self, tool_def: ToolDefinition):
        """Creates a cache function based on tool definition"""
        if not tool_def.cache_enabled:
            return None

        def cache_func(args: Dict[str, Any], result: Any) -> bool:
            if not tool_def.cache_rules:
                return True

            # Apply custom cache rules here
            # This is a simple example - expand based on your needs
            for rule_key, rule_value in tool_def.cache_rules.items():
                if rule_key in args and args[rule_key] != rule_value:
                    return False
            return True

        return cache_func

    async def load_tools(self):
        """Fetch and load all tools into memory"""
        tool_definitions = await self.fetch_tool_definitions()

        for tool_def in tool_definitions:
            # Create parameter schema dynamically
            param_schema = type(
                f"{tool_def.name}Params",
                (BaseModel,),
                {
                    field_name: (field_type, Field(..., description=field_desc))
                    for field_name, (
                        field_type,
                        field_desc,
                    ) in tool_def.parameters.items()
                },
            )

            # Create the structured tool
            tool = CrewStructuredTool.from_function(
                name=tool_def.name,
                description=tool_def.description,
                args_schema=param_schema,
                func=self._create_tool_executor(tool_def),
            )

            # Add caching if enabled
            if self.cache_enabled and tool_def.cache_enabled:
                tool.cache_function = self._create_cache_function(tool_def)

            self.tools[tool_def.name] = tool

    def get_tool(self, name: str) -> Optional[CrewStructuredTool]:
        """Retrieve a specific tool by name"""
        return self.tools.get(name)

    def list_tools(self) -> List[str]:
        """List all available tool names"""
        return list(self.tools.keys())

    async def close(self):
        """Cleanup resources"""
        await self._http_client.aclose()
