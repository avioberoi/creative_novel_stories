#!/bin/bash
#SBATCH --job-name=ns-baseline
#SBATCH --partition=jevans-gpu
#SBATCH --account=pi-jevans
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=03:00:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/baseline_%A_%a.log
#SBATCH --array=0-2
set -e
MODES=(random greedy divbeam)
MODE=${MODES[$SLURM_ARRAY_TASK_ID]}
source /home/aoberoi1/novelty_stories/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:/project/jevans/avi/envs/ns_deps"

# wait for vLLM
while [ ! -s $NS_ROOT/vllm_endpoint.txt ]; do sleep 20; done
EP=$(cat $NS_ROOT/vllm_endpoint.txt)
export VLLM_URL="http://${EP}/v1"
until curl -sf "$VLLM_URL/models" >/dev/null 2>&1; do sleep 20; done

cd /home/aoberoi1/novelty_stories
N=${N:-200}
$PY baselines.py --mode $MODE --n $N --name "baseline_${MODE}"
