from agno import LLM
from core.promo_state import PromoState

class ValidatorAgent:
    def __init__(self, model: LLM, prompt_path: str):
        self.model = model
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt = f.read()

    async def validate(self, state: PromoState):
        text = self.prompt + "\n\n" + state.json()
        response = await self.model(text)
        return response.strip()
