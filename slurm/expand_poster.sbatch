#!/bin/bash
#SBATCH --job-name=ns-expand-poster
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=4
#SBATCH --mem=32G
#SBATCH --time=02:00:00
#SBATCH --output=logs/expand_poster_%j.log
set -e
source "$(dirname "$0")/setenv.sh"

# expand.py needs vLLM Qwen32B; wait for its endpoint
while [ ! -s "$NS_ROOT/vllm_endpoint.txt" ]; do sleep 30; done
EP=$(cat "$NS_ROOT/vllm_endpoint.txt")
export VLLM_URL="http://${EP}/v1"
until curl -sf "$VLLM_URL/models" >/dev/null 2>&1; do sleep 30; done

cd "$(dirname "$0")/.."

# expand top-N snippets into full stories
RUNS=$(ls -d "$NS_ROOT"/runs/*_s42 2>/dev/null | grep -v smoke | tr '\n' ' ')
echo "expanding from: $RUNS"
$PY expand.py --config config.yaml --runs $RUNS --out "$NS_ROOT/expanded"

# generate QR — replace with your final repo URL
$PY scripts/oneoff/make_qr.py "https://github.com/<your-org>/<your-repo>" "$NS_ROOT/qr.png"

# render final poster with all data and QR
$PY scripts/oneoff/poster.py --config config.yaml --runs $RUNS \
  --qr "$NS_ROOT/qr.png" --out "$NS_ROOT/poster.pdf"
echo "wrote $NS_ROOT/poster.pdf"
