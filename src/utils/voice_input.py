# voice_input.py
import streamlit as st
from audio_recorder_streamlit import audio_recorder
from openai import OpenAI
import io
import os

class VoiceInterface:
    def __init__(self, tts_voice="alloy", tts_model="tts-1", stt_model="whisper-1"):
        self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
        self.tts_voice = tts_voice
        self.tts_model = tts_model
        self.stt_model = stt_model

    def get_voice_input(self):
        """Records audio and transcribes it using Whisper."""
        st.write("### 🎤 Or, tell me how you feel:")
    
        # Display audio recorder
        audio_bytes = audio_recorder(
            text="Click to talk",
            recording_color="#e8bdeb",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="2x",
            pause_threshold=3.0
        )
    
        transcribed_text = None
    
        if audio_bytes:
            try:
                # Create a file-like object from audio bytes
                audio_file = io.BytesIO(audio_bytes)
                audio_file.name = "recording.wav"
            
                # Send to OpenAI Whisper for transcription
                with st.spinner('Transcribing your voice...'):
                    transcription = self.client.audio.transcriptions.create(
                        model=self.stt_model,
                        file=audio_file
                    )

                transcribed_text = transcription.text
                st.success("🎶 I heard you!")
                st.write(f"**You said:** {transcribed_text}")
            
            except Exception as e:
                st.error(f"Sorry, I couldn't process the audio. Error: {str(e)}")
    
        return transcribed_text

    def text_to_speech(self, text):
        """Converts text to speech using TTS."""
        try:
            response = self.client.audio.speech.create(
                model=self.tts_model,
                voice=self.tts_voice,
                input=text
            )
            audio_bytes = io.BytesIO()
            for chunk in response.iter_bytes():
                audio_bytes.write(chunk)
            audio_bytes.seek(0)
            return audio_bytes
        except Exception as e:
            st.error(f"Could not generate speech: {e}")
            return None

# Global instance
voice_interface = VoiceInterface()