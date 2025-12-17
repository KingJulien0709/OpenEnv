import pkg_resources
import yaml
import uuid
from typing import Any, Dict, List, Optional

from core.env_server import Action, Environment, Observation
from ..models import MissionAction, MissionObservation, MissionState, ToolDefinition

try:
    from uav_mission_env.environment import MissionEnvironment as UAVMissionEnv
    import numpy as np
except ImportError:
    UAVMissionEnv = None  # Set to None if not installed
    # install with pip install https://github.com/KingJulien0709/uav_mission_env.git

class MissionEnvironment(Environment):
    def __init__(self, random_seed: int = 42, config: Optional[Dict[str, Any]] = None):
        super().__init__()  # Call parent __init__
        if UAVMissionEnv is None:
            raise ImportError("Please install uav_mission_env package: pip install git+https://github.com/KingJulien0709/uav_mission_env.git")
        kwargs = {}
        if config is not None:
            kwargs.update(config)
        self.env = UAVMissionEnv(**kwargs)   # default configuration
        self.dataset_path = pkg_resources.resource_filename('uav_mission_env', 'data')
        self._state = MissionState(
            episode_id=str(uuid.uuid4()),
            step_count=0,
            current_state_name="",
            current_state_data={},
            available_tools=[],
        )

    def reset(self, seed: Optional[int] = 42) -> MissionObservation:
        """Reset the environment to an initial state and return the initial observation."""
        self._state.episode_id = str(uuid.uuid4())
        self._state.step_count = 0
        obs = self.env.reset(seed=seed)
        #print(obs)
        return self._make_observation(obs)

    def step(self, action: MissionAction) -> MissionObservation:
        """Take a step in the environment using the provided action.
        Args:
            action (MyToolCallAction): The action to take.
        Returns:
            MissionObservation: The observation after taking the action. It contains
            - observation (MyObservation): The observation after taking the action.
            - available_tools (List[ToolDefinition]): The available tools after taking the action.
            - reward (float): The reward received after taking the action.
            - done (bool): Whether the episode has ended.
            - info (dict): Additional information.
        """


        if not isinstance(action, MissionAction):
            raise ValueError(f"Expected MissionAction, got {type(action)}")

        # Assuming action.action is a numpy array or list that the env can use
        obs, reward, terminated, truncated, info = self.env.step(action.to_dict())
        self._state.step_count += 1

        #print(obs)
        mission_obs = self._make_observation(obs)
        mission_obs.reward = reward
        mission_obs.done = terminated or truncated or self._state.step_count >= 10

        #update state
        self._state.current_state_name = obs.get('current_state_name', "")
        self._state.current_state_data = obs.get('obs_payload', {})


        return mission_obs

    @property
    def state(self) -> MissionState:
        """Get the current environment state."""
        return self._state

    def close(self):
        """Clean up resources when closing the environment."""
        pass


    def _make_observation(self, obs) -> MissionObservation:
        available_tools = [
            ToolDefinition.from_json_schema(tool_def)
            for tool_def in obs.get('available_tools', []) #FIXME replace with actual tool definitions
        ]
        self._state.current_state_data = obs.get('obs_payload', {})
        self._state.available_tools = available_tools

        return MissionObservation(
            current_state_data=obs.get('obs_payload', {}),
            done=False, # This will be updated in step
            reward=0.0, # Will be filled by step
            available_tools=available_tools,
            metadata={}
        )
    
    def actions(self) -> List[ToolDefinition]:
        return self._state.current_state_data.get("available_tools", [])

