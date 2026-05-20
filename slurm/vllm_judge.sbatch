#!/bin/bash
#SBATCH --job-name=ns-vllm-judge
#SBATCH --partition=jevans-gpu
#SBATCH --account=pi-jevans
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=96G
#SBATCH --time=06:00:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/vllm_judge_%j.log
set -e
source /home/aoberoi1/novelty_stories/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH=/project/jevans/maxzhuyt/vllm_env/lib/python3.11/site-packages:${PYTHONPATH:-}
PORT=30001
echo "$(hostname):$PORT" > $NS_ROOT/vllm_judge_endpoint.txt
echo "Gemma judge endpoint: $(cat $NS_ROOT/vllm_judge_endpoint.txt)"

$PY -m vllm.entrypoints.openai.api_server \
  --model /project/jevans/maxzhuyt/models/gemma-2-27b-it \
  --port $PORT \
  --dtype bfloat16 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 16 \
  --max-model-len 4096 \
  --enable-prefix-caching \
  --disable-log-requests
