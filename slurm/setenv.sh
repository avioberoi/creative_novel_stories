#!/bin/bash
# Source this from each sbatch script. Sets common env vars + creates cache dirs.
#
# CUSTOMIZE for your environment:
#   NS_ROOT  — project working directory (runs, embs, figs land here)
#   NS_CACHE — HF / torch / vLLM / triton / pip / tmp caches
#   PY       — python interpreter (a venv with the project deps installed)
#
# Override at submit time with `--export=ALL,NS_ROOT=...,NS_CACHE=...,PY=...`
# or set them in your shell profile.

set -u
export PYTHONUNBUFFERED=1
: "${NS_ROOT:=$PWD}"
: "${NS_CACHE:=$NS_ROOT/.cache}"
: "${PY:=python}"
mkdir -p "$NS_ROOT/logs" "$NS_ROOT/embs" "$NS_ROOT/runs" "$NS_ROOT/figs" "$NS_ROOT/expanded"
mkdir -p "$NS_CACHE"/{huggingface,torch,vllm,triton,pip,tmp}
export HF_HOME="$NS_CACHE/huggingface"
export TORCH_HOME="$NS_CACHE/torch"
export VLLM_CACHE_ROOT="$NS_CACHE/vllm"
export TRITON_CACHE_DIR="$NS_CACHE/triton"
export PIP_CACHE_DIR="$NS_CACHE/pip"
export TMPDIR="$NS_CACHE/tmp"
