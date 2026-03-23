from typing import Optional
from app.utils.logger import logger
import base64
import io


class TTSService:
    def __init__(self):
        self.api_endpoint = None
        self.api_key = None
        self.default_voice = "female_yiyi"
        self.voice_options = {
            "female_yiyi": "小艺",
            "female_xiaoyan": "小燕",
            "male_john": "约翰",
            "female_ami": "艾米"
        }

    def configure(self, api_endpoint: str, api_key: str = None):
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        logger.info(f"TTS Service configured with endpoint: {api_endpoint}")

    async def synthesize(self, text: str, voice: str = None, speed: float = 1.0) -> bytes:
        if not self.api_endpoint:
            logger.warning("TTS endpoint not configured, using mock audio")
            return self._generate_mock_audio(text)

        try:
            voice_id = voice or self.default_voice

            payload = {
                "text": text,
                "voice": voice_id,
                "speed": speed
            }

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            import httpx
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    self.api_endpoint,
                    json=payload,
                    headers=headers
                )

                if response.status_code == 200:
                    audio_data = response.content
                    logger.info(f"TTS synthesized {len(text)} chars -> {len(audio_data)} bytes")
                    return audio_data
                else:
                    logger.error(f"TTS API error: {response.status_code}")
                    return self._generate_mock_audio(text)

        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            return self._generate_mock_audio(text)

    async def synthesize_streaming(self, text: str, voice: str = None, speed: float = 1.0):
        if not self.api_endpoint:
            mock_audio = self._generate_mock_audio(text)
            yield mock_audio
            return

        try:
            voice_id = voice or self.default_voice

            payload = {
                "text": text,
                "voice": voice_id,
                "speed": speed,
                "stream": True
            }

            headers = {"Content-Type": "application/json"}
            if self.api_key:
                headers["Authorization"] = f"Bearer {self.api_key}"

            import httpx
            async with httpx.AsyncClient(timeout=60.0) as client:
                async with client.stream("POST", self.api_endpoint, json=payload, headers=headers) as response:
                    async for chunk in response.aiter_bytes(chunk_size=8192):
                        if chunk:
                            yield chunk

        except Exception as e:
            logger.error(f"TTS streaming error: {e}")
            yield self._generate_mock_audio(text)

    def _generate_mock_audio(self, text: str) -> bytes:
        wav_header = bytearray([
            0x52, 0x49, 0x46, 0x46,
            0x24, 0x00, 0x00, 0x00,
            0x57, 0x41, 0x56, 0x45,
            0x66, 0x6D, 0x74, 0x20,
            0x10, 0x00, 0x00, 0x00,
            0x01, 0x00, 0x01, 0x00,
            0x44, 0xAC, 0x00, 0x00,
            0x88, 0x58, 0x01, 0x00,
            0x02, 0x00, 0x10, 0x00,
            0x64, 0x61, 0x74, 0x61,
            0x00, 0x00, 0x00, 0x00
        ])

        num_samples = min(len(text) * 500, 48000)
        audio_data = bytes([0] * (num_samples * 2))
        wav_header[4:8] = (36 + len(audio_data)).to_bytes(4, 'little')
        wav_header[40:44] = len(audio_data).to_bytes(4, 'little')

        logger.info(f"Generated mock audio: {len(text)} chars -> {len(wav_header) + len(audio_data)} bytes")
        return bytes(wav_header) + audio_data

    def get_available_voices(self) -> list:
        return [
            {"id": k, "name": v} for k, v in self.voice_options.items()
        ]


tts_service = TTSService()