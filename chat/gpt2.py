"""This module actually invokes the GPT2 model with the seed sentence to complete the prompt."""
import asyncio
import secrets
from chatgpdb import settings

import transformers

transformers.set_seed(secrets.randbelow(1_000_000_000))


class GptSolver:
    def __init__(self):
        kws = {}
        if settings.RUN_CUDA:
            kws = dict(device_map="auto")
        self.pipeline = transformers.pipeline(
            "text-generation", model=settings.GPT_MODEL, **kws
        )

    async def generate(self, prompt: str, length_of_response: int) -> str:
        # Set a cryptographically secure random seed to ensure all of the answers are
        # fully unique. Otherwise https://pubs.acs.org/doi/abs/10.1021/ct800573m says
        # the results from this service will be useless!
        transformers.set_seed(secrets.randbelow(1_000_000_000))

        # This is the long part, so run it in a thread non-blocking
        outputs = await asyncio.to_thread(
            self.pipeline, prompt, min_length=length_of_response
        )

        output = outputs[0]["generated_text"]

        return f"{output}..."


global_solver = GptSolver()
