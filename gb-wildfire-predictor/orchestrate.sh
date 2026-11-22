#!/bin/bash 

# 1. Configuration 
START_DATE = "2023-06-01" 
END_DATE = "2023-06-10"
mkdir -p logs 

current_date = "$START_DATE"

while [["current_date " < $END_DATE || "current_date " == $END_DATE]]; do 
    echo "Submitting: $current_date" 


    sbatch --export=ALL,TARGET_DATE="$current_date" submit_job.sh
    current_date=$(date -I -d "$current_date + 1 day")
done