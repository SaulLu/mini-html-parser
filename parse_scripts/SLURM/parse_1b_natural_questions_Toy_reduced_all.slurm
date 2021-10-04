#!/bin/bash
#SBATCH --job-name=parse_1b_natural_questions_Toy_reduced_all # job name
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1           # crucial - only 1 task per dist per node!
#SBATCH --cpus-per-task=40            # number of cores per tasks
#SBATCH --hint=nomultithread          # we get physical cores not logical
#SBATCH --time 01:00:00               # maximum execution time (HH:MM:SS)
#SBATCH --output=/gpfsdswork/projects/rech/six/uue59kq/logs/%x-%j.out          # output file name
#SBATCH --error=/gpfsdswork/projects/rech/six/uue59kq/logs/%x-%j.err           # error file name
#SBATCH --account=six@cpu # account

set -x -e

source $HOME/start-user

cd $WORK/repos/sync/mini-html-parser

python parse_scripts/parse_natural_questions_Toy_keep_everything.py \
    --data-dir-orig "${SCRATCH}/new_dataset/Natural_Questions_reduced/v1.0/" \
    --data-dir-target "${SCRATCH}/new_dataset/Natural_Questions_HTML_reduced_all/" \
    --num-cores 40