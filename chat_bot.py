import torch
from peft import PeftModel
import transformers
import textwrap
from transformers import LlamaTokenizer, LlamaForCausalLM, GenerationConfig
from transformers.generation.utils import GreedySearchDecoderOnlyOutput
 
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"
DEVICE
tokenizer = LlamaTokenizer.from_pretrained("decapoda-research/llama-7b-hf")
model = LlamaForCausalLM.from_pretrained(
    "decapoda-research/llama-7b-hf",
    load_in_8bit=True,
    device_map="auto",
)
model = PeftModel.from_pretrained(model, "lora-alpaca-simple-2", torch_dtype=torch.float16)
model.config.pad_token_id = tokenizer.pad_token_id = 0  # unk
model.config.bos_token_id = 1
model.config.eos_token_id = 2
model = model.eval()
model = torch.compile(model)

PROMPT_TEMPLATE = f"""
Below is an instruction that describes a task. Write a response that appropriately completes the request.
 
### Instruction:
[INSTRUCTION]
 
### Response:
"""

def create_prompt(instruction: str) -> str:
    return PROMPT_TEMPLATE.replace("[INSTRUCTION]", instruction)

def generate_response(prompt: str, model: PeftModel) -> GreedySearchDecoderOnlyOutput:
    encoding = tokenizer(prompt, return_tensors="pt")
    input_ids = encoding["input_ids"].to(DEVICE)
 
    generation_config = GenerationConfig(
        temperature=0.1,
        top_p=0.75,
        repetition_penalty=1.1,
    )
    with torch.inference_mode():
        return model.generate(
            input_ids=input_ids,
            generation_config=generation_config,
            return_dict_in_generate=True,
            output_scores=True,
            max_new_tokens=256,
        )

def format_response(response: GreedySearchDecoderOnlyOutput) -> str:
    decoded_output = tokenizer.decode(response.sequences[0])
    response = decoded_output.split("### Response:")[1].strip()
    return "\n".join(textwrap.wrap(response))

def ask_alpaca(prompt: str, model: PeftModel = model) -> str:
    prompt = create_prompt(prompt)
    response = generate_response(prompt, model)
    print(prompt)
    print(format_response(response))
    print("")

def run_chat():
    current_history = ''
    base_ins = 'continue the dialogue between a Human and an Assistant, your role is the Assistant.\n'
    instruct = base_ins
    while True:
        value = input("Human: \n")
        if value == 'bbb':
            break

        current_history = current_history + f'Human: {value}\n'
        instruct = base_ins + current_history
        response = ask_alpaca(prompt = instruct)
        current_history = current_history + f'Assistant: {response}\n'
        print("Assistant:\n", response)
