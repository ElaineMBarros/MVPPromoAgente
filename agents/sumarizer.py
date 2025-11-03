from agno import LLM
from core.promo_state import PromoState

class SummarizerAgent:
    def __init__(self, model: LLM, prompt_path: str):
        self.model = model
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt = f.read()

    async def summarize(self, state: PromoState):
        response = await self.model(self.prompt + "\n\n" + state.json())
        return response
