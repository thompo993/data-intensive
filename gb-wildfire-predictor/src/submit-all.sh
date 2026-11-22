#!/bin/bash
# Usage: ./submit_all.sh [START_DATE] [END_DATE]   (YYYY-MM-DD, inclusive)
set -euo pipefail

START_DATE="${1:-2023-06-01}"
END_DATE="${2:-2023-06-10}"

# Slurm will NOT create the log directory; it must exist before sbatch runs
mkdir -p secrets/logs

current_date="$START_DATE"
while [[ ! "$current_date" > "$END_DATE" ]]; do   # ISO dates compare correctly as strings
    echo "Submitting: $current_date"
    sbatch --export=ALL,TARGET_DATE="$current_date" submit_job.sh
    current_date=$(date -I -d "$current_date + 1 day")
done