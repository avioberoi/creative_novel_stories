#!/bin/bash
#SBATCH --job-name=ns-encode
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=logs/encode_%A_%a.log
#SBATCH --array=0-3
set -e
ENCODERS=(qwen3_emb bge e5_mistral emb_gemma)
ENC=${ENCODERS[$SLURM_ARRAY_TASK_ID]}
source "$(dirname "$0")/setenv.sh"

cd "$(dirname "$0")/.."
$PY scripts/oneoff/encode_corpus.py --encoder "$ENC"
