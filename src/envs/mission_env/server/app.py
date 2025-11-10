from core.env_server import create_app
from ..models import MissionAction, MissionObservation
from .mission_environment import MissionEnvironment

env = MissionEnvironment()

app = create_app(env, MissionAction, MissionObservation, env_name="mission_env")

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)