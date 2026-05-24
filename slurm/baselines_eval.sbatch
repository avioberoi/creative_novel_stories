#!/bin/bash
#SBATCH --job-name=ns-baseval
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=logs/baselines_eval_%j.log
set -e
source "$(dirname "$0")/setenv.sh"

cd "$(dirname "$0")/.."
for d in "$NS_ROOT"/runs/baseline_*; do
  [ -f "$d/archive.npz" ] || { echo "skip $(basename "$d") -- no archive yet"; continue; }
  echo "=== $(basename "$d") ==="
  $PY eval.py --config config.yaml --run_dir "$d" --task sun
  $PY eval.py --config config.yaml --run_dir "$d" --task transfer
  $PY eval.py --config config.yaml --run_dir "$d" --task litbench
done
echo "done."
