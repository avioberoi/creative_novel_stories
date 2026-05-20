#!/bin/bash
#SBATCH --job-name=ns-vllm-judge
#SBATCH --partition=gpu
#SBATCH --account=<account>
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --output=<PROJECT_ROOT>/novelty_stories/logs/vllm_judge_%j.log
set -e
source <REPO_ROOT>/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH=<VLLM_ENV>/lib/python3.11/site-packages:${PYTHONPATH:-}
PORT=30001
echo "$(hostname):$PORT" > $NS_ROOT/vllm_judge_endpoint.txt
echo "Gemma judge endpoint: $(cat $NS_ROOT/vllm_judge_endpoint.txt)"

$PY -m vllm.entrypoints.openai.api_server \
  --model <MODEL_ROOT>/gemma-2-27b-it \
  --port $PORT \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 16 \
  --max-model-len 4096 \
  --enable-prefix-caching \
  --disable-log-requests
