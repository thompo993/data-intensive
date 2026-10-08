#!/bin/bash
# ======================
# slurm_mpi_hello.sh
# ======================
#SBATCH --job-name=mpi_hello
#SBATCH --partition=teach_cpu
#SBATCH --account=phys040684
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1
#SBATCH --cpus-per-task=1
#SBATCH --time=0:0:5
#SBATCH --mem=100M


# initialise mamba
source ~/ initMamba.sh
mamba activate mpi_test
cd $SLURM_SUBMIT_DIR


mpirun -np 4 python mpi_hello.py