# 📚 SpeechScribe V4 - API Reference

**Authors:** NAJIB MOHAMMED AL-AMIR & WALID HASSAN MOHAMMAD AL-MOTAWAKEL  
**AI Assistant:** Perplexity AI

---

## 📦 Module: `src`

### Classes

#### `AudioProcessor`
Handle audio file operations.

**Methods:**
- `load(path)` - Load audio file
- `extract_segments(audio, sample_rate, segment_ms, hop_ms)` - Extract segments
- `save(path, sample_rate, audio)` - Save audio to WAV
- `get_supported_formats()` - Get list of supported formats

**Example:**
```python
from src import AudioProcessor

processor = AudioProcessor()
sample_rate, audio = processor.load('audio.mp3')
segments = processor.extract_segments(audio, sample_rate)
```

---

#### `ClustererV4`
Ultra-fast clustering using NumPy vectorization.

**Methods:**
- `find_matches_fast(x, y, threshold_ratio)` - Find matches
- `transcribe(audio, sample_rate, segment_ms, threshold, max_clusters)` - Full transcription

**Example:**
```python
from src import ClustererV4

clusterer = ClustererV4()
clusters = clusterer.transcribe(audio, sample_rate, segment_ms=25.0)
```

---

#### `SpeechTranscriberV4`
Main transcription class.

**Methods:**
- `load_audio()` - Load audio file
- `transcribe()` - Run transcription
- `save_clusters_for_review(output_path)` - Save clusters to JSON
- `create_labels_template(output_path)` - Create CSV template
- `load_manual_labels(labels_path)` - Load manual labels
- `generate_text()` - Generate text from labels
- `save_text(output_txt, output_csv, output_srt)` - Save results

**Example:**
```python
from src import SpeechTranscriberV4

transcriber = SpeechTranscriberV4(audio_path='audio.mp3')
transcriber.transcribe()
transcriber.save_clusters_for_review()
transcriber.create_labels_template()
transcriber.load_manual_labels()
transcriber.generate_text()
transcriber.save_text()
```

---

## 🎨 Module: `gui`

### Classes

#### `SpeechScribeMainWindow`
Main GUI window.

**Usage:**
```python
from gui import SpeechScribeMainWindow
from PyQt5.QtWidgets import QApplication

app = QApplication([])
window = SpeechScribeMainWindow()
window.show()
app.exec_()
```

---

## 📊 Data Structures

### Cluster Dictionary
```python
{
    'id': int,                      # Cluster ID
    'representative_start': int,    # Start sample
    'representative_end': int,      # End sample
    'segments': [                   # List of segments
        {
            'start': int,           # Start sample
            'end': int,             # End sample
            'start_seconds': float, # Start time (s)
            'end_seconds': float,   # End time (s)
        }
    ],
    'matches': [int],               # Match positions
    'method': str,                  # Method used
}
```

### Segment Dictionary
```python
{
    'index': int,           # Segment index
    'start': int,           # Start sample
    'end': int,             # End sample
    'data': np.array,       # Audio data
    'start_seconds': float, # Start time (s)
    'end_seconds': float,   # End time (s)
}
```

---

## 🔧 Configuration

### SpeechTranscriberV4 Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `audio_path` | str | None | Path to audio file |
| `segment_ms` | float | 25.0 | Segment length (ms) |
| `hop_ms` | float | 12.5 | Hop length (ms) |
| `threshold` | float | 0.85 | Similarity threshold |
| `max_clusters` | int | 200 | Maximum clusters |

---

## 📝 Complete Example

```python
from src import SpeechTranscriberV4

# Initialize
transcriber = SpeechTranscriberV4(
    audio_path='audio.mp3',
    segment_ms=25.0,
    threshold=0.85,
    max_clusters=200,
)

# Transcribe
transcriber.load_audio()
transcriber.transcribe()

# Save for review
transcriber.save_clusters_for_review('clusters.json')
transcriber.create_labels_template('manual_labels.csv')

# After manual labeling
transcriber.load_manual_labels('manual_labels.csv')
transcriber.generate_text()
transcriber.save_text(
    output_txt='output.txt',
    output_csv='output.csv',
    output_srt='output.srt',
)
```

---

## 📧 Support

- **Email:** [walidddhony@gmail.com](mailto:walidddhony@gmail.com)
- **GitHub:** [@slam-prog](https://github.com/slam-prog)

---

**SpeechScribe V4 - A Tree of Goodness Serving Humanity** 🌳