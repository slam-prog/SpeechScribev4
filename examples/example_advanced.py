#!/usr/bin/env python3
"""
SpeechScribe V4 - Advanced Example.

Authors: NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL
AI Assistant: Perplexity AI

Usage:
    python example_advanced.py
"""

from src import SpeechTranscriberV4, AudioProcessor, ClustererV4
import numpy as np


def example_custom_settings():
    """Example with custom settings."""
    print("="*60)
    print("Example 1: Custom Settings")
    print("="*60)
    
    transcriber = SpeechTranscriberV4(
        audio_path='audio.mp3',
        segment_ms=30.0,      # 30ms segments
        threshold=0.80,       # Lower threshold
        max_clusters=300,     # More clusters
    )
    
    transcriber.transcribe()
    transcriber.save_clusters_for_review()
    transcriber.create_labels_template()


def example_multiple_formats():
    """Example with different audio formats."""
    print("\n" + "="*60)
    print("Example 2: Multiple Formats")
    print("="*60)
    
    processor = AudioProcessor()
    
    # Test different formats
    formats = ['audio.wav', 'audio.mp3', 'audio.flac', 'audio.m4a']
    
    for fmt in formats:
        try:
            sample_rate, audio = processor.load(fmt)
            print(f"✅ {fmt}: {len(audio)/sample_rate:.2f}s")
        except FileNotFoundError:
            print(f"⚠️ {fmt}: Not found")


def example_programmatic():
    """Example with programmatic control."""
    print("\n" + "="*60)
    print("Example 3: Programmatic Control")
    print("="*60)
    
    # Load audio
    processor = AudioProcessor()
    sample_rate, audio = processor.load('audio.wav')
    
    # Extract segments
    segments = processor.extract_segments(audio, sample_rate, segment_ms=25.0)
    print(f"Extracted {len(segments)} segments")
    
    # Cluster
    clusterer = ClustererV4()
    clusters = clusterer.transcribe(audio, sample_rate, segment_ms=25.0)
    print(f"Created {len(clusters)} clusters")


def example_full_pipeline():
    """Example with full pipeline."""
    print("\n" + "="*60)
    print("Example 4: Full Pipeline")
    print("="*60)
    
    transcriber = SpeechTranscriberV4(audio_path='audio.wav')
    
    # Step 1: Transcribe
    transcriber.transcribe()
    
    # Step 2: Save for review
    transcriber.save_clusters_for_review()
    transcriber.create_labels_template()
    
    # Step 3: Load labels (after manual labeling)
    # transcriber.load_manual_labels()
    
    # Step 4: Generate text
    # transcriber.generate_text()
    
    # Step 5: Save results
    # transcriber.save_text()


def main():
    """Run all examples."""
    print("\n🎙️ SpeechScribe V4 - Advanced Examples\n")
    
    # Run examples
    example_custom_settings()
    example_multiple_formats()
    example_programmatic()
    example_full_pipeline()
    
    print("\n" + "="*60)
    print("✅ All examples complete!")
    print("="*60)


if __name__ == "__main__":
    main()