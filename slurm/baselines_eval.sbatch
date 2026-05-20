#!/bin/bash
#SBATCH --job-name=ns-baseval
#SBATCH --partition=gpu
#SBATCH --account=pi-jevans
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/baselines_eval_%j.log
set -e
source /home/aoberoi1/novelty_stories/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:/project/jevans/avi/envs/ns_deps"

cd /home/aoberoi1/novelty_stories
for d in $NS_ROOT/runs/baseline_*; do
  [ -f "$d/archive.npz" ] || { echo "skip $(basename $d) -- no archive yet"; continue; }
  echo "=== $(basename $d) ==="
  $PY eval.py --config config.yaml --run_dir "$d" --task sun
  $PY eval.py --config config.yaml --run_dir "$d" --task transfer
  $PY eval.py --config config.yaml --run_dir "$d" --task litbench
done
echo "done."
