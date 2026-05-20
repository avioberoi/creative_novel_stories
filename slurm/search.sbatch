#!/bin/bash
#SBATCH --job-name=ns-search
#SBATCH --partition=jevans-gpu
#SBATCH --account=pi-jevans
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=08:00:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/search_%A_%a.log
#SBATCH --array=0-4
set -e
METRICS=(euclidean cosine mahalanobis lof diffusion)
METRIC=${METRICS[$SLURM_ARRAY_TASK_ID]}
source /home/aoberoi1/novelty_stories/slurm/setenv.sh

# wait for the vLLM endpoint file and for the server to actually accept requests
while [ ! -s $NS_ROOT/vllm_endpoint.txt ]; do
  echo "waiting for vllm_endpoint.txt..."; sleep 20
done
ENDPOINT=$(cat $NS_ROOT/vllm_endpoint.txt)
export VLLM_URL="http://${ENDPOINT}/v1"
echo "Using vLLM at $VLLM_URL"
until curl -sf "$VLLM_URL/models" >/dev/null 2>&1; do
  echo "waiting for vllm /models to respond at $VLLM_URL ..."; sleep 20
done
echo "vLLM is ready."

set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:/project/jevans/avi/envs/ns_deps"

cd /home/aoberoi1/novelty_stories
$PY novelty.py --metric $METRIC --seed 42 --name "${METRIC}_s42"
