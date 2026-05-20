#!/bin/bash
# Source me from each sbatch script. Redirects all caches to <PROJECT_ROOT>.
# We KEEP ~/.local enabled here: vllm_env has a broken sentence_transformers/numba
# pinning that ~/.local fixes by override. The only job that needs to avoid ~/.local
# is vllm.sbatch (for triton) — it prepends vllm_env site-packages explicitly.
export NS_ROOT=<PROJECT_ROOT>/novelty_stories
export NS_CACHE=<PROJECT_ROOT>/cache
mkdir -p $NS_ROOT/logs $NS_ROOT/embs $NS_ROOT/runs $NS_ROOT/figs $NS_ROOT/expanded
mkdir -p $NS_CACHE/{huggingface,torch,vllm,triton,pip,tmp}
export HF_HOME=$NS_CACHE/huggingface
export TORCH_HOME=$NS_CACHE/torch
export VLLM_CACHE_ROOT=$NS_CACHE/vllm
export TRITON_CACHE_DIR=$NS_CACHE/triton
export PIP_CACHE_DIR=$NS_CACHE/pip
export TMPDIR=$NS_CACHE/tmp
export PY=<VLLM_ENV>/bin/python
