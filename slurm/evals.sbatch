#!/bin/bash
#SBATCH --job-name=ns-eval
#SBATCH --partition=jevans-gpu
#SBATCH --account=pi-jevans
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=04:00:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/eval_%A_%a.log
set -e
source /home/aoberoi1/novelty_stories/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:/project/jevans/avi/envs/ns_deps"

cd /home/aoberoi1/novelty_stories

# pick up the judge endpoint if a Gemma vLLM server is running
if [ -s "$NS_ROOT/vllm_judge_endpoint.txt" ]; then
  export JUDGE_URL="http://$(cat $NS_ROOT/vllm_judge_endpoint.txt)/v1"
  echo "Gemma judge at $JUDGE_URL"
fi

for d in $NS_ROOT/runs/*/; do
  [ -f "$d/archive.npz" ] || continue
  echo "=== $d ==="
  $PY eval.py --run_dir "$d" --task transfer
  $PY eval.py --run_dir "$d" --task sun
  $PY eval.py --run_dir "$d" --task litbench
  if [ -n "${JUDGE_URL:-}" ]; then
    $PY eval.py --run_dir "$d" --task gemma
  fi
done

RUNS=$(ls -d $NS_ROOT/runs/*/ 2>/dev/null | tr '\n' ' ')
if [ -n "$RUNS" ]; then
  $PY viz.py --runs $RUNS --out $NS_ROOT/figs
fi
