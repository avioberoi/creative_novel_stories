#!/bin/bash
#SBATCH --job-name=ns-expand-poster
#SBATCH --partition=jevans
#SBATCH --account=pi-jevans
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=/project/jevans/avi/novelty_stories/logs/expand_poster_%j.log
set -e
source /home/aoberoi1/novelty_stories/slurm/setenv.sh
set +u; source ~/.bashrc; set -u
export PYTHONPATH="${PYTHONPATH:-}:/project/jevans/avi/envs/ns_deps"

# expand.py needs vLLM Qwen32B; wait for its endpoint
while [ ! -s $NS_ROOT/vllm_endpoint.txt ]; do sleep 30; done
EP=$(cat $NS_ROOT/vllm_endpoint.txt)
export VLLM_URL="http://${EP}/v1"
until curl -sf "$VLLM_URL/models" >/dev/null 2>&1; do sleep 30; done

cd /home/aoberoi1/novelty_stories

# expand top-N snippets into full stories
RUNS=$(ls -d $NS_ROOT/runs/*_s42 2>/dev/null | grep -v smoke | tr '\n' ' ')
echo "expanding from: $RUNS"
$PY expand.py --config config.yaml --runs $RUNS --out $NS_ROOT/expanded

# generate QR (placeholder URL — replace with final once known)
$PY make_qr.py "https://github.com/avioberoi/novelty_stories" $NS_ROOT/qr.png

# render final poster with all data and QR
$PY poster.py --config config.yaml --runs $RUNS \
  --qr $NS_ROOT/qr.png --out $NS_ROOT/poster.pdf
echo "wrote $NS_ROOT/poster.pdf"
