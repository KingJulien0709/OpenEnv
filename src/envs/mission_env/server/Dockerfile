# Dockerfile for Mission Environment

ARG BASE_IMAGE=openenv-base:latest
FROM ${BASE_IMAGE}

# Install git and OpenCV dependencies (needed for pip install from git repos and cv2)
RUN apt-get update && apt-get install -y \
    git \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Add github.com to known_hosts to avoid SSH host key verification prompt
RUN mkdir -p -m 0700 ~/.ssh && ssh-keyscan github.com >> ~/.ssh/known_hosts

# Install dependencies (using SSH mount for private repo access)
# Force reinstall to get latest version from GitHub
COPY src/envs/mission_env/server/requirements.txt /tmp/requirements.txt
RUN --mount=type=ssh pip install --no-cache-dir --force-reinstall -r /tmp/requirements.txt && rm /tmp/requirements.txt

# Copy OpenEnv core (base image already set WORKDIR=/app)
COPY src/core/ /app/src/core/

# Copy Mission environment code
COPY src/envs/mission_env/ /app/src/envs/mission_env/

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the FastAPI server
CMD ["uvicorn", "envs.mission_env.server.app:app", "--host", "0.0.0.0", "--port", "8000"]
