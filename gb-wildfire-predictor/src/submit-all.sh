#!/bin/bash
# ======================
# submit_job.sh  (one job = one day of data)
# ======================# 
# Usage: ./submit_all.sh [START_DATE] [END_DATE] (YYYY-MM-DD, inclusive)
# should be fed into submit job.sh script. maybe the name isnt best

set -euo pipefail

START_DATE="${1:-2023-06-01}"
END_DATE="${2:-2023-06-10}"

mkdir -p secrets/logs

current_date="$START_DATE"
while [[ ! "$current_date" > "$END_DATE" ]]; do   
    echo "Submitting: $current_date"
    sbatch --export=ALL,TARGET_DATE="$current_date" src/submit-job.sh
    current_date=$(date -I -d "$current_date + 1 day")
done