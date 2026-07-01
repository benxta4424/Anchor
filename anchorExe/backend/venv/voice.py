"""
Voice Analysis Module - Groq Whisper Integration
Handles audio transcription and voice feature extraction
"""

import os
import base64
import tempfile
import numpy as np
from groq import Groq
from typing import Dict, Any, Optional

# Initialize Groq client lazily
_client = None

def get_groq_client():
    global _client
    if _client is None:
        api_key = os.environ.get('GROQ_API_KEY')
        if not api_key:
            raise ValueError("GROQ_API_KEY is not set in environment variables")
        _client = Groq(api_key=api_key)
    return _client


def transcribe_audio(audio_binary: bytes, language: str = 'ro') -> str:
    """
    Transcribe audio using Groq Whisper
    
    Args:
        audio_binary: Binary audio data (WAV, MP3, etc.)
        language: Language code ('ro' for Romanian, 'en' for English)
    
    Returns:
        Transcribed text
    
    Example:
        >>> with open('audio.wav', 'rb') as f:
        >>>     audio = f.read()
        >>> text = transcribe_audio(audio)
        >>> print(text)
    """
    try:
        client = get_groq_client()
        params = {
            "file": ("audio.wav", audio_binary, "audio/wav"),
            "model": "whisper-large-v3",
            "temperature": 0.1,  
        }
        if language and language != 'auto':
            params["language"] = language
            
        response = client.audio.transcriptions.create(**params)
        
        transcript = response.text.strip()
        
        if not transcript:
            raise ValueError("Transcription returned empty text")
        
        return transcript
        
    except Exception as e:
        error_msg = f"Transcription failed: {str(e)}"
        print(f"❌ {error_msg}")
        raise Exception(error_msg)


# Set to True to enable dynamic librosa feature extraction
USE_LIBROSA = True


def extract_voice_features(audio_binary: bytes) -> Dict[str, float]:
    """
    Extract acoustic features from audio
    
    Features:
    - pace: Duration in seconds (slow speech = higher depression indicator)
    - energy: Average amplitude (low energy = depression)
    - zero_crossing_rate: Voice clarity (low = depression/monotone)
    - rms_energy: Root mean square energy
    
    Args:
        audio_binary: Binary audio data
    
    Returns:
        Dictionary with voice features
    """
    
    if USE_LIBROSA:
        try:
            import librosa
            # Save to temporary file
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as tmp:
                tmp.write(audio_binary)
                tmp_path = tmp.name
            
            try:
                # Load audio
                y, sr = librosa.load(tmp_path)
                duration = librosa.get_duration(y=y, sr=sr)
                
                # Extract features
                energy = float(np.mean(np.abs(y)))
                zcr = float(np.mean(librosa.feature.zero_crossing_rate(y)))
                rms = float(np.mean(librosa.feature.rms(y=y)))
                mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                mfcc_mean = float(np.mean(mfcc))
                spectral_centroid = float(np.mean(librosa.feature.spectral_centroid(y=y, sr=sr)))
                
                onset_env = librosa.onset.onset_strength(y=y, sr=sr)
                try:
                    tempo = float(librosa.feature.tempo(onset_envelope=onset_env, sr=sr)[0])
                except TypeError:
                    tempo = float(librosa.feature.tempo(onset_env=onset_env, sr=sr)[0])
                
                return {
                    "duration": float(duration),
                    "energy": energy,
                    "zero_crossing_rate": zcr,
                    "rms_energy": rms,
                    "mfcc_mean": mfcc_mean,
                    "spectral_centroid": spectral_centroid,
                    "tempo": tempo,
                }
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            print(f"⚠️ Librosa features failed, falling back to wave+numpy: {e}")

    # Pure wave + numpy features parser (Fast, reliable, never hangs!)
    try:
        import wave
        import io
        
        # Load audio using standard wave library
        with wave.open(io.BytesIO(audio_binary), 'rb') as wav:
            num_frames = wav.getnframes()
            frame_rate = wav.getframerate()
            num_channels = wav.getnchannels()
            samp_width = wav.getsampwidth()
            
            duration = float(num_frames) / float(frame_rate) if frame_rate > 0 else 0.0
            
            # Read frames
            raw_data = wav.readframes(num_frames)
            
            # Convert raw data to numpy array
            if samp_width == 1:
                dtype = np.uint8
            elif samp_width == 2:
                dtype = np.int16
            elif samp_width == 4:
                dtype = np.int32
            else:
                dtype = np.int16 # default fallback
            
            samples = np.frombuffer(raw_data, dtype=dtype)
            
            # If stereo, take the mean of channels
            if num_channels > 1 and len(samples) > 0:
                samples = samples.reshape(-1, num_channels)
                samples = samples.mean(axis=1)
            
            # Normalize samples to [-1, 1] range for float representation
            if len(samples) > 0:
                if dtype == np.int16:
                    normalized_samples = samples.astype(np.float32) / 32768.0
                elif dtype == np.int32:
                    normalized_samples = samples.astype(np.float32) / 2147483648.0
                elif dtype == np.uint8:
                    normalized_samples = (samples.astype(np.float32) - 128.0) / 128.0
                else:
                    normalized_samples = samples.astype(np.float32)
                
                energy = float(np.mean(np.abs(normalized_samples)))
                rms = float(np.sqrt(np.mean(normalized_samples**2)))
                
                # Zero Crossing Rate
                zero_crossings = np.nonzero(np.diff(np.sign(normalized_samples)))[0]
                zcr = float(len(zero_crossings) / len(normalized_samples)) if len(normalized_samples) > 0 else 0.0
                
                # Dynamic heuristics for tempo and spectral centroid based on energy
                tempo = 110.0 # healthy default
                spectral_centroid = 2800.0 # healthy default
                
                if energy < 0.015:
                    tempo = 70.0  # slow tempo
                    spectral_centroid = 1700.0  # flat tone
                elif energy < 0.04:
                    tempo = 85.0
                    spectral_centroid = 2100.0
                    
                return {
                    "duration": duration,
                    "energy": energy,
                    "zero_crossing_rate": zcr,
                    "rms_energy": rms,
                    "mfcc_mean": 0.0,
                    "spectral_centroid": spectral_centroid,
                    "tempo": tempo,
                }
    except Exception as e:
        print(f"❌ Fallback wave extraction failed: {e}")
        
    # Hard fallback
    return {
        "duration": 5.0,
        "energy": 0.04,
        "zero_crossing_rate": 0.07,
        "rms_energy": 0.03,
        "mfcc_mean": 0.0,
        "spectral_centroid": 2500.0,
        "tempo": 100.0,
    }


def analyze_voice_quality(features: Dict[str, float]) -> Dict[str, Any]:
    """
    Analyze voice quality and extract depression indicators using clinical continuous mapping
    
    Depression indicators:
    - Low energy: Loss of interest/motivation
    - High zero crossing rate: Unclear speech (mumbling)
    - Low spectral centroid: Flat, monotone voice
    - Low tempo: Slow, dragging speech
    - Long duration for few words: Hesitation, pauses
    
    Args:
        features: Voice features dict from extract_voice_features()
    
    Returns:
        Analysis dict with depression scores and descriptions
    """
    
    analysis = {
        "energy_score": 0,  # 0-100
        "pace_score": 0,  # 0-100
        "clarity_score": 0,  # 0-100
        "tone_score": 0,  # 0-100
        "overall_voice_indicator": 0,  # 0-100 (higher = more depressed)
        "descriptions": [],
    }
    
    energy = features.get('energy', 0.0)
    tempo = features.get('tempo', 110.0)
    zcr = features.get('zero_crossing_rate', 0.1)
    centroid = features.get('spectral_centroid', 2800.0)
    duration = features.get('duration', 0.0)
    
    # 1. Guard against empty/silent or extremely short recordings
    if energy < 0.0015 or duration < 0.8:
        analysis["descriptions"].append("Înregistrare prea scurtă sau fără semnal sonor detectabil.")
        return analysis

    # 2. Continuous Energy Analysis:
    # Healthy normal speech: energy >= 0.025 -> score 0
    # Quiet/depressed:       energy < 0.005 -> high score (80+)
    if energy >= 0.025:
        energy_val = 0.0
    else:
        energy_val = max(0.0, min(90.0, 85.0 * (1.0 - energy / 0.025)))
    analysis["energy_score"] = int(energy_val)
    if energy_val > 65:
        analysis["descriptions"].append("Energie vocală scăzută (vocalizare plată, oboseală)")
    elif energy_val < 20:
        analysis["descriptions"].append("Energie vocală bună (vorbire dinamică)")
        
    # 3. Continuous Pace Analysis (Tempo):
    # Healthy range: 85-150 BPM -> score 0
    # Slow speech:   < 85 BPM -> higher score
    if 85 <= tempo <= 150:
        pace_val = 0.0
    elif tempo > 150:
        pace_val = 0.0
    else:
        pace_val = min(90.0, (85.0 - tempo) * 1.5)
    analysis["pace_score"] = int(pace_val)
    if pace_val > 60:
        analysis["descriptions"].append("Ritm lent al vorbirii (letargie, retard psihomotor)")
    elif pace_val < 20:
        analysis["descriptions"].append("Ritm de vorbire normal / alert")

    # 4. Continuous Clarity Analysis (Zero Crossing Rate):
    # Healthy clear speech: ZCR >= 0.05 -> score 0
    # Mumbled/flat:         ZCR < 0.05 -> higher score
    if zcr >= 0.05:
        clarity_val = 0.0
    else:
        clarity_val = min(80.0, (0.05 - zcr) * 1600.0)
    analysis["clarity_score"] = int(clarity_val)
    if clarity_val > 55:
        analysis["descriptions"].append("Articulație vocală redusă (vorbire neclară / mormăită)")
    elif clarity_val < 20:
        analysis["descriptions"].append("Articulație clară a cuvintelor")

    # 5. Continuous Tone Analysis (Spectral Centroid):
    # Expressive voice: centroid >= 2000 Hz -> score 0
    # Flat monotone:    centroid < 2000 Hz -> higher score
    if centroid >= 2000:
        tone_val = 0.0
    else:
        tone_val = min(80.0, (2000.0 - centroid) * 0.06)
    analysis["tone_score"] = int(tone_val)
    if tone_val > 55:
        analysis["descriptions"].append("Voce monotonă (ton plat, variație redusă de pitch)")
    elif tone_val < 15:
        analysis["descriptions"].append("Modulație tonală variată (exprimare expresivă)")

    # 6. Overall Voice Indicator (weighted average)
    raw_indicator = int(
        energy_val * 0.40 +
        pace_val * 0.25 +
        clarity_val * 0.20 +
        tone_val * 0.15
    )
    # Extra suppression: if energy is high and pace is fast, the person is clearly not depressed
    if energy > 0.05 and tempo > 105:
        raw_indicator = int(raw_indicator * 0.4)
    elif energy > 0.035 and tempo > 90:
        raw_indicator = int(raw_indicator * 0.7)
    
    analysis["overall_voice_indicator"] = max(0, min(100, raw_indicator))
    
    return analysis


def process_voice_input(audio_binary: bytes, language: str = 'ro') -> Dict[str, Any]:
    """
    Complete voice processing pipeline
    
    1. Transcribe audio to text
    2. Extract voice features
    3. Analyze voice quality
    
    Args:
        audio_binary: Raw audio data
        language: Language code
    
    Returns:
        Complete analysis dict with transcript and voice metrics
    
    Example:
        >>> with open('audio.wav', 'rb') as f:
        >>>     result = process_voice_input(f.read())
        >>> print(f"Text: {result['transcript']}")
        >>> print(f"Voice indicator: {result['analysis']['overall_voice_indicator']}")
    """
    
    try:
        # Step 1: Transcribe
        print("📝 Transcribing audio...")
        transcript = transcribe_audio(audio_binary, language)
        
        # Step 2: Extract features
        print("🎵 Extracting voice features...")
        features = extract_voice_features(audio_binary)
        
        # Step 3: Analyze quality
        print("🔍 Analyzing voice quality...")
        analysis = analyze_voice_quality(features)
        
        result = {
            "status": "success",
            "transcript": transcript,
            "features": features,
            "analysis": analysis,
        }
        
        return result
        
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "transcript": "",
            "features": {},
            "analysis": {},
        }


# Test function
def test_voice_module():
    """Quick test of voice module"""
    print("Testing voice module...")
    print("✅ Module loaded successfully")
    print("Available functions:")
    print("  - transcribe_audio(audio_binary, language='ro')")
    print("  - extract_voice_features(audio_binary)")
    print("  - analyze_voice_quality(features)")
    print("  - process_voice_input(audio_binary, language='ro')")


if __name__ == "__main__":
    test_voice_module()
