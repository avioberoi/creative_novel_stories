#!/bin/bash
#SBATCH --job-name=ns-eval-partial
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=01:00:00
#SBATCH --output=logs/eval_partial_%j.log
set -e
source "$(dirname "$0")/setenv.sh"

cd "$(dirname "$0")/.."
for d in "$NS_ROOT"/runs/*_s42; do
  [ -f "$d/archive.npz" ] || continue
  bn=$(basename "$d")
  echo "=== $bn ==="
  # transfer (held-out emb_gemma Spearman) — fast
  $PY eval.py --config config.yaml --run_dir "$d" --task transfer
  # litbench BT scoring — downloads 3B model first call (~5 min) then ~30s/archive
  $PY eval.py --config config.yaml --run_dir "$d" --task litbench
done
echo "done."
