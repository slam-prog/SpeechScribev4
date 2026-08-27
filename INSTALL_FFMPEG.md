# 📦 Installing FFmpeg

FFmpeg is required for full audio format support (MP3, FLAC, M4A, etc.)

## Ubuntu/Debian

```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

## macOS

```bash
brew install ffmpeg
```

## Windows

### Method 1: Chocolatey

```bash
choco install ffmpeg
```

### Method 2: Manual

1. Download from: https://ffmpeg.org/download.html
2. Extract to `C:\ffmpeg`
3. Add `C:\ffmpeg\bin` to PATH
4. Restart computer

## Verify Installation

```bash
ffmpeg -version
```

If version info appears, installation is successful! ✅

## Without FFmpeg

SpeechScribe will work with WAV files only.

---

**Authors:** NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL  
**AI Assistant:** AI Assistant: Perplexity AI