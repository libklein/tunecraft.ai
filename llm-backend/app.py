from json import dumps, loads
from llama_cpp import Llama
from pathlib import Path
from typing import Optional


def log_into_huggingface(token: str):
    from huggingface_hub import login

    login(token=token, add_to_git_credential=False)


def evaluate_prompt(model, messages: list[dict]):
    model_response = model.create_chat_completion(messages, max_tokens=2048)

    serialized_response = model_response["choices"][0]["message"]["content"]

    return serialized_response


def generate_chatml_prompt(
    prompt: str, system_prompt: Optional[str] = None
) -> list[dict]:
    # Add the system prompt to the prompt
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]


def load_model(
    model_dir_or_id: str | Path, use_gpu: bool = False, max_seq_length: int = 2048
):
    if Path(model_dir_or_id).exists():
        return Llama(
            model_path=str(model_dir_or_id),
            n_gpu_layers=-1 if use_gpu else 0,
            n_ctx=max_seq_length,
            chat_format="chatml",
            verbose=False,
        )
    else:
        return Llama.from_pretrained(
            repo_id=str(model_dir_or_id),
            n_gpu_layers=-1 if use_gpu else 0,
            n_ctx=max_seq_length,
            chat_format="chatml",
            filename="*.gguf",
            verbose=False,
        )


huggingface_token = None

if huggingface_token:
    try:
        log_into_huggingface(huggingface_token)
    except Exception as e:
        print(f"An error occurred logging into huggingface: {e}")
        exit(1)

system_prompt = None
use_gpu = False
max_seq_length = 2048
model_dir_or_id = Path(
    "./libklein/unsloth-mistral-7b-instruct-v0.2-bnb-4bit-no-system-prompt-q4_k_m-unsloth.Q4_K_M.gguf"
)
model = load_model(model_dir_or_id, use_gpu=use_gpu, max_seq_length=max_seq_length)


def handler(body, context):
    if (prompt := body.get("prompt")) is None:
        # Invalid request
        return {
            "statusCode": 400,
            "body": dumps({"error": "Invalid request"}),
            "headers": {"Content-Type": "application/json"},
        }

    prompt = generate_chatml_prompt(prompt, system_prompt)
    model_response = evaluate_prompt(model, prompt)

    return {
        "statusCode": 200,
        "body": dumps({"response": model_response}),
        "headers": {"Content-Type": "application/json"},
    }
