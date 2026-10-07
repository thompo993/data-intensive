#!/bin/bash
# ./run.sh script.py 1000
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <script_name.py> <iterations>"
    exit 1
fi

SCRIPT=$1
ITERATIONS=$2
OUTDIR="outputs"

# Ensure output directory exists
mkdir -p "$OUTDIR"

# Generate output filename
BASENAME=$(basename "$SCRIPT" .py)
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
OUTPUT_FILE="${OUTDIR}/${BASENAME}_${ITERATIONS}iters_${TIMESTAMP}.log"

# Execute and redirect stdout and stderr
python3 "$SCRIPT" "$ITERATIONS" > "$OUTPUT_FILE" 2>&1

echo "Execution complete. Output saved to $OUTPUT_FILE"