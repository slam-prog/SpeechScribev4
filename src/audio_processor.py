"""
Audio processing utilities for SpeechScribe.
Supports ALL audio formats via pydub.

Authors: NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL
AI Assistant: Perplexity AI
"""

import numpy as np
from pathlib import Path

try:
    from pydub import AudioSegment
    PYDUB_AVAILABLE = True
except ImportError:
    PYDUB_AVAILABLE = False
    from scipy.io import wavfile


class AudioProcessor:
    """
    Handle audio file operations.
    
    Supports:
    - WAV (native)
    - MP3, FLAC, M4A, OGG, AAC, WMA, AIFF (via pydub)
    - Mono and stereo conversion
    - Automatic normalization
    - DC offset removal
    
    Example:
        processor = AudioProcessor()
        sample_rate, audio = processor.load('audio.mp3')
        segments = processor.extract_segments(audio, sample_rate)
    """
    
    def __init__(self):
        """Initialize audio processor."""
        pass
    
    def load(self, path):
        """
        Load audio file and convert to mono.
        
        Args:
            path (str): Path to audio file (any format)
        
        Returns:
            tuple: (sample_rate, audio_data)
                - sample_rate (int): Sample rate in Hz
                - audio_data (np.array): Audio data as float64 [-1, 1]
        
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If file is not a valid audio file
        """
        path = Path(path)
        
        if not path.exists():
            raise FileNotFoundError(f"Audio file not found: {path}")
        
        # Get file extension
        file_ext = path.suffix.lower()
        
        # Use pydub for non-WAV formats
        if file_ext != '.wav' and PYDUB_AVAILABLE:
            return self._load_with_pydub(path)
        elif file_ext == '.wav':
            return self._load_wav(path)
        else:
            # Fallback to scipy for WAV only
            if not PYDUB_AVAILABLE:
                print("⚠️ Warning: pydub not installed. Only WAV files supported.")
                print("   Install with: pip install pydub")
                print("   Also install FFmpeg for full format support.")
            return self._load_wav(path)
    
    def _load_wav(self, path):
        """Load WAV file using scipy."""
        sample_rate, audio = wavfile.read(path)
        
        # Convert to mono if stereo
        if audio.ndim == 2:
            audio = audio.mean(axis=1)
        
        # Convert to float64
        audio = audio.astype(np.float64)
        
        # Remove DC offset
        audio -= np.mean(audio)
        
        # Normalize amplitude to [-1, 1]
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val
        
        return sample_rate, audio
    
    def _load_with_pydub(self, path):
        """Load any audio format using pydub."""
        # Load audio file
        audio_segment = AudioSegment.from_file(path)
        
        # Convert to mono
        audio_segment = audio_segment.set_channels(1)
        
        # Get sample rate
        sample_rate = audio_segment.frame_rate
        
        # Get audio data as numpy array
        audio = np.array(audio_segment.get_array_of_samples(), dtype=np.float64)
        
        # Normalize to [-1, 1]
        max_val = np.max(np.abs(audio))
        if max_val > 0:
            audio /= max_val
        
        # Remove DC offset
        audio -= np.mean(audio)
        
        return sample_rate, audio
    
    def extract_segments(self, audio, sample_rate, segment_ms=25.0, hop_ms=12.5):
        """
        Extract overlapping segments from audio.
        
        Args:
            audio (np.array): Audio data
            sample_rate (int): Sample rate in Hz
            segment_ms (float): Segment length in milliseconds
            hop_ms (float): Hop length in milliseconds
        
        Returns:
            list: List of segment dictionaries with keys:
                - index: Segment index
                - start: Start sample
                - end: End sample
                - data: Audio data
                - start_seconds: Start time in seconds
                - end_seconds: End time in seconds
        """
        segment_length = int(round(sample_rate * segment_ms / 1000.0))
        hop_length = int(round(sample_rate * hop_ms / 1000.0))
        
        segments = []
        
        for start in range(0, len(audio) - segment_length + 1, hop_length):
            end = start + segment_length
            segment = audio[start:end]
            
            segments.append({
                'index': len(segments),
                'start': start,
                'end': end - 1,
                'data': segment,
                'start_seconds': start / sample_rate,
                'end_seconds': (end - 1) / sample_rate,
            })
        
        return segments
    
    def save(self, path, sample_rate, audio):
        """
        Save audio to WAV file.
        
        Args:
            path (str): Output path
            sample_rate (int): Sample rate in Hz
            audio (np.array): Audio data
        """
        from scipy.io import wavfile
        
        # Convert to 16-bit PCM
        audio_int16 = (audio * 32767).astype(np.int16)
        
        # Save
        wavfile.write(path, sample_rate, audio_int16)
    
    def get_supported_formats(self):
        """
        Get list of supported audio formats.
        
        Returns:
            list: List of supported file extensions
        """
        formats = ['.wav']
        
        if PYDUB_AVAILABLE:
            formats.extend([
                '.mp3', '.flac', '.m4a', '.ogg', '.aac', 
                '.wma', '.aiff', '.aif', '.opus'
            ])
        
        return formats