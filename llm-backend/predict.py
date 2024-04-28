from json import dumps, loads
from llama_cpp import Llama
from typing import Optional
from cog import BasePredictor, Input
import logging
import logging.config
from pythonjsonlogger import jsonlogger

logging.config.fileConfig("logging.conf")
logger = logging.getLogger("json")


def generate_chatml_prompt(
    prompt: str, system_prompt: Optional[str] = None
) -> list[dict]:
    # Add the system prompt to the prompt
    return [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt},
    ]


def read_api_key():
    with open(".api_key", "r") as f:
        return f.read().strip()


class Predictor(BasePredictor):
    system_prompt = None
    use_gpu = False
    max_seq_length = 2048
    model_path = "llm.gguf"

    def evaluate_prompt(self, messages: list[dict]) -> str:
        model_response = self.model.create_chat_completion(messages, max_tokens=2048)

        serialized_response = model_response["choices"][0]["message"]["content"]

        return serialized_response

    def setup(self):
        self.api_key = read_api_key()
        self.model = Llama(
            model_path=str(self.model_path),
            n_gpu_layers=-1 if self.use_gpu else 0,
            n_ctx=self.max_seq_length,
            chat_format="chatml",
            verbose=False,
        )

    def predict(
        self,
        prompt: str = Input(description="The prompt."),
        key: str = Input(description="API Key", default=""),
    ) -> str:
        if key != self.api_key:
            logger.error("Unauthorized request.")
            return None
        logger.info("Received request.", extra={"prompt": prompt})
        parsed_prompt = generate_chatml_prompt(prompt, self.system_prompt)
        logger.info(
            "Generated prompt.",
            extra={"prompt": prompt, "parsed_prompt": parsed_prompt},
        )
        model_response = self.evaluate_prompt(parsed_prompt)

        logger.info(
            "Processed request.",
            extra={
                "prompt": prompt,
                "parsed_prompt": parsed_prompt,
                "response": model_response,
            },
        )

        return model_response
