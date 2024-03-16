
import torch
from transformers import AutoTokenizer, pipeline
from trl import setup_chat_format
from peft import AutoPeftModelForCausalLM
from flask import Flask, request
import os


def log_into_huggingface(token: str):
    from huggingface_hub import login
    login(token=token, add_to_git_credential=True)

def evaluate_prompt(pipe, prompt: list[dict]):
    prompt = pipe.tokenizer.apply_chat_template(prompt, tokenize=False, add_generation_prompt=True)
    outputs = pipe(prompt, max_new_tokens=256, do_sample=True, temperature=0.7, top_k=50, top_p=0.95, eos_token_id=pipe.tokenizer.eos_token_id, pad_token_id=pipe.tokenizer.pad_token_id)
    model_response = outputs[0]['generated_text'][len(prompt):].strip()
    print("Response:", model_response)
    return model_response

def build_pipeline(model_dir_or_id: str):
    model = AutoPeftModelForCausalLM.from_pretrained(
        model_dir_or_id,
        # device_map="auto",
        # torch_dtype=torch.bfloat16,
        load_in_4bit=True
    )
    tokenizer = AutoTokenizer.from_pretrained(model_dir_or_id)

    return pipeline("text-generation", model=model, tokenizer=tokenizer)


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__, instance_relative_config=True)
    if test_config is None:
        # load the instance config, if it exists, when not testing
        app.config.from_pyfile('config.py', silent=True)
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

    model_dir_or_id = app.config.get("MODEL_DIR_OR_ID")
    pipe = build_pipeline(model_dir_or_id)

    @app.route('/evaluate', methods=['POST'])
    def hello():
        prompt = request.json.get('prompt')
        # Return the response
        model_response = evaluate_prompt(pipe, prompt)
        # Model returns a json formatted string. Indicate that it's in fact json
        response = app.response_class(
            response=model_response,
            status=200,
            mimetype='application/json'
        )
        return response

    return app
