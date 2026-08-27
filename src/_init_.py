"""
SpeechScribe V4 - Ultra-Fast Speech Transcription.

A high-performance speech transcription system using NumPy vectorization.
Supports all languages with manual labeling.

Version: 4.0.0
Authors: 
  - NAJIB MOHAMMED AL-AMIR
  - WALID HASSAN MOHAMMAD AL-MOTAWAKIL
AI Assistant: Perplexity AI
License: HEUL-1.0 (Humanitarian & Ethical Use License)
"""

from .audio_processor import AudioProcessor
from .clusterer_v4 import ClustererV4
from .transcriber_v4 import SpeechTranscriberV4

__version__ = "4.0.0"
__author__ = "NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKIL"
__email__ = "walidddhony@gmail.com"
__license__ = "HEUL-1.0"
__AI Assistant: Perplexity AI

__all__ = [
    "AudioProcessor",
    "ClustererV4",
    "SpeechTranscriberV4",
]