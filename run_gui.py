#!/usr/bin/env python3
"""
SpeechScribe V4 - GUI Launcher.

Authors: NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL
AI Assistant: Perplexity AI

Usage:
    python run_gui.py
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

try:
    from PyQt5.QtWidgets import QApplication
    from gui.main_window import SpeechScribeMainWindow  # ← تأكد من هذا السطر
    
    def main():
        """Main entry point for GUI."""
        app = QApplication(sys.argv)
        app.setStyle('Fusion')
        
        # Set application info
        app.setApplicationName("SpeechScribe V4")
        app.setApplicationVersion("4.0.0")
        app.setOrganizationName("SpeechScribe")
        
        # Create and show window
        window = SpeechScribeMainWindow()
        window.show()
        
        # Run event loop
        sys.exit(app.exec_())
    
    if __name__ == "__main__":
        main()
        
except ImportError as e:
    print("❌ Error: PyQt5 not installed!")
    print("   Install with: pip install PyQt5")
    print(f"   Details: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)