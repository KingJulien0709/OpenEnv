from typing import List, Optional
from dataclasses import dataclass, field
from typing import Any, Dict
from core.env_server import Action
from core.env_server import Observation, State

@dataclass(kw_only=True)
class MissionAction(Action):
    """Action representing a named operation (a 'tool call')."""
    tool_name: str
    parameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the action to a dictionary format for the environment."""
        return {
            "tool_name": self.tool_name,
            "parameters": self.parameters,
        }

@dataclass
class ToolParameter:
    """Definition of a tool parameter."""
    name: str
    type: str  # JSON Schema type: "string", "number", "boolean", "object", "array"
    description: str
    required: bool = True
    default: Any = None

@dataclass
class ToolDefinition:
    """Specification of an action that can be taken in an environment."""

    name: str
    description: str
    parameters: List[ToolParameter]

    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format for LLM tool calling."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": {
                "type": "object",
                "properties": {
                    p.name: {
                        "type": p.type,
                        "description": p.description,
                    }
                    for p in self.parameters
                },
                "required": [p.name for p in self.parameters if p.required],
            },
        }

    @classmethod
    def from_json_schema(cls, data: Dict[str, Any]) -> "ToolDefinition":
        """Create a ToolDefinition from JSON Schema format."""
        parameters = [
            ToolParameter(
                name=param_name,
                type=param_info.get("type", "string"),
                description=param_info.get("description", ""),
                required=param_name in data.get("parameters", {}).get("required", []),
            )
            for param_name, param_info in data.get("parameters", {}).get("properties", {}).items()
        ]
        return cls(
            name=data.get("name", ""),
            description=data.get("description", ""),
            parameters=parameters,
        )

@dataclass
class MissionObservation(Observation):
    """Observation includes the dynamic list of available tools."""
    current_state_data: Dict[str, Any] = field(default_factory=dict) # uav_mission_env specific observation data
    available_tools: List[ToolDefinition] = field(default_factory=list) # available tools at this observation step
    done: bool = False
    reward: float = 0.0

@dataclass
class MissionState(State):
    """State representation for the Mission Environment."""
    current_state_name: str = ""
    current_state_data: Dict[str, Any] = field(default_factory=dict)
    available_tools: List[ToolDefinition] = field(default_factory=list)


