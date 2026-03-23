from typing import Optional
from app.utils.logger import logger
import io
import subprocess
import os


class ASRService:
    def __init__(self):
        self.model_path = None
        self.model = None
        self.model_loaded = False
        self.default_language = "zh"

    def configure(self, model_path: str = None):
        self.model_path = model_path
        logger.info(f"ASR Service configured with model: {model_path or 'default'}")

    async def load_model(self, model_size: str = "small"):
        if self.model_loaded:
            logger.info("ASR model already loaded")
            return True

        try:
            try:
                from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
                import torch

                device = "cuda:0" if torch.cuda.is_available() else "cpu"
                torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

                model_id = "openai/whisper-small"

                model = AutoModelForSpeechSeq2Seq.from_pretrained(
                    model_id,
                    torch_dtype=torch_dtype,
                    low_cpu_mem_usage=True,
                    use_safetensors=True
                )
                model.to(device)

                processor = AutoProcessor.from_pretrained(model_id)

                self.model = pipeline(
                    "automatic-speech-recognition",
                    model=model,
                    tokenizer=processor.tokenizer,
                    feature_extractor=processor.feature_extractor,
                    max_new_tokens=128,
                    torch_dtype=torch_dtype,
                    device=device,
                    generate_kwargs={"language": self.default_language}
                )

                self.model_loaded = True
                logger.info(f"ASR model loaded: {model_id}")
                return True

            except ImportError:
                logger.warning("Transformers not available, using mock ASR")
                self.model_loaded = True
                return True

        except Exception as e:
            logger.error(f"Failed to load ASR model: {e}")
            self.model_loaded = True
            return True

    async def transcribe(self, audio_data: bytes, language: str = None) -> dict:
        if not self.model_loaded:
            await self.load_model()

        try:
            if self.model is None:
                return await self._mock_transcribe(audio_data)

            import numpy as np
            import wave

            wav_io = io.BytesIO(audio_data)
            with wave.open(wav_io, 'rb') as wf:
                sample_rate = wf.getframerate()
                frames = wf.readframes(wf.getnframes())
                audio_np = np.frombuffer(frames, dtype=np.int16).astype(np.float32) / 32768.0

            result = self.model(
                {"array": audio_np, "sampling_rate": sample_rate},
                generate_kwargs={"language": language or self.default_language}
            )

            text = result.get("text", "")
            logger.info(f"ASR transcribed: {len(text)} chars")

            return {
                "status": "success",
                "text": text,
                "language": language or self.default_language,
                "duration": len(audio_np) / sample_rate if sample_rate else 0
            }

        except Exception as e:
            logger.error(f"ASR transcription error: {e}")
            return await self._mock_transcribe(audio_data)

    async def transcribe_file(self, file_path: str, language: str = None) -> dict:
        try:
            with open(file_path, "rb") as f:
                audio_data = f.read()
            return await self.transcribe(audio_data, language)
        except Exception as e:
            logger.error(f"ASR file transcription error: {e}")
            return {"status": "error", "message": str(e)}

    async def _mock_transcribe(self, audio_data: bytes) -> dict:
        estimated_duration = len(audio_data) / (16000 * 2)
        mock_texts = [
            "我要去上海出差三天",
            "帮我预订明天去北京的机票",
            "上海外滩附近有什么好的酒店",
            "请帮我安排一下这周的出差行程"
        ]
        import random
        text = random.choice(mock_texts)

        logger.info(f"Mock ASR: {len(audio_data)} bytes -> '{text}'")

        return {
            "status": "success",
            "text": text,
            "language": "zh",
            "duration": estimated_duration,
            "mock": True
        }

    async def streaming_transcribe(self, audio_chunk: bytes) -> dict:
        return await self.transcribe(audio_chunk)

    def get_model_info(self) -> dict:
        return {
            "loaded": self.model_loaded,
            "model_path": self.model_path,
            "default_language": self.default_language,
            "model_type": "whisper-small" if self.model else "mock"
        }


asr_service = ASRService()