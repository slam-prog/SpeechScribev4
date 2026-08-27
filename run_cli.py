#!/usr/bin/env python3
"""
SpeechScribe V4 - Command Line Interface.

Authors: NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL
AI Assistant: Perplexity AI

Usage:
    python run_cli.py <audio_file> [options]
    
Examples:
    python run_cli.py audio.wav
    python run_cli.py audio.mp3 --segment-ms 30
    python run_cli.py audio.flac --threshold 0.8
"""

import sys
import argparse
import time
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from transcriber_v4 import SpeechTranscriberV4


def main():
    """Main entry point for CLI."""
    parser = argparse.ArgumentParser(
        description='SpeechScribe V4 - Ultra-Fast Speech Transcription',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_cli.py audio.wav
  python run_cli.py audio.mp3 --segment-ms 30 --threshold 0.8
  python run_cli.py audio.flac --max-clusters 300
        """
    )
    
    parser.add_argument('audio_file', type=str, help='Path to audio file (WAV, MP3, FLAC, M4A, etc.)')
    parser.add_argument('--segment-ms', type=float, default=25.0, help='Segment length in ms (default: 25)')
    parser.add_argument('--threshold', type=float, default=0.85, help='Similarity threshold (default: 0.85)')
    parser.add_argument('--max-clusters', type=int, default=200, help='Maximum clusters (default: 200)')
    parser.add_argument('--output', type=str, default='output', help='Output prefix (default: output)')
    
    args = parser.parse_args()
    
    # Check if file exists
    audio_path = Path(args.audio_file)
    if not audio_path.exists():
        print(f"❌ Error: File '{args.audio_file}' not found!")
        sys.exit(1)
    
    print("="*60)
    print("🎙️ SpeechScribe V4 - Ultra-Fast Transcription")
    print("="*60)
    print(f"Input: {args.audio_file}")
    print(f"Segment: {args.segment_ms}ms")
    print(f"Threshold: {args.threshold}")
    print(f"Max clusters: {args.max_clusters}")
    print("="*60)
    
    start_time = time.time()
    
    try:
        # Create transcriber
        transcriber = SpeechTranscriberV4(
            audio_path=args.audio_file,
            segment_ms=args.segment_ms,
            threshold=args.threshold,
            max_clusters=args.max_clusters,
        )
        
        # Run transcription
        transcriber.transcribe()
        
        # Save clusters
        transcriber.save_clusters_for_review('clusters.json')
        transcriber.create_labels_template('manual_labels.csv')
        
        print("\n" + "="*60)
        print("✅ Phase 1 Complete!")
        print("="*60)
        print("\n📋 Next Steps:")
        print("  1. Open 'clusters.json' and listen to samples")
        print("  2. Open 'manual_labels.csv' and assign characters")
        print("  3. Save the file")
        print("  4. Run: python run_cli.py --generate")
        print("="*60)
        
        print(f"\n⏱️ Total time: {time.time() - start_time:.2f}s")
        
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()