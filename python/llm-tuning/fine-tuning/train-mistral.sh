#!/bin/bash
#
python finetune.py finetune mistralai/Mistral-7B-Instruct-v0.2 conversation.json "mistral-7b-v0.2-500-examples" --huggingface-token=$(cat .hugging-face-token) --max-seq-length=4096 --epochs=10
