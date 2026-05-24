#!/bin/bash
#SBATCH --job-name=ns-greedy-recon
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:45:00
#SBATCH --output=logs/greedy_recon_%j.log
set -e
source "$(dirname "$0")/setenv.sh"
cd "$(dirname "$0")/.."
$PY scripts/oneoff/recon_greedy.py
echo "---running eval---"
$PY eval.py --config config.yaml --run_dir "$NS_ROOT/runs/baseline_greedy" --task sun
$PY eval.py --config config.yaml --run_dir "$NS_ROOT/runs/baseline_greedy" --task transfer
$PY eval.py --config config.yaml --run_dir "$NS_ROOT/runs/baseline_greedy" --task litbench
echo "done."
