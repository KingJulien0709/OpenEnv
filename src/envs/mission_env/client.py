from __future__ import annotations

from typing import TYPE_CHECKING, Optional

from core.http_env_client import HTTPEnvClient, StepResult
from .models import MissionObservation, MissionAction, MissionState, ToolDefinition, ToolParameter

if TYPE_CHECKING:
    from core.containers.runtime import ContainerProvider


class MissionEnv(HTTPEnvClient[MissionAction, MissionObservation]):

    def __init__(self, base_url: str, timeout: float = 60.0, provider: Optional["ContainerProvider"] = None):
        super().__init__(base_url=base_url, request_timeout_s=timeout, provider=provider)

    def _step_payload(self, action: MissionAction) -> dict:
        output = {}
        output.update(action.to_dict())
        return output

    def _parse_result(self, payload: dict) -> StepResult[MissionObservation]:
        obs_data = payload.get("observation")
        if obs_data is None:
            raise ValueError("Missing 'observation' in payload")

        # Parse available_tools - they come as dicts from asdict() serialization
        available_tools = []
        for tool_data in obs_data.get('available_tools', []):
            # Convert parameter dicts to ToolParameter objects
            parameters = [
                ToolParameter(**param_data) if isinstance(param_data, dict) else param_data
                for param_data in tool_data.get('parameters', [])
            ]
            # Create ToolDefinition with the parameters
            tool = ToolDefinition(
                name=tool_data.get('name', ''),
                description=tool_data.get('description', ''),
                parameters=parameters
            )
            available_tools.append(tool)

        observation = MissionObservation(
            current_state_data=obs_data.get('current_state_data', {}),
            available_tools=available_tools,
        )

        return StepResult(
            observation=observation,
            reward=payload.get("reward", 0.0),
            done=payload.get("done", False),
        )

    def _parse_state(self, payload):
        return MissionState(**payload)