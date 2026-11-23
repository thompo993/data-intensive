#!/bin/bash
# ======================
# submit_job.sh  (one job = one day of data)
# ======================# 
# Usage: ./submit_all.sh [START_DATE] [END_DATE] (YYYY-MM-DD, inclusive)
# should be fed into submit job.sh script. maybe the name isnt best

set -euo pipefail

START_DATE="${1:-2023-01-01}"
END_DATE="${2:-2024-01-01}"

# n days -1
N=$(( ( $(date -d "$END_DATE" +%s) - $(date -d "$START_DATE" +%s) ) / 86400 ))


mkdir -p secrets/logs

sbatch --array=0-"$N"%10 \
       --export=ALL,START_DATE="$START_DATE" \
       src/submit-job.sh