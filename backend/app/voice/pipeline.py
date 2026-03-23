from typing import Optional, AsyncGenerator
from app.utils.logger import logger
from app.voice.tts import tts_service
from app.voice.asr import asr_service


class VoicePipeline:
    def __init__(self):
        self.tts = tts_service
        self.asr = asr_service
        self.conversation_history = []
        self.session_id = None

    async def initialize(self, session_id: str = None):
        self.session_id = session_id or f"voice_{id(self)}"
        await self.asr.load_model()
        logger.info(f"Voice pipeline initialized: {self.session_id}")
        return {"status": "initialized", "session_id": self.session_id}

    async def process_voice_input(self, audio_data: bytes) -> dict:
        asr_result = await self.asr.transcribe(audio_data)

        if asr_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Voice transcription failed",
                "asr_result": asr_result
            }

        user_text = asr_result.get("text", "")

        self.conversation_history.append({
            "role": "user",
            "content": user_text,
            "audio_duration": asr_result.get("duration", 0)
        })

        return {
            "status": "success",
            "user_text": user_text,
            "language": asr_result.get("language", "zh"),
            "duration": asr_result.get("duration", 0)
        }

    async def generate_voice_response(self, text: str, voice: str = None) -> bytes:
        audio_data = await self.tts.synthesize(text, voice=voice)

        self.conversation_history.append({
            "role": "assistant",
            "content": text,
            "audio_size": len(audio_data)
        })

        return audio_data

    async def generate_voice_response_streaming(
        self,
        text: str,
        voice: str = None
    ) -> AsyncGenerator[bytes, None]:
        async for chunk in self.tts.synthesize_streaming(text, voice=voice):
            yield chunk

    async def full_turn(self, audio_data: bytes, agent_response: str = None) -> dict:
        asr_result = await self.process_voice_input(audio_data)

        if asr_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Failed to process voice input",
                "asr_result": asr_result
            }

        user_text = asr_result.get("user_text")

        if agent_response:
            audio_response = await self.generate_voice_response(agent_response)
        else:
            audio_response = None

        return {
            "status": "success",
            "user_text": user_text,
            "agent_response": agent_response,
            "audio_response": audio_response,
            "session_id": self.session_id
        }

    def get_conversation_history(self) -> list:
        return self.conversation_history

    def clear_history(self):
        self.conversation_history = []
        logger.info(f"Conversation history cleared for session: {self.session_id}")

    async def get_voices(self) -> list:
        return self.tts.get_available_voices()

    async def get_asr_info(self) -> dict:
        return self.asr.get_model_info()


voice_pipeline = VoicePipeline()