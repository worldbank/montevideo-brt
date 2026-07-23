#!/bin/bash
set -euo pipefail

# Resolve the script's own directory so this works regardless of where the
# repo is cloned or where the script is called from.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Load the Mapbox token (and any other vars) from a local .env file, if present.
if [ -f .env ]; then
    set -a
    source .env
    set +a
fi

source venv/bin/activate
python query_mapbox_api.py -c Montevideo
