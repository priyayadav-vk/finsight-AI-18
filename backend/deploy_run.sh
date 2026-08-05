#!/usr/bin/env bash
# Simple helper to build and run the app with docker-compose
# Usage: sudo ./deploy_run.sh [build|up|down|logs]

set -euo pipefail
CMD=${1:-up}
COMPOSE_FILE="$(pwd)/docker-compose.yml"

case "$CMD" in
  build)
    docker-compose -f "$COMPOSE_FILE" build --pull --no-cache
    ;;
  up)
    docker-compose -f "$COMPOSE_FILE" up -d --build
    ;;
  down)
    docker-compose -f "$COMPOSE_FILE" down
    ;;
  logs)
    docker-compose -f "$COMPOSE_FILE" logs -f --tail=200
    ;;
  restart)
    docker-compose -f "$COMPOSE_FILE" restart
    ;;
  *)
    echo "Usage: $0 {build|up|down|logs|restart}"
    exit 2
    ;;
esac

exit 0
