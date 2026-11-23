#!/bin/bash
# ======================
# make-table-job.sh  (builds the interactive Bokeh table from data/*.parquet)
# Usage (from project root): sbatch src/make-table-job.sh [DATA_DIR] [OUT_FILE]
# ======================
#SBATCH --job-name=bt_gb_wildfire_make_table
#SBATCH --partition=teach_cpu
#SBATCH --account=phys040684
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=00:10:00
#SBATCH --mem=4G
#SBATCH --output=secrets/logs/job_%j_%x.out
#SBATCH --error=secrets/logs/job_%j_%x.err

DATA_DIR="${1:-data}"
OUT_FILE="${2:-data_table.html}"

source ~/initMamba.sh
eval "$(mamba shell hook --shell bash)"
mamba activate gb-wildfire-predictor
cd "$SLURM_SUBMIT_DIR"

set -eo pipefail

echo "Building table from $DATA_DIR/ -> $OUT_FILE"
python src/plot_table_bokeh.py "$DATA_DIR" "$OUT_FILE"
echo "job completed: $OUT_FILE"