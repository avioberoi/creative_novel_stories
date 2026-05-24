#!/bin/bash
#SBATCH --job-name=ns-diff-eval
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=logs/diff_eval_%j.log
set -e
source "$(dirname "$0")/setenv.sh"

cd "$(dirname "$0")/.."
D="$NS_ROOT/runs/diffusion_s42"
$PY eval.py --config config.yaml --run_dir "$D" --task sun
$PY eval.py --config config.yaml --run_dir "$D" --task transfer
$PY eval.py --config config.yaml --run_dir "$D" --task litbench
echo "done."
