#!/bin/bash
#SBATCH --job-name=ns-greedy-recon
#SBATCH --partition=gpu
#SBATCH --account=pi-jevans
#SBATCH --qos=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
#SBATCH --time=00:45:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/greedy_recon_%j.log
set -e
source /home/aoberoi1/novelty_stories/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:/project/jevans/avi/envs/ns_deps"
cd /home/aoberoi1/novelty_stories
$PY /home/aoberoi1/novelty_stories/recon_greedy.py
echo "---running eval---"
$PY eval.py --config config.yaml --run_dir $NS_ROOT/runs/baseline_greedy --task sun
$PY eval.py --config config.yaml --run_dir $NS_ROOT/runs/baseline_greedy --task transfer
$PY eval.py --config config.yaml --run_dir $NS_ROOT/runs/baseline_greedy --task litbench
echo "done."
