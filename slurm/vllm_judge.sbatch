#!/bin/bash
#SBATCH --job-name=ns-vllm-judge
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --output=logs/vllm_judge_%j.log
set -e
source "$(dirname "$0")/setenv.sh"
PORT=30001
echo "$(hostname):$PORT" > "$NS_ROOT/vllm_judge_endpoint.txt"
echo "Gemma judge endpoint: $(cat "$NS_ROOT/vllm_judge_endpoint.txt")"

$PY -m vllm.entrypoints.openai.api_server \
  --model "${GEMMA2_27B_MODEL:-google/gemma-2-27b-it}" \
  --port $PORT \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 16 \
  --max-model-len 4096 \
  --enable-prefix-caching \
  --disable-log-requests
