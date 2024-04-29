#!/bin/bash
python finetune.py finetune unsloth/mistral-7b-instruct-v0.2-bnb-4bit conversation.json "unsloth-mistral-7b-instruct-v0.2-bnb-4bit-no-system-prompt" --huggingface-token=$(cat .hugging-face-token) --max-seq-length=2048 --epochs=10
