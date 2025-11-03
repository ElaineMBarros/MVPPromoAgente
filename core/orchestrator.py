from core.promo_state import PromoState

class Orchestrator:
    def __init__(self, extractor, validator, summarizer, memory):
        self.extractor = extractor
        self.validator = validator
        self.summarizer = summarizer
        self.memory = memory

    async def handle(self, message: str, session_id: str) -> str:
        state = await self.memory.load(session_id)
        state = await self.extractor.extract(message, state)

        missing = state.missing_fields()
        if missing:
            return f"Perfeito, já registrei essas informações. Agora só preciso: {', '.join(missing)}"

        validation = await self.validator.validate(state)
        if validation != "OK":
            return validation

        return await self.summarizer.summarize(state)
