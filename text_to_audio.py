import uuid
import os
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
from gtts import gTTS
from config import ELEVENLABS_API_KEY

elevenlabs = ElevenLabs(
    api_key=ELEVENLABS_API_KEY,
)


def text_to_speech_file(text: str, folder: str, voice_id: str = "pNInz6obpgDQGcFmaJgB") -> str:
    save_file_path = os.path.join(f"user_uploads/{folder}", "audio.mp3")
    
    # Ensure directory exists
    os.makedirs(os.path.dirname(save_file_path), exist_ok=True)
    
    try:
        print(f"Attempting to generate voice via ElevenLabs (voice: {voice_id})...")
        # Calling the text_to_speech conversion API
        response = elevenlabs.text_to_speech.convert(
            voice_id=voice_id,
            output_format="mp3_22050_32",
            text=text,
            model_id="eleven_turbo_v2_5", # low latency turbo model
            voice_settings=VoiceSettings(
                stability=0.0,
                similarity_boost=1.0,
                style=0.0,
                use_speaker_boost=True,
                speed=1.0,
            ),
        )

        # Writing the audio to a file
        with open(save_file_path, "wb") as f:
            for chunk in response:
                if chunk:
                    f.write(chunk)
                    
        print(f"{save_file_path}: ElevenLabs audio saved successfully!")
    except Exception as e:
        print(f"WARNING: ElevenLabs failed ({e}). Falling back to Google Text-to-Speech (gTTS)...")
        try:
            # Fallback to gTTS
            tts = gTTS(text=text, lang='en')
            tts.save(save_file_path)
            print(f"{save_file_path}: gTTS audio saved successfully!")
        except Exception as ge:
            print(f"ERROR: gTTS fallback also failed ({ge})")
            raise ge

    # Return the path of the saved audio file
    return save_file_path

