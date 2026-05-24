#!/bin/bash
#SBATCH --job-name=ns-vllm
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=128G
#SBATCH --time=10:00:00
#SBATCH --output=logs/vllm_%j.log
#
# vLLM server for generator (Qwen3-32B). Writes endpoint to
# $NS_ROOT/vllm_endpoint.txt for other jobs to read.
set -e
source "$(dirname "$0")/setenv.sh"
PORT=30000
echo "$(hostname):$PORT" > "$NS_ROOT/vllm_endpoint.txt"
echo "vLLM endpoint: $(cat "$NS_ROOT/vllm_endpoint.txt")"

# Set QWEN3_32B_MODEL to a local snapshot path if you've pre-downloaded the weights.
$PY -m vllm.entrypoints.openai.api_server \
  --model "${QWEN3_32B_MODEL:-Qwen/Qwen3-32B}" \
  --port $PORT \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 16 \
  --max-model-len 8192 \
  --enable-prefix-caching \
  --disable-log-requests
