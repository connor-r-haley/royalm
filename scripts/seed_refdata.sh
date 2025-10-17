#!/usr/bin/env bash
set -euo pipefail

python -m backend.refdata.init_db
python -m backend.refdata.seed

echo "Seed complete."

