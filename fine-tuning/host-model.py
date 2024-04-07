from flask import Flask, request
import os
from json import dumps, loads
from llama_cpp import Llama
from pathlib import Path
from typing import Optional


def log_into_huggingface(token: str):
    from huggingface_hub import login

    login(token=token, add_to_git_credential=True)


def evaluate_prompt(model, messages: list[dict]):
    model_response = model.create_chat_completion(messages, max_tokens=2048)

    serialized_response = dumps(model_response["choices"][0]["message"]["content"])

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


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile("config.py", silent=True)
    else:
        # load the test config if passed in
        app.config.from_mapping(test_config)

    # ensure the instance folder exists
    try:
        os.makedirs(app.instance_path)
    except OSError:
        pass

    huggingface_token = app.config.get("HUGGINGFACE_TOKEN")

    if huggingface_token:
        try:
            log_into_huggingface(huggingface_token)
        except Exception as e:
            print(f"An error occurred logging into huggingface: {e}")
            return

    system_prompt = app.config.get("SYSTEM_PROMPT")
    use_gpu = app.config.get("USE_GPU", False)
    max_seq_length = app.config.get("MAX_SEQ_LENGTH", 2048)

    model_dir_or_id = app.config.get("MODEL_DIR_OR_ID")
    model = load_model(model_dir_or_id, use_gpu=use_gpu, max_seq_length=max_seq_length)

    @app.route("/evaluate", methods=["POST"])
    def evaluate():
        prompt = request.json.get("prompt")

        if not prompt:
            return {"error": "Prompt not provided"}, 400

        prompt = generate_chatml_prompt(prompt, system_prompt)
        # Return the response
        model_response = evaluate_prompt(model, prompt)

        # Model returns a json formatted string. Indicate that it's in fact json
        response = app.response_class(
            response=model_response, status=200, mimetype="application/json"
        )
        return response

    return app
