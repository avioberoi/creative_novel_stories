#!/bin/bash
#SBATCH --job-name=ns-greedy-recon
#SBATCH --partition=gpu
#SBATCH --account=<account>
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:45:00
#SBATCH --output=<PROJECT_ROOT>/novelty_stories/logs/greedy_recon_%j.log
set -e
source <REPO_ROOT>/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:<PROJECT_ROOT>/envs"
cd <REPO_ROOT>
$PY <REPO_ROOT>/recon_greedy.py
echo "---running eval---"
$PY eval.py --config config.yaml --run_dir $NS_ROOT/runs/baseline_greedy --task sun
$PY eval.py --config config.yaml --run_dir $NS_ROOT/runs/baseline_greedy --task transfer
$PY eval.py --config config.yaml --run_dir $NS_ROOT/runs/baseline_greedy --task litbench
echo "done."
