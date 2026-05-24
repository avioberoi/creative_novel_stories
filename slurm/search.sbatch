#!/bin/bash
#SBATCH --job-name=ns-search
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=logs/search_%A_%a.log
#SBATCH --array=0-4
#
# Set NS_ROOT (project working dir) and PY (python interpreter) in your env or
# via --export before sbatch'ing. See slurm/setenv.sh.
set -e
METRICS=(euclidean cosine mahalanobis lof diffusion)
METRIC=${METRICS[$SLURM_ARRAY_TASK_ID]}
source "$(dirname "$0")/setenv.sh"

# Wait for the vLLM endpoint file and for the server to actually accept requests.
while [ ! -s "$NS_ROOT/vllm_endpoint.txt" ]; do
  echo "waiting for vllm_endpoint.txt..."; sleep 20
done
ENDPOINT=$(cat "$NS_ROOT/vllm_endpoint.txt")
export VLLM_URL="http://${ENDPOINT}/v1"
echo "Using vLLM at $VLLM_URL"
until curl -sf "$VLLM_URL/models" >/dev/null 2>&1; do
  echo "waiting for vllm /models to respond at $VLLM_URL ..."; sleep 20
done
echo "vLLM is ready."

cd "$(dirname "$0")/.."
$PY novelty.py --metric "$METRIC" --seed 42 --name "${METRIC}_s42"
