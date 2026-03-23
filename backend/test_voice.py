import asyncio
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.voice.tts import TTSService
from app.voice.asr import ASRService
from app.voice.pipeline import VoicePipeline


async def test_tts(tts, test_round):
    print(f"\n--- TTS Round {test_round} ---")

    test_texts = [
        "欢迎使用智能商旅助手，我可以帮您安排出差行程。",
        "请问您需要预订机票、酒店还是安排用餐？",
        "根据您的位置，我为您找到了三家合适的酒店。"
    ]

    for i, text in enumerate(test_texts):
        voice = "female_yiyi" if i % 2 == 0 else "female_xiaoyan"
        audio_data = await tts.synthesize(text, voice=voice, speed=1.0)

        assert len(audio_data) > 0, f"Empty audio data for: {text[:20]}..."

        is_wav = audio_data[:4] == b'RIFF'
        print(f"  [{i+1}] Text: {text[:25]}... -> {len(audio_data)} bytes, WAV: {is_wav}")

    voices = tts.get_available_voices()
    print(f"  Available voices: {len(voices)}")
    assert len(voices) >= 4, "Should have at least 4 voice options"

    print(f"✅ TTS Round {test_round} PASS")
    return True


async def test_asr(asr, test_round):
    print(f"\n--- ASR Round {test_round} ---")

    await asr.load_model()

    info = asr.get_model_info()
    print(f"  Model info: loaded={info['loaded']}, type={info['model_type']}")
    assert info['loaded'] == True, "Model should be loaded"

    mock_audio = b'RIFF' + b'\x00' * 1000 + b'WAVE'

    result = await asr.transcribe(mock_audio)
    assert result.get('status') == 'success', f"ASR failed: {result}"
    assert 'text' in result, "Should have transcribed text"
    print(f"  Transcribed: '{result['text']}' (mock: {result.get('mock', False)})")

    print(f"✅ ASR Round {test_round} PASS")
    return True


async def test_pipeline(pipeline, test_round):
    print(f"\n--- Pipeline Round {test_round} ---")

    init_result = await pipeline.initialize(f"test_session_{test_round}")
    assert init_result.get('status') == 'initialized', "Pipeline init failed"
    print(f"  Initialized: {init_result['session_id']}")

    mock_audio = b'RIFF' + b'\x00' * 2000 + b'WAVE'

    voice_input = await pipeline.process_voice_input(mock_audio)
    assert voice_input.get('status') == 'success', f"Voice input failed: {voice_input}"
    print(f"  Voice input: '{voice_input.get('user_text')}'")

    response_text = "好的，我来帮您安排明天的出差行程。"
    audio_response = await pipeline.generate_voice_response(response_text)
    assert len(audio_response) > 0, "Empty audio response"
    print(f"  Generated response: {len(audio_response)} bytes")

    full_turn = await pipeline.full_turn(mock_audio, response_text)
    assert full_turn.get('status') == 'success', f"Full turn failed: {full_turn}"
    print(f"  Full turn completed")

    voices = await pipeline.get_voices()
    print(f"  Available voices: {len(voices)}")

    asr_info = await pipeline.get_asr_info()
    print(f"  ASR model: {asr_info['model_type']}")

    history = pipeline.get_conversation_history()
    print(f"  History entries: {len(history)}")

    pipeline.clear_history()
    history_after_clear = pipeline.get_conversation_history()
    assert len(history_after_clear) == 0, "History should be cleared"
    print(f"  History cleared")

    print(f"✅ Pipeline Round {test_round} PASS")
    return True


async def test_streaming(tts, test_round):
    print(f"\n--- Streaming TTS Round {test_round} ---")

    text = "这是流式语音合成的测试内容。"
    chunks = []
    async for chunk in tts.synthesize_streaming(text):
        chunks.append(chunk)
        assert len(chunk) > 0, "Empty chunk"

    total_size = sum(len(c) for c in chunks)
    print(f"  Streamed {len(chunks)} chunks, total {total_size} bytes")
    assert total_size > 0, "Should have streamed data"

    print(f"✅ Streaming TTS Round {test_round} PASS")
    return True


async def test_error_handling(asr, test_round):
    print(f"\n--- Error Handling Round {test_round} ---")

    result = await asr.transcribe(b'')
    assert result.get('status') == 'success', "Should handle empty audio gracefully"
    print(f"  Empty audio handled: '{result.get('text', 'empty')}'")

    info = asr.get_model_info()
    assert 'model_type' in info, "Should return model info"
    print(f"  Model info: {info['model_type']}")

    print(f"✅ Error Handling Round {test_round} PASS")
    return True


async def run_voice_tests():
    print("=" * 60)
    print("VOICE MODULE 3-ROUND SELF-TEST")
    print("=" * 60)

    tts = TTSService()
    asr = ASRService()
    pipeline = VoicePipeline()

    tts.configure(None)
    asr.configure(None)

    all_passed = True

    for round_num in range(1, 4):
        print(f"\n{'='*60}")
        print(f"ROUND {round_num}/3")
        print(f"{'='*60}")

        try:
            await test_tts(tts, round_num)
        except Exception as e:
            print(f"❌ TTS Round {round_num} FAIL: {e}")
            all_passed = False

        try:
            await test_asr(asr, round_num)
        except Exception as e:
            print(f"❌ ASR Round {round_num} FAIL: {e}")
            all_passed = False

        try:
            await test_pipeline(pipeline, round_num)
        except Exception as e:
            print(f"❌ Pipeline Round {round_num} FAIL: {e}")
            all_passed = False

        try:
            await test_streaming(tts, round_num)
        except Exception as e:
            print(f"❌ Streaming Round {round_num} FAIL: {e}")
            all_passed = False

        try:
            await test_error_handling(asr, round_num)
        except Exception as e:
            print(f"❌ Error Handling Round {round_num} FAIL: {e}")
            all_passed = False

    print("\n" + "=" * 60)
    if all_passed:
        print("✅✅✅ ALL 3 ROUNDS PASSED ✅✅✅")
    else:
        print("❌ SOME TESTS FAILED")
    print("=" * 60)

    return all_passed


if __name__ == "__main__":
    result = asyncio.run(run_voice_tests())
    sys.exit(0 if result else 1)
