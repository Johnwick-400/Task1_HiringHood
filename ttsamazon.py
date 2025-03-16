import streamlit as st
import boto3
import os
import time
import pygame
from io import BytesIO
import re
from tempfile import NamedTemporaryFile

pygame.mixer.init()

class TTSProcessor:
    def __init__(self):
        self.polly_client = boto3.client(
            'polly',
            region_name='us-east-1'
        )
        
        self.voices = {
            "Matthew (US Male)": {"VoiceId": "Matthew", "Engine": "neural"},
            "Joanna (US Female)": {"VoiceId": "Joanna", "Engine": "neural"},
            "Kevin (US Child)": {"VoiceId": "Kevin", "Engine": "neural"},
            "Kimberly (US Female)": {"VoiceId": "Kimberly", "Engine": "neural"},
            "Salli (US Female)": {"VoiceId": "Salli", "Engine": "neural"},
            "Joey (US Male)": {"VoiceId": "Joey", "Engine": "neural"},
            
            "Amy (UK Female)": {"VoiceId": "Amy", "Engine": "neural"},
            "Emma (UK Female)": {"VoiceId": "Emma", "Engine": "neural"},
            "Brian (UK Male)": {"VoiceId": "Brian", "Engine": "neural"},
            
            "Olivia (Australian Female)": {"VoiceId": "Olivia", "Engine": "neural"},
            
            "Kajal (Indian Female)": {"VoiceId": "Kajal", "Engine": "neural"},
            
            "Ayanda (South African Female)": {"VoiceId": "Ayanda", "Engine": "neural"},
        }
        
        self.default_voice = "Joanna (US Female)"
        
        self.temp_dir = "temp_audio"
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)

    def validate_text(self, text):
        if not text.strip():
            return "", "Error: Text input is empty."
        
        cleaned_text = re.sub(r'\s+', ' ', text).strip()
        
        if len(cleaned_text) > 3000:
            return cleaned_text[:3000], "Warning: Text was truncated to 3000 characters."
        
        special_chars = re.findall(r'[^\w\s.,!?\'"-:;()]', cleaned_text)
        if special_chars:
            unique_chars = set(special_chars)
            return cleaned_text, f"Warning: Text contains some special characters that may affect pronunciation: {', '.join(unique_chars)}"
        
        return cleaned_text, "Text validation successful."

    def generate_speech(self, text, voice_name, rate="medium", volume="medium"):
        cleaned_text, validation_msg = self.validate_text(text)
        if not cleaned_text:
            return None, validation_msg
        
        voice_config = self.voices.get(voice_name, self.voices[self.default_voice])
        
        rate_values = {"slow": "x-slow", "medium": "medium", "fast": "x-fast"}
        volume_values = {"low": "soft", "medium": "medium", "high": "loud"}
        
        ssml_text = (
            f'<speak>'
            f'<prosody rate="{rate_values[rate]}" volume="{volume_values[volume]}">'
            f'{cleaned_text}'
            f'</prosody>'
            f'</speak>'
        )
        
        try:
            response = self.polly_client.synthesize_speech(
                Engine=voice_config["Engine"],
                VoiceId=voice_config["VoiceId"],
                OutputFormat='mp3',
                Text=ssml_text,
                TextType='ssml'
            )
            
            temp_file = NamedTemporaryFile(delete=False, suffix='.mp3', dir=self.temp_dir)
            temp_file.close()
            
            if "AudioStream" in response:
                with open(temp_file.name, 'wb') as audio_file:
                    audio_file.write(response['AudioStream'].read())
                return temp_file.name, validation_msg
            else:
                return None, "Error: Failed to generate audio stream."
                
        except Exception as e:
            return None, f"Error: {str(e)}"
    
    def play_audio(self, audio_file_path):
        if audio_file_path and os.path.exists(audio_file_path):
            try:
                pygame.mixer.music.load(audio_file_path)
                pygame.mixer.music.play()
                while pygame.mixer.music.get_busy():
                    pygame.time.Clock().tick(10)
                return True
            except Exception as e:
                return f"Error playing audio: {str(e)}"
        return "Audio file not found."
        
    def cleanup_old_files(self, max_age_minutes=30):
        current_time = time.time()
        for filename in os.listdir(self.temp_dir):
            file_path = os.path.join(self.temp_dir, filename)
            if os.path.isfile(file_path):
                file_age = (current_time - os.path.getmtime(file_path)) / 60
                if file_age > max_age_minutes:
                    os.remove(file_path)

def main():
    st.set_page_config(page_title="Text-to-Speech with Amazon Polly", layout="wide")
    
    st.title("Text-to-Speech Converter")
    st.subheader("Convert your text to natural-sounding speech using Amazon Polly")
    
    tts = TTSProcessor()
    
    tts.cleanup_old_files()
    
    # Initialize all session state variables
    if 'audio_file' not in st.session_state:
        st.session_state.audio_file = None
        
    if 'validation_result' not in st.session_state:
        st.session_state.validation_result = None
        
    if 'cleaned_text' not in st.session_state:
        st.session_state.cleaned_text = None
        
    if 'last_validated_text' not in st.session_state:
        st.session_state.last_validated_text = ""
    
    text_input = st.text_area("Enter text to convert to speech:", height=150, key="text_input")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        voice_selection = st.selectbox(
            "Select Voice:",
            options=list(tts.voices.keys()),
            index=list(tts.voices.keys()).index(tts.default_voice)
        )
    
    with col2:
        rate_selection = st.select_slider(
            "Speech Rate:",
            options=["slow", "medium", "fast"],
            value="medium"
        )
    
    with col3:
        volume_selection = st.select_slider(
            "Volume Level:",
            options=["low", "medium", "high"],
            value="medium"
        )
    
    # Validate text button
    if st.button("✓ Validate Text"):
        if text_input:
            cleaned_text, validation_msg = tts.validate_text(text_input)
            st.session_state.validation_result = validation_msg
            st.session_state.cleaned_text = cleaned_text
            st.session_state.last_validated_text = text_input
            
            if "Error" in validation_msg:
                st.error(validation_msg)
            elif "Warning" in validation_msg:
                st.warning(validation_msg)
            else:
                st.success(validation_msg)
                
            if cleaned_text != text_input:
                st.info("The input text was modified for better TTS results.")
        else:
            st.warning("Please enter some text to validate.")
    
    # Show validation result if available
    if st.session_state.validation_result and "Error" not in st.session_state.validation_result:
        st.success("Text is valid and ready for conversion.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Generate Speech"):
            if not text_input:
                st.warning("Please enter some text to convert to speech.")
                return
                
            # Validate text if not already validated or if text has changed
            if st.session_state.cleaned_text is None or text_input != st.session_state.last_validated_text:
                cleaned_text, validation_msg = tts.validate_text(text_input)
                st.session_state.validation_result = validation_msg
                st.session_state.cleaned_text = cleaned_text
                st.session_state.last_validated_text = text_input
                
                if "Error" in validation_msg:
                    st.error(validation_msg)
                    return
                elif "Warning" in validation_msg:
                    st.warning(validation_msg)
            
            with st.spinner("Generating speech..."):
                audio_file, message = tts.generate_speech(
                    text_input, 
                    voice_selection, 
                    rate_selection, 
                    volume_selection
                )
                
                if audio_file:
                    st.session_state.audio_file = audio_file
                    st.success("Speech generated successfully!")
                    
                    with open(audio_file, "rb") as f:
                        audio_bytes = f.read()
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.error(message)
    
    with col2:
        if st.button("▶️ Play Audio") and st.session_state.audio_file:
            status = tts.play_audio(st.session_state.audio_file)
            if status is not True:
                st.error(status)
    
    if st.session_state.audio_file:
        with open(st.session_state.audio_file, "rb") as f:
            audio_bytes = f.read()
            
        st.download_button(
            label="Download Audio File",
            data=audio_bytes,
            file_name="speech_output.mp3",
            mime="audio/mp3"
        )
    
    with st.expander("Advanced Options & Information"):
        st.markdown("### Text Validation Results")
        if st.session_state.validation_result:
            st.write(st.session_state.validation_result)
            
            if st.session_state.cleaned_text and st.session_state.cleaned_text != text_input:
                st.write("Modified text:")
                st.code(st.session_state.cleaned_text)
        
        st.markdown("### Available Voices")
        voices_df = []
        for name, config in tts.voices.items():
            accent = name.split("(")[1].replace(")", "")
            voice_id = config["VoiceId"]
            voices_df.append({"Voice Name": name, "Accent": accent, "Voice ID": voice_id})
        
        st.table(voices_df)
    
    st.markdown("---")
    st.markdown("### How to use this application")
    st.markdown("""
    1. Enter your text in the text area
    2. Click "Validate Text" to check for potential issues or modifications if required
    3. Select voice, speech rate, and volume settings
    4. Click "Generate Speech" to create the audio
    5. Use the audio player or "Play Audio" button to listen
    6. Download the MP3 file if needed
    """)

def run_unit_tests():
    tts = TTSProcessor()
    
    text1 = ""
    result1, msg1 = tts.validate_text(text1)
    assert result1 == "", "Empty text validation failed"
    assert "Error" in msg1, "Empty text error message failed"
    
    text2 = "This is a normal text without special characters."
    result2, msg2 = tts.validate_text(text2)
    assert result2 == text2, "Normal text validation failed"
    assert "successful" in msg2, "Normal text success message failed"
    
    text3 = "Text with special chars: ™ § ¶ © ®"
    result3, msg3 = tts.validate_text(text3)
    assert "Warning" in msg3, "Special characters warning failed"
    
    text4 = "a" * 4000
    result4, msg4 = tts.validate_text(text4)
    assert len(result4) == 3000, "Text truncation failed"
    assert "Warning" in msg4, "Truncation warning failed"
    
    print("All validation tests passed!")

if __name__ == "__main__":
    main()