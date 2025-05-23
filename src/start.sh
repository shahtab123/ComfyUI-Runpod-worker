#!/usr/bin/env bash

# Use libtcmalloc for better memory usage (installed via google-perftools)
export LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4

# Start ComfyUI and API handling
if [ "$SERVE_API_LOCALLY" == "true" ]; then
    echo "[COMFYUI WORKER] Starting ComfyUI"
    python /comfyui/main.py --disable-auto-launch --disable-metadata --listen 0.0.0.0 --port 8188 &
    
    echo "[COMFYUI WORKER] Starting RunPod handler"
    python -u /rp_handler.py --rp_serve_api --rp_api_host=0.0.0.0
else
    echo "[COMFYUI WORKER] Starting ComfyUI (no local API)"
    python /comfyui/main.py --disable-auto-launch --disable-metadata --listen 0.0.0.0 --port 8188 &
    
    echo "[COMFYUI WORKER] Starting RunPod handler"
    python -u /rp_handler.py
fi
