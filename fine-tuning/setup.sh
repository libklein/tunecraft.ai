#!/bin/bash

# Create a virtual environment
# python3 -m venv .venv
# source .venv/bin/activate

# Install Pytorch & other libraries
pip install "torch" tensorboard

# Install Hugging Face libraries
pip install --upgrade \
	"transformers" \
	"datasets" \
	"evaluate" \
	"accelerate" \
	"bitsandbytes" \
	"numpy" \
	"typer" \
	"flask"

# install peft & trl from github
pip install git+https://github.com/huggingface/trl --upgrade
pip install git+https://github.com/huggingface/peft --upgrade

# Install unsloth for pytorch 2.2.0 and Cuda 12.1
pip install "unsloth[cu121-ampere-torch220] @ git+https://github.com/unslothai/unsloth.git"

if python -c 'import torch; assert torch.cuda.is_available()'; then
	echo "Installing llama-cpp-python for GPU"
	CMAKE_ARGS="-DLLAMA_CUDA=on" pip install "llama-cpp-python"
else
	# Install llama-cpp-python for CPU
	echo "Installing llama-cpp-python for CPU"
	pip install "llama-cpp-python"
fi

# Run the following command in python and error if the hardware is not supported
if python -c 'import torch; assert torch.cuda.get_device_capability()[0] >= 8'; then
	echo "Hardware supported for Flash Attention"
else
	echo "Hardware not supported for Flash Attention"
	exit 1
fi

# install flash-attn
pip install ninja packaging
MAX_JOBS=4 pip install flash-attn --no-build-isolation

# Setup huggingface git credential storing
git config --global credential.helper store
