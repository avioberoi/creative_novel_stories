#!/bin/bash
#SBATCH --job-name=ns-encode
#SBATCH --partition=jevans-gpu
#SBATCH --account=pi-jevans
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=02:00:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/encode_%A_%a.log
#SBATCH --array=0-3
set -e
ENCODERS=(qwen3_emb bge e5_mistral nv_embed)
ENC=${ENCODERS[$SLURM_ARRAY_TASK_ID]}
source /home/aoberoi1/novelty_stories/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:/project/jevans/avi/envs/ns_deps"

cd /home/aoberoi1/novelty_stories
$PY encode_corpus.py --encoder $ENC
