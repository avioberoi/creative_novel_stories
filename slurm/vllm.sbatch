#!/bin/bash
#SBATCH --job-name=ns-vllm
#SBATCH --partition=gpu
#SBATCH --account=<account>
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=10:00:00
#SBATCH --output=<PROJECT_ROOT>/novelty_stories/logs/vllm_%j.log
set -e
source <REPO_ROOT>/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
# IMPORTANT: vLLM needs vllm_env's pinned triton; ~/.local has a broken triton that
# wins by default. Prepending vllm_env site-packages to PYTHONPATH forces it first.
export PYTHONPATH=<VLLM_ENV>/lib/python3.11/site-packages:${PYTHONPATH:-}
PORT=30000
echo "$(hostname):$PORT" > $NS_ROOT/vllm_endpoint.txt
echo "vLLM endpoint: $(cat $NS_ROOT/vllm_endpoint.txt)"

$PY -m vllm.entrypoints.openai.api_server \
  --model <MODEL_ROOT>/Qwen3-32B \
  --port $PORT \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 16 \
  --max-model-len 8192 \
  --enable-prefix-caching \
  --disable-log-requests
