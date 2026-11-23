#!/bin/bash
# ======================
# submit_job.sh  (one job = one day of data)
# ======================
#SBATCH --job-name=bt_gb_wildfire_get_data
#SBATCH --partition=teach_cpu
#SBATCH --account=phys040684
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --mem=4G
#SBATCH --output=secrets/logs/job_%j_%x.out
#SBATCH --error=secrets/logs/job_%j_%x.err

if [[ -z "${START_DATE:-}" || -z "${SLURM_ARRAY_TASK_ID:-}" ]]; then
    echo "Error: START_DATE or SLURM_ARRAY_TASK_ID not set" >&2
    exit 1
fi

TARGET_DATE=$(date -I -d "$START_DATE + $SLURM_ARRAY_TASK_ID days")
END_DATE_PLUS_ONE=$(date -I -d "$TARGET_DATE + 1 day")

source ~/initMamba.sh
eval "$(mamba shell hook --shell bash)"
mamba activate gb-wildfire-predictor
cd "$SLURM_SUBMIT_DIR"

export GEE_SERVICE_ACCOUNT_KEY="/user/work/sv23035/data-intensive/uk-wildfire-predictor/secrets/uk-wildfire-predictor-dd633889f29d.json"

END_DATE_PLUS_ONE=$(date -I -d "$TARGET_DATE + 1 day")

echo "Processing window: $TARGET_DATE to $END_DATE_PLUS_ONE"
python src/processor.py --start "$TARGET_DATE" --end "$END_DATE_PLUS_ONE"
echo "job completed for $TARGET_DATE"