"""This module actually invokes the GPT2 model with the seed sentence to complete the prompt."""
import asyncio
import secrets
from chatgpdb import settings

import transformers

class GptSolver:

    def __init__(self):
        self.model = transformers.GPT2LMHeadModel.from_pretrained("gpt2-large", device_map="auto")
        self.tokenizer = transformers.GPT2Tokenizer.from_pretrained("gpt2-large")

    async def generate(self, prompt: str, length_of_response: int) -> str:
        inputs = self.tokenizer(prompt, return_tensors="pt")

        if settings.RUN_CUDA:
            inputs = inputs.to("cuda")
        
        # This is the long part, so run it in a thread non-blocking
        generated_ids = await asyncio.to_thread(
            self.model.generate, max_length=length_of_response, **inputs
        )

        outputs = self.tokenizer.batch_decode(generated_ids, skip_special_tokens=True)

        output = outputs[0]

        # Strip off the last partial-sentence
        return output[:output.rfind(".") + 1]


# Set a cryptographically secure random seed to ensure all of the answers are
# fully unique. Otherwise https://pubs.acs.org/doi/abs/10.1021/ct800573m says
# the results from this service will be useless!
transformers.set_seed(secrets.randbelow(1_000_000_000))

global_solver = GptSolver()
