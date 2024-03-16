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

# Run the following command in python and error if the hardware is not supported
if python -c 'import torch; assert torch.cuda.get_device_capability()[0] >= 8, "Hardware not supported for Flash Attention"'; then
	echo "Hardware supported for Flash Attention"
else
	echo "Hardware not supported for Flash Attention"
	exit 1
fi

# install flash-attn
pip install ninja packaging
MAX_JOBS=4 pip install flash-attn --no-build-isolation
