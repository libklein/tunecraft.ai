import json
import typer
from pathlib import Path
import json
import numpy as np
from collections import defaultdict
from transformers import LlamaTokenizerFast

cli = typer.Typer()

class DataFormatError(Exception):
    pass

def check_data_for_format_errors(items: list):

    for line_num, batch in enumerate(items):
        prefix = f"Error in line #{line_num + 1}: "
        if not isinstance(batch, dict):
            raise DataFormatError(
                f"{prefix}Each line in the provided data should be a dictionary"
            )

        if "messages" not in batch:
            raise DataFormatError(
                f"{prefix}Each line in the provided data should have a 'messages' key"
            )

        if not isinstance(batch["messages"], list):
            raise DataFormatError(
                f"{prefix}Each line in the provided data should have a 'messages' key with a list of messages"
            )

        messages = batch["messages"]
        if not any(message.get("role", None) == "assistant" for message in messages):
            raise DataFormatError(
                f"{prefix}Each message list should have at least one message with role 'assistant'"
            )

        for message_num, message in enumerate(messages):
            prefix = f"Error in line #{line_num + 1}, message #{message_num + 1}: "
            if "role" not in message or "content" not in message:
                raise DataFormatError(
                    f"{prefix}Each message should have a 'role' and 'content' key"
                )

            if any(k not in ("role", "content", "name") for k in message):
                raise DataFormatError(
                    f"{prefix}Each message should only have 'role', 'content', and 'name' keys, any other key is not allowed"
                )

            if message.get("role", None) not in ("system", "user", "assistant"):
                raise DataFormatError(
                    f"{prefix}Each message should have a valid role (system, user, or assistant)"
                )

@cli.command()
def check_dataset(dataset: Path):
    with open(dataset, 'r', encoding='utf-8') as f:
        items = [json.loads(line) for line in f]

    try:
        check_data_for_format_errors(items)
        print("Data format is valid!")
    except DataFormatError as e:
        print("Data format is NOT valid!")
        print(e)


def print_token_statistics(stats) -> None:
    for key in stats:
        print(f"Statistics for {key}:")
        if isinstance(stats[key], dict):
            for stat_key, stat_value in stats[key].items():
                print(f"\t{stat_key}: {stat_value:.3f}")
        else:
            print(f"\t{stats[key]}")
        print("")

def get_tokenized_stats(tokenizer, items: list, print_stats: bool = True):

    counters = defaultdict(list)
    for batch in items:
        messages = batch["messages"]

        # add message count
        counters["message"].append(len(messages))

        # add the number of tokens of this message to the token counter
        text = convert_message_list_to_text(messages)
        tokens = tokenizer(text)['input_ids']
        counters["token"].append(len(tokens))

    stats = {}
    for key, value in counters.items():
        stats[key] = {
            "max": float(np.max(value)),
            "min": float(np.min(value)),
            "median": float(np.median(value)),
            "mean": float(np.mean(value)),
            "p95": float(np.percentile(value, 95)),
            "p5": float(np.percentile(value, 5)),
        }
    stats["ds_size"] = len(items)

    if print_stats:
        print_token_statistics(stats)

    return stats

def convert_message_list_to_text(messages: list) -> str:
    B_INST, E_INST = "[INST]", "[/INST]"
    B_SYS, E_SYS = "<<SYS>>\n", "\n<</SYS>>\n\n"
    text = ""

    if messages[0]["role"] == "system":
        messages = [
            {
                "role": messages[1]["role"],
                "content": B_SYS
                + messages[0]["content"]
                + E_SYS
                + messages[1]["content"],
            }
        ] + messages[2:]

    assert all([msg["role"] == "user" for msg in messages[::2]]) and all(
            [msg["role"] == "assistant" for msg in messages[1::2]]
        ), (
            "model only supports 'system','user' and 'assistant' roles, "
            "starting with user and alternating (u/a/u/a/u...)"
        )

    texts = []
    for prompt, answer in zip(messages[::2], messages[1::2]):
        texts.append(f"{B_INST} {(prompt['content']).strip()} {E_INST} {(answer['content']).strip()} ")

    text = "</s><s>".join(texts)
    # add the bos and eos token at the beginning of the first turn and the end of the last turn
    text = "<s>" + text + " </s>"
    # During training last message should be from assistant (not from a user)
    assert (
        messages[-1]["role"] == "assistant"
    ), f"Last message must be from assistant, got {messages[-1]['role']}"

    return text

@cli.command()
def estimate_sequence_length(dataset: Path, tokenizer_id: str = "hf-internal-testing/llama-tokenizer"):
    SUPPORTED_CONTEXT_LENGTHS = [512, 1024, 2048, 4096]

    # Import the tokenizer
    tokenizer = LlamaTokenizerFast.from_pretrained(tokenizer_id)
    tokenizer.pad_token = tokenizer.eos_token

    # Load the dataset
    with open(dataset, 'r', encoding='utf-8') as f:
        items = json.load(f)

    # Auto calculate the context length
    stats = get_tokenized_stats(tokenizer, items, print_stats=True)
    ctx_length = None
    for ctx_length in SUPPORTED_CONTEXT_LENGTHS:
        if ctx_length > stats["token"]["p95"]:
            break

    print("Automatically selected context length: ", ctx_length)

if __name__ == "__main__":
    cli()
