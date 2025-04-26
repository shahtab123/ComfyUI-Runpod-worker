# Stage 1: base image with ComfyUI and dependencies
FROM nvidia/cuda:12.4.1-cudnn-runtime-ubuntu22.04 as base

ENV DEBIAN_FRONTEND=noninteractive
ENV PIP_PREFER_BINARY=1
ENV PYTHONUNBUFFERED=1 
ENV CMAKE_BUILD_PARALLEL_LEVEL=8

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
    && apt-get clean && rm -rf /var/lib/apt/lists/*

    
# Download and install Python from source
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

# Install ComfyUI from source and download dependencies
RUN git clone https://github.com/comfyanonymous/ComfyUI --depth 1 /comfyui
WORKDIR /comfyui
RUN pip install -r requirements.txt
RUN pip install torch torchvision torchaudio -I --index-url https://download.pytorch.org/whl/cu124

RUN pip install runpod onnxruntime-gpu

# Install custom nodes here, KJNodes given as an example
RUN git clone https://github.com/kijai/ComfyUI-KJNodes custom_nodes/ComfyUI-KJNodes 
RUN pip install -r custom_nodes/ComfyUI-KJNodes/requirements.txt 

WORKDIR /

ADD src/start.sh src/rp_handler.py src/rp_io.py src/comfy_handler.py ./
RUN chmod +x /start.sh

CMD ["/start.sh"]

# Stage 2: download models
FROM base as downloader

WORKDIR /comfyui

RUN mkdir -p models/unet/ models/text_encoders/ models/clip/ models/vae/

RUN wget -q -O models/unet/flux1-dev-fp8.safetensors https://huggingface.co/Kijai/flux-fp8/resolve/main/flux1-dev-fp8.safetensors && \
    wget -q -O models/text_encoders/google_t5-v1_1-xxl_encoderonly_fp16.safetensors https://huggingface.co/mcmonkey/google_t5-v1_1-xxl_encoderonly/resolve/main/model.safetensors && \
    wget -q -O models/clip/clip_l.safetensors https://huggingface.co/comfyanonymous/flux_text_encoders/resolve/main/clip_l.safetensors && \
    wget -q -O models/vae/flux1_ae.safetensors https://huggingface.co/ostris/OpenFLUX.1/resolve/main/vae/diffusion_pytorch_model.safetensors

# Stage 3: final image
FROM base as final

COPY --from=downloader /comfyui/models /comfyui/models

CMD ["/start.sh"]
