#!/bin/bash
#SBATCH --job-name=modelling-metadata-html-create-toy-dataset # job name
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1           # crucial - only 1 task per dist per node!
#SBATCH --cpus-per-task=8            # number of cores per tasks
#SBATCH --hint=nomultithread          # we get physical cores not logical
#SBATCH --time 01:00:00               # maximum execution time (HH:MM:SS)
#SBATCH --output=/gpfsdswork/projects/rech/six/uue59kq/logs/%x-%j.out          # output file name
#SBATCH --error=/gpfsdswork/projects/rech/six/uue59kq/logs/%x-%j.err           # error file name
#SBATCH --account=six@cpu # account

set -x -e

source $HOME/start-user

cd $WORK/repos/sync/mini-html-parser

python parse_scripts/parse_natural_questions_Toy_v2.py \
    --data_dir "${SCRATCH}/upload/v1.0/" \