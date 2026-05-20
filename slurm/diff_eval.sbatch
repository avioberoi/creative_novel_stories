#!/bin/bash
#SBATCH --job-name=ns-diff-eval
#SBATCH --partition=gpu
#SBATCH --account=<account>
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:30:00
#SBATCH --output=<PROJECT_ROOT>/novelty_stories/logs/diff_eval_%j.log
set -e
source <REPO_ROOT>/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:<PROJECT_ROOT>/envs"

cd <REPO_ROOT>
D=$NS_ROOT/runs/diffusion_s42
$PY eval.py --config config.yaml --run_dir "$D" --task sun
$PY eval.py --config config.yaml --run_dir "$D" --task transfer
$PY eval.py --config config.yaml --run_dir "$D" --task litbench
echo "done."
