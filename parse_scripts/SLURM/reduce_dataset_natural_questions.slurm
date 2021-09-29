#!/bin/bash
#SBATCH --job-name=reduce_natural_questions_dataset                                # (change me!) job name
#SBATCH --nodes=1
#SBATCH --ntasks-per-node=1                                             # crucial - only 1 task per dist per node!
#SBATCH --cpus-per-task=8                                               # (change me! between 0 and 48) number of cores per tasks
#SBATCH --hint=nomultithread                                            # we get physical cores not logical
#SBATCH --gres=gpu:0                                                    # (change me! between 0 and 1) number of gpus
#SBATCH --time 05:10:00                                                 # (change me! between 0 and 20h) maximum execution time (HH:MM:SS)
#SBATCH --output=/gpfsdswork/projects/rech/six/uue59kq/logs/%x-%j.out   # output file name
#SBATCH --error=/gpfsdswork/projects/rech/six/uue59kq/logs/%x-%j.err    # error file name
#SBATCH --account=six@gpu                                               # account
#SBATCH -p compil                                                       # partition with internet

set -x -e

source $HOME/start-user

cd $WORK/repos/sync/mini-html-parser

# echo "begin dev"
# python parse_scripts/dataset_reducer.py \
#     --data-path "${SCRATCH}/upload/v1.0/dev" \
#     --new-dataset-path "${SCRATCH}/new_dataset/Natural_Questions_reduced/v1.0/dev" \
#     --total-number-examples 6000 \

echo "begin train"
python parse_scripts/dataset_reducer.py \
    --data-path "${SCRATCH}/upload/v1.0/train" \
    --new-dataset-path "${SCRATCH}/new_dataset/Natural_Questions_reduced/v1.0/train" \
    --total-number-examples 50000 \
