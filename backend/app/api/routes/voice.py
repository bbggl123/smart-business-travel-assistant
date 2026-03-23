from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from typing import Optional
import json

router = APIRouter(prefix="/voice", tags=["voice"])


@router.post("/tts")
async def text_to_speech(
    text: str = Form(...),
    voice: Optional[str] = Form(None),
    speed: Optional[float] = Form(1.0)
):
    from app.voice import tts_service

    try:
        audio_data = await tts_service.synthesize(text, voice=voice, speed=speed)

        return StreamingResponse(
            iter([audio_data]),
            media_type="audio/wav",
            headers={
                "Content-Disposition": "attachment; filename=output.wav"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")


@router.post("/tts/stream")
async def text_to_speech_streaming(
    text: str = Form(...),
    voice: Optional[str] = Form(None),
    speed: Optional[float] = Form(1.0)
):
    from app.voice import tts_service

    async def generate():
        async for chunk in tts_service.synthesize_streaming(text, voice=voice, speed=speed):
            yield chunk

    return StreamingResponse(
        generate(),
        media_type="audio/wav",
        headers={
            "Content-Disposition": "attachment; filename=output.wav"
        }
    )


@router.post("/asr")
async def speech_to_text(
    audio: UploadFile = File(...),
    language: Optional[str] = Form(None)
):
    from app.voice import asr_service

    try:
        audio_data = await audio.read()

        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        result = await asr_service.transcribe(audio_data, language=language)

        if result.get("status") == "success":
            return JSONResponse(content={
                "code": 0,
                "message": "success",
                "data": {
                    "text": result.get("text"),
                    "language": result.get("language", "zh"),
                    "duration": result.get("duration", 0)
                }
            })
        else:
            raise HTTPException(status_code=500, detail="Transcription failed")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR error: {str(e)}")


@router.post("/asr/bytes")
async def speech_to_text_bytes(
    audio_data: bytes,
    language: Optional[str] = None
):
    from app.voice import asr_service

    try:
        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio data")

        result = await asr_service.transcribe(audio_data, language=language)

        if result.get("status") == "success":
            return JSONResponse(content={
                "code": 0,
                "message": "success",
                "data": {
                    "text": result.get("text"),
                    "language": result.get("language", "zh"),
                    "duration": result.get("duration", 0)
                }
            })
        else:
            raise HTTPException(status_code=500, detail="Transcription failed")

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"ASR error: {str(e)}")


@router.post("/conversation")
async def voice_conversation(
    audio: UploadFile = File(...),
    session_id: Optional[str] = Form(None)
):
    from app.voice import voice_pipeline

    try:
        audio_data = await audio.read()

        if len(audio_data) == 0:
            raise HTTPException(status_code=400, detail="Empty audio file")

        await voice_pipeline.initialize(session_id)

        result = await voice_pipeline.process_voice_input(audio_data)

        return JSONResponse(content={
            "code": 0,
            "message": "success",
            "data": result
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Voice conversation error: {str(e)}")


@router.get("/voices")
async def get_available_voices():
    from app.voice import tts_service

    try:
        voices = tts_service.get_available_voices()
        return JSONResponse(content={
            "code": 0,
            "message": "success",
            "data": {
                "voices": voices
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/asr/info")
async def get_asr_info():
    from app.voice import asr_service

    try:
        info = asr_service.get_model_info()
        return JSONResponse(content={
            "code": 0,
            "message": "success",
            "data": info
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/load-model")
async def load_asr_model(model_size: str = "small"):
    from app.voice import asr_service

    try:
        success = await asr_service.load_model(model_size)
        return JSONResponse(content={
            "code": 0,
            "message": "success" if success else "failed",
            "data": {
                "loaded": success
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.get("/history")
async def get_voice_history():
    from app.voice import voice_pipeline

    try:
        history = voice_pipeline.get_conversation_history()
        return JSONResponse(content={
            "code": 0,
            "message": "success",
            "data": {
                "history": history,
                "session_id": voice_pipeline.session_id
            }
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")


@router.post("/history/clear")
async def clear_voice_history():
    from app.voice import voice_pipeline

    try:
        voice_pipeline.clear_history()
        return JSONResponse(content={
            "code": 0,
            "message": "success"
        })
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")