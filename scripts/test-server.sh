#! /usr/bin/env bash
set -e
set -x

docker compose exec backend bash scripts/tests-start.sh "app/tests/api/routes/test_servers.py"
