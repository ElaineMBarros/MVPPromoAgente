import json
from agno import LLM
from core.promo_state import PromoState

class ExtractorAgent:
    def __init__(self, model: LLM, prompt_path: str):
        self.model = model
        with open(prompt_path, "r", encoding="utf-8") as f:
            self.prompt = f.read()

    async def extract(self, text: str, state: PromoState) -> PromoState:
        response = await self.model(
            self.prompt + "\n\nTEXTO:\n" + text,
            response_format="json"
        )
        data = json.loads(response)

        for field, value in data.items():
            if value and not getattr(state, field):
                setattr(state, field, value.strip())

        return state
