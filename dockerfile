# Stage 1: base image with ComfyUI and dependencies
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04 as base

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_PREFER_BINARY=1
ENV PYTHONUNBUFFERED=1 
ENV CMAKE_BUILD_PARALLEL_LEVEL=8

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    wget \
    curl \
    git \
    libssl-dev \
    zlib1g-dev \
    libncurses5-dev \
    libncursesw5-dev \
    libreadline-dev \
    libsqlite3-dev \
    libgdbm-dev \
    libdb5.3-dev \
    libbz2-dev \
    libexpat1-dev \
    liblzma-dev \
    tk-dev \
    libffi-dev \
    libgl1 \
    libglib2.0-0 \
    libopencv-dev \
    google-perftools \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Install Python from source
ENV PYTHON_VERSION=3.12.2
RUN curl -O https://www.python.org/ftp/python/${PYTHON_VERSION}/Python-${PYTHON_VERSION}.tgz && \
    tar -xzf Python-${PYTHON_VERSION}.tgz && \
    cd Python-${PYTHON_VERSION} && \
    ./configure --enable-optimizations && \
    make -j$(nproc) && \
    make altinstall && \
    cd .. && \
    rm -rf Python-${PYTHON_VERSION} Python-${PYTHON_VERSION}.tgz
RUN ln -s /usr/local/bin/python3.12 /usr/bin/python && \
    ln -s /usr/local/bin/pip3.12 /usr/bin/pip

# Clone and install ComfyUI
RUN git clone https://github.com/comfyanonymous/ComfyUI --depth 1 /comfyui
WORKDIR /comfyui

RUN pip install -r requirements.txt
RUN pip install torch torchvision torchaudio -I --index-url https://download.pytorch.org/whl/cu124
RUN pip install runpod onnxruntime-gpu

# Optional custom nodes
RUN git clone https://github.com/kijai/ComfyUI-KJNodes custom_nodes/ComfyUI-KJNodes
RUN pip install -r custom_nodes/ComfyUI-KJNodes/requirements.txt

# Add start script
WORKDIR /
COPY start.sh /start.sh
RUN chmod +x /start.sh

ENV LD_PRELOAD=/usr/lib/x86_64-linux-gnu/libtcmalloc_minimal.so.4

CMD ["/start.sh"]

# Stage 2: download models
FROM base as downloader

WORKDIR /comfyui
RUN mkdir -p models/unet/ models/text_encoders/ models/clip/ models/vae/

RUN wget -q --header="Authorization: Bearer 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" -O models/unet/flux1-dev.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/flux1-dev.safetensors && \
    wget -q -O models/clip/clip_l.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors && \
    wget -q -O models/clip/t5xxl_fp8_e4m3fn.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/t5xxl_fp8_e4m3fn.safetensors && \
    wget -q --header="Authorization: Bearer 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" -O models/vae/ae.safetensors https://huggingface.co/black-forest-labs/FLUX.1-dev/resolve/main/ae.safetensors

# Stage 3: final build with all models
FROM base as final

COPY --from=downloader /comfyui/models /comfyui/models
COPY --from=base /start.sh /start.sh

CMD ["/start.sh"]
