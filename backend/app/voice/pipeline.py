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
        self.intent_agent = None
        self.llm_gateway = None

    async def initialize(self, session_id: str = None, use_llm: bool = True):
        self.session_id = session_id or f"voice_{id(self)}"
        await self.asr.load_model()
        
        if use_llm:
            try:
                from app.agents.intent import IntentUnderstandingAgent
                from app.llm.gateway import llm_gateway
                self.intent_agent = IntentUnderstandingAgent()
                self.intent_agent.enable_cot = True
                self.llm_gateway = llm_gateway
                logger.info(f"Voice pipeline initialized with LLM: {self.session_id}")
            except Exception as e:
                logger.warning(f"LLM not available for voice pipeline: {e}")
        
        logger.info(f"Voice pipeline initialized: {self.session_id}")
        return {"status": "initialized", "session_id": self.session_id, "llm_enabled": use_llm}

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

    async def process_with_llm(self, user_text: str) -> dict:
        """使用LLM处理用户文本输入"""
        if not self.intent_agent or not self.llm_gateway:
            return {"status": "error", "message": "LLM not initialized"}

        try:
            intent_result = await self.intent_agent.process({
                "session_id": self.session_id,
                "message": user_text
            })

            is_complete = intent_result.get("is_complete", False)
            missing_fields = intent_result.get("missing_fields", [])
            questions = intent_result.get("questions", [])
            entities = intent_result.get("entities", {})

            if not is_complete and missing_fields:
                follow_up_text = "为了更好地为您服务，请补充以下信息：\n\n"
                for i, q in enumerate(questions[:3], 1):
                    follow_up_text += f"{i}. {q.get('question', '请补充信息')}\n"
                
                return {
                    "status": "clarification_needed",
                    "user_text": user_text,
                    "entities": entities,
                    "missing_fields": missing_fields,
                    "questions": questions,
                    "response_text": follow_up_text,
                    "is_complete": False
                }
            
            return {
                "status": "complete",
                "user_text": user_text,
                "entities": entities,
                "is_complete": True,
                "response_text": intent_result.get("response_text", "")
            }

        except Exception as e:
            logger.error(f"LLM processing error: {e}")
            return {"status": "error", "message": str(e)}

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

    async def full_voice_turn(self, audio_data: bytes) -> dict:
        """完整的语音对话流程：ASR → LLM → TTS"""
        asr_result = await self.process_voice_input(audio_data)
        
        if asr_result.get("status") != "success":
            return {
                "status": "error",
                "message": "Failed to process voice input",
                "asr_result": asr_result
            }
        
        user_text = asr_result.get("user_text")
        
        llm_result = await self.process_with_llm(user_text)
        
        response_text = llm_result.get("response_text", "")
        audio_response = None
        
        if response_text:
            audio_response = await self.generate_voice_response(response_text)
        
        return {
            "status": "success",
            "user_text": user_text,
            "llm_result": llm_result,
            "response_text": response_text,
            "audio_response": audio_response,
            "session_id": self.session_id
        }

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