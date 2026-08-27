# 📖 SpeechScribe V4 - Usage Guide

**Authors:** NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL  
**AI Assistant:** Perplexity AI

---

## 🎯 Quick Start

### Method 1: GUI (Recommended for Beginners)

```bash
python run_gui.py
```

**Steps:**
1. Click "📂 Open Audio" to load audio file
2. Click "▶️ Transcribe" to start transcription
3. Listen to clusters using "🔊 Play" button
4. Type characters in the "Character" column
5. Click "✨ Generate Text" to export

### Method 2: CLI (For Professionals)

```bash
python run_cli.py audio.mp3
```

**Options:**
```bash
# Custom segment size
python run_cli.py audio.mp3 --segment-ms 30

# Adjust similarity threshold
python run_cli.py audio.mp3 --threshold 0.8

# Set max clusters
python run_cli.py audio.mp3 --max-clusters 300

# Custom output prefix
python run_cli.py audio.mp3 --output my_transcription
```

### Method 3: Python API (For Developers)

```python
from src import SpeechTranscriberV4

# Create transcriber
transcriber = SpeechTranscriberV4(
    audio_path='audio.mp3',
    segment_ms=25.0,
    threshold=0.85,
    max_clusters=200,
)

# Run transcription
transcriber.transcribe()

# Save results
transcriber.save_clusters_for_review()
transcriber.create_labels_template()

# After manual labeling
transcriber.load_manual_labels()
transcriber.generate_text()
transcriber.save_text()
```

---

## 📦 Supported Audio Formats

### With pydub + FFmpeg:
- ✅ WAV (always supported)
- ✅ MP3
- ✅ FLAC
- ✅ M4A
- ✅ OGG
- ✅ AAC
- ✅ WMA
- ✅ AIFF/AIF
- ✅ OPUS

### Without pydub:
- ✅ WAV only

---

## ⚙️ Configuration Options

### Segment Size (`segment_ms`)

| Value | Use Case |
|-------|----------|
| 10-15ms | Very fast speech |
| 20-30ms | Normal speech (recommended) |
| 40-50ms | Slow speech |
| 100-2000ms | Special applications |

### Similarity Threshold (`threshold`)

| Value | Effect |
|-------|--------|
| 0.70-0.80 | More matches (less precise) |
| 0.85-0.90 | Balanced (recommended) |
| 0.91-0.95 | Fewer matches (more precise) |

### Max Clusters (`max_clusters`)

| Value | Use Case |
|-------|----------|
| 100-200 | Short audio (< 10 min) |
| 200-500 | Medium audio (10-60 min) |
| 500+ | Long audio (> 1 hour) |

---

## 📝 Output Files

### 1. `clusters.json`
Cluster information for review.

```json
{
  "id": 0,
  "count": 150,
  "representative": {
    "start_seconds": 0.00,
    "end_seconds": 0.025
  },
  "segments": [...]
}
```

### 2. `manual_labels.csv`
Template for manual labeling.

```csv
cluster_id,character,count,first_occurrence_seconds,notes
0,,150,0.00,
1,,120,0.03,
```

### 3. `output_text.txt`
Plain text transcription.

### 4. `output_text_details.csv`
Detailed transcription with timestamps.

```csv
character,start,end,start_seconds,end_seconds
ه,0,1102,0.000,0.025
ذ,551,1653,0.012,0.037
```

### 5. `output_subtitles.srt`
Subtitle file for videos.

```srt
1
00:00:00,000 --> 00:00:00,025
ه

2
00:00:00,012 --> 00:00:00,037
ذ
```

---

## 🎯 Best Practices

### 1. Audio Quality
- Use high-quality recordings
- Minimize background noise
- Ensure proper volume levels

### 2. Settings
- Start with default settings (25ms, 0.85 threshold)
- Adjust based on results
- Test with short audio first

### 3. Labeling
- Listen carefully to each cluster
- Use consistent characters
- Review final text

### 4. Performance
- Close other applications
- Use SSD for faster I/O
- Increase RAM for large files

---

## 🐛 Troubleshooting

### Issue: "Only WAV files supported"
**Solution:** Install pydub and FFmpeg
```bash
pip install pydub
sudo apt-get install ffmpeg  # Ubuntu
brew install ffmpeg  # macOS
choco install ffmpeg  # Windows
```

### Issue: "PyQt5 not installed"
**Solution:** Install PyQt5
```bash
pip install PyQt5
```

### Issue: "No module named 'src'"
**Solution:** Run from project root
```bash
cd SpeechScribe
python run_gui.py
```

### Issue: Low accuracy
**Solution:** 
1. Adjust `segment_ms` (try 20-30ms)
2. Adjust `threshold` (try 0.80-0.90)
3. Check audio quality

---

## 📧 Support

- **Email:** [walidddhony@gmail.com](mailto:walidddhony@gmail.com)
- **GitHub:** [@slam-prog](https://github.com/slam-prog)
- **Issues:** [GitHub Issues](https://github.com/slam-prog/SpeechScribe/issues)

---

**SpeechScribe V4 - A Tree of Goodness Serving Humanity** 🌳
