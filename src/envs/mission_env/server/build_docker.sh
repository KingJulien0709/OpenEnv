#!/bin/bash
# Script to build the Mission Environment Docker image
# Usage: ./build_docker.sh [tag]
#
# Note: Requires openenv-base:latest to be built first.
# See: src/core/containers/images/README.md

set -e

TAG="${1:-latest}"
IMAGE_NAME="mission-env:${TAG}"

echo "🐳 Building Mission Environment Docker Image"
echo "=============================================="
echo "Image: $IMAGE_NAME"
echo ""

# Get script directory
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"

# Navigate to OpenEnv root (4 levels up from server/)
OPENENV_ROOT="$(cd "$SCRIPT_DIR/../../../.." && pwd)"

echo "📁 OpenEnv root: $OPENENV_ROOT"
echo ""

# Check if base image exists
if ! docker image inspect openenv-base:latest >/dev/null 2>&1; then
    echo "⚠️  Base image openenv-base:latest not found!"
    echo ""
    echo "Building base image first..."
    docker build \
        -f "$OPENENV_ROOT/src/core/containers/images/Dockerfile" \
        -t openenv-base:latest \
        "$OPENENV_ROOT"
    echo ""
fi

# Build Mission environment image
echo "⏳ Building Mission Environment image..."
docker build \
    --ssh default \
    -f "$SCRIPT_DIR/Dockerfile" \
    -t "$IMAGE_NAME" \
    "$OPENENV_ROOT"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Build successful!"
    echo ""
    echo "🚀 Run the Mission Environment server:"
    echo ""
    echo "  docker run -p 8000:8000 $IMAGE_NAME"
    echo ""
    echo "📊 Test the server:"
    echo ""
    echo "  curl http://localhost:8000/health"
    echo ""
else
    echo ""
    echo "❌ Build failed!"
    exit 1
fi
