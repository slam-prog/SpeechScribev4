"""
Unit tests for SpeechScribe V4.

Authors: NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL
AI Assistant: Perplexity AI
"""

import pytest
import numpy as np
from pathlib import Path
import sys

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from audio_processor import AudioProcessor
from clusterer_v4 import ClustererV4
from transcriber_v4 import SpeechTranscriberV4


class TestAudioProcessor:
    """Test AudioProcessor class."""
    
    def test_init(self):
        """Test initialization."""
        processor = AudioProcessor()
        assert processor is not None
    
    def test_get_supported_formats(self):
        """Test supported formats."""
        processor = AudioProcessor()
        formats = processor.get_supported_formats()
        assert '.wav' in formats


class TestClustererV4:
    """Test ClustererV4 class."""
    
    def test_init(self):
        """Test initialization."""
        clusterer = ClustererV4()
        assert clusterer is not None
        assert clusterer.segment_length == 1102
    
    def test_find_matches_fast(self):
        """Test match finding."""
        clusterer = ClustererV4()
        
        # Create test signals
        x = np.sin(np.linspace(0, 10, 100))
        y = np.concatenate([np.zeros(50), x, np.zeros(50)])
        
        # Find matches
        matches = clusterer.find_matches_fast(x, y, threshold_ratio=0.8)
        
        # Should find at least one match
        assert len(matches) > 0


class TestSpeechTranscriberV4:
    """Test SpeechTranscriberV4 class."""
    
    def test_init(self):
        """Test initialization."""
        transcriber = SpeechTranscriberV4()
        assert transcriber is not None
        assert transcriber.segment_ms == 25.0
        assert transcriber.threshold == 0.85
    
    def test_init_with_params(self):
        """Test initialization with parameters."""
        transcriber = SpeechTranscriberV4(
            audio_path='test.wav',
            segment_ms=30.0,
            threshold=0.8,
            max_clusters=300,
        )
        assert transcriber.audio_path == 'test.wav'
        assert transcriber.segment_ms == 30.0
        assert transcriber.threshold == 0.8
        assert transcriber.max_clusters == 300


if __name__ == '__main__':
    pytest.main([__file__, '-v'])