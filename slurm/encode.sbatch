#!/bin/bash
#SBATCH --job-name=ns-encode
#SBATCH --partition=gpu
#SBATCH --account=<account>
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=<PROJECT_ROOT>/novelty_stories/logs/encode_%A_%a.log
#SBATCH --array=0-3
set -e
ENCODERS=(qwen3_emb bge e5_mistral emb_gemma)
ENC=${ENCODERS[$SLURM_ARRAY_TASK_ID]}
source <REPO_ROOT>/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:<PROJECT_ROOT>/envs"

cd <REPO_ROOT>
$PY encode_corpus.py --encoder $ENC
