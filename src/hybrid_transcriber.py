"""
Hybrid Transcriber - Combines mgr1 (fast) + traditional clustering (accurate).
"""

import numpy as np
import json
import csv
import time

from .audio_processor import AudioProcessor
from .mgr1 import mgr1


class HybridTranscriber:
    """Semi-automatic speech transcription using hybrid approach."""
    
    def __init__(
        self,
        audio_path=None,
        segment_ms=25.0,
        hop_ms=12.5,
        mgr1_sensi=0,
        traditional_threshold=0.85,
        max_clusters=200,
    ):
        """
        Initialize transcriber.
        
        Args:
            audio_path: Path to audio file
            segment_ms: Segment length in milliseconds
            hop_ms: Hop length in milliseconds
            mgr1_sensi: Sensitivity for mgr1 (0 = exact match)
            traditional_threshold: Similarity threshold for traditional clustering
            max_clusters: Maximum clusters for traditional clustering
        """
        self.audio_path = audio_path
        self.segment_ms = segment_ms
        self.hop_ms = hop_ms
        self.mgr1_sensi = mgr1_sensi
        self.traditional_threshold = traditional_threshold
        self.max_clusters = max_clusters
        
        # Initialize components
        self.audio_processor = AudioProcessor()
        
        # Data
        self.audio = None
        self.sample_rate = None
        self.segments = []
        self.clusters = []
        self.labels = {}
        self.text_result = []
    
    def load_audio(self):
        """Load audio file."""
        if self.audio_path is None:
            raise ValueError("No audio path specified")
        
        self.sample_rate, self.audio = self.audio_processor.load(self.audio_path)
    
    def extract_segments(self):
        """Extract audio segments."""
        if self.audio is None:
            raise ValueError("No audio loaded")
        
        self.segments = self.audio_processor.extract_segments(
            self.audio,
            self.sample_rate,
            self.segment_ms,
            self.hop_ms,
        )
    
    def transcribe(self):
        """Run full hybrid transcription pipeline."""
        start_time = time.time()
        
        # ========== Load Audio ==========
        print("Loading audio...")
        self.load_audio()
        print(f"Loaded {len(self.audio)/self.sample_rate:.2f}s audio")
        
        # ========== Extract Segments ==========
        print("Extracting segments...")
        self.extract_segments()
        print(f"Extracted {len(self.segments)} segments")
        
        # ========== Phase 1: Fast Filtering with mgr1 ==========
        print("\n" + "="*60)
        print("=== Phase 1: Fast Filtering (mgr1, sensi=0) ===")
        print("="*60)
        phase1_start = time.time()
        
        clusters_fast = []
        cluster_id = 0
        
        # Sort segments by energy (helps find good templates)
        def get_energy(seg):
            return np.sum(seg['data'] ** 2)
        
        segments_sorted = sorted(self.segments, key=get_energy, reverse=True)
        
        for template_seg in segments_sorted:
            if template_seg['labeled']:
                continue
            
            # Get template
            template = template_seg['data']
            
            # Search for matches using mgr1
            matches = mgr1(template, self.audio, self.mgr1_sensi)
            
            # Create cluster
            cluster = {
                'id': cluster_id,
                'representative': template_seg,
                'segments': [template_seg],
                'method': 'mgr1',
            }
            
            template_seg['labeled'] = True
            template_seg['cluster_id'] = cluster_id
            
            # Find matching segments
            for match_pos in matches:
                for seg in self.segments:
                    if not seg['labeled'] and abs(seg['start'] - match_pos) < self.hop_ms * self.sample_rate / 1000:
                        seg['labeled'] = True
                        seg['cluster_id'] = cluster_id
                        cluster['segments'].append(seg)
            
            if len(cluster['segments']) > 1:  # Only keep clusters with multiple segments
                clusters_fast.append(cluster)
                cluster_id += 1
                
                if len(clusters_fast) % 50 == 0:
                    print(f"  Created {len(clusters_fast)} fast clusters...")
        
        phase1_time = time.time() - phase1_start
        segments_labeled_p1 = sum(1 for s in self.segments if s['labeled'])
        
        print(f"\nPhase 1 Results:")
        print(f"  Time: {phase1_time:.2f}s")
        print(f"  Clusters: {len(clusters_fast)}")
        print(f"  Segments labeled: {segments_labeled_p1}/{len(self.segments)} ({segments_labeled_p1/len(self.segments)*100:.1f}%)")
        
        # ========== Phase 2: Traditional Clustering for Remaining ==========
        print("\n" + "="*60)
        print("=== Phase 2: Traditional Clustering (Remaining) ===")
        print("="*60)
        phase2_start = time.time()
        
        # Get unlabeled segments
        unlabeled_segments = [s for s in self.segments if not s['labeled']]
        print(f"Remaining segments: {len(unlabeled_segments)}")
        
        clusters_traditional = []
        
        if len(unlabeled_segments) > 0:
            clusters_traditional = self._cluster_traditional(
                unlabeled_segments,
                self.traditional_threshold,
                self.max_clusters,
            )
            
            # Assign cluster IDs
            for cluster in clusters_traditional:
                cluster['id'] = cluster_id
                cluster['method'] = 'traditional'
                
                for seg in cluster['segments']:
                    # Find original segment
                    for orig_seg in self.segments:
                        if orig_seg['start'] == seg['start']:
                            orig_seg['labeled'] = True
                            orig_seg['cluster_id'] = cluster_id
                            break
                
                cluster_id += 1
            
            print(f"  Created {len(clusters_traditional)} traditional clusters")
        else:
            print("  No remaining segments!")
        
        phase2_time = time.time() - phase2_start
        
        # ========== Merge Results ==========
        print("\n" + "="*60)
        print("=== Merging Results ===")
        print("="*60)
        
        self.clusters = clusters_fast + clusters_traditional
        
        # Sort by size
        self.clusters.sort(key=lambda c: len(c['segments']), reverse=True)
        
        # Renumber
        for i, cluster in enumerate(self.clusters):
            cluster['id'] = i
        
        total_time = time.time() - start_time
        segments_labeled = sum(1 for s in self.segments if s['labeled'])
        
        print(f"\nFinal Results:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Phase 1 (mgr1): {phase1_time:.2f}s ({phase1_time/total_time*100:.1f}%)")
        print(f"  Phase 2 (traditional): {phase2_time:.2f}s ({phase2_time/total_time*100:.1f}%)")
        print(f"  Total clusters: {len(self.clusters)}")
        print(f"  Segments labeled: {segments_labeled}/{len(self.segments)} ({segments_labeled/len(self.segments)*100:.1f}%)")
        print(f"  Fast clusters: {len(clusters_fast)} ({sum(len(c['segments']) for c in clusters_fast)} segments)")
        print(f"  Traditional clusters: {len(clusters_traditional)} ({sum(len(c['segments']) for c in clusters_traditional)} segments)")
        print("="*60)
        
        return self.clusters
    
    def _cluster_traditional(self, segments, similarity_threshold=0.85, max_clusters=200):
        """
        Traditional clustering for remaining segments.
        """
        if not segments:
            return []
        
        clusters = []
        used = set()
        
        # Sort by energy
        def get_energy(seg):
            return np.sum(seg['data'] ** 2)
        
        segments_sorted = sorted(segments, key=get_energy, reverse=True)
        
        for i, seg in enumerate(segments_sorted):
            if i in used:
                continue
            
            # Load segment data
            seg_data = seg['data']
            
            # Find similar segments
            cluster_segments = []
            
            for j, other in enumerate(segments_sorted):
                if j in used or j == i:
                    continue
                
                # Compare
                other_data = other['data']
                
                # Normalize
                a = seg_data - np.mean(seg_data)
                b = other_data - np.mean(other_data)
                
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                
                if norm_a == 0 or norm_b == 0:
                    continue
                
                a = a / norm_a
                b = b / norm_b
                
                similarity = np.dot(a, b)
                
                if similarity >= similarity_threshold:
                    cluster_segments.append(other)
                    used.add(j)
            
            # Add cluster
            if cluster_segments:
                cluster_segments.append(seg)
                used.add(i)
                
                clusters.append({
                    'id': len(clusters),
                    'segments': cluster_segments,
                    'representative': seg,
                    'count': len(cluster_segments),
                })
                
                # Stop if enough clusters
                if len(clusters) >= max_clusters:
                    break
        
        # Sort by size
        clusters.sort(key=lambda c: c['count'], reverse=True)
        
        return clusters
    
    def save_clusters_for_review(self, output_path='clusters.json'):
        """Save clusters to JSON file."""
        clusters_lite = []
        
        for cluster in self.clusters:
            cluster_lite = {
                'id': cluster['id'],
                'count': len(cluster['segments']),
                'method': cluster.get('method', 'unknown'),
                'representative': {
                    'start_seconds': cluster['representative']['start_seconds'],
                    'end_seconds': cluster['representative']['end_seconds'],
                },
                'segments': [
                    {
                        'start_seconds': seg['start_seconds'],
                        'end_seconds': seg['end_seconds'],
                    }
                    for seg in cluster['segments'][:10]  # Limit to 10
                ]
            }
            clusters_lite.append(cluster_lite)
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(clusters_lite, f, indent=2, ensure_ascii=False)
        
        print(f"Saved clusters to {output_path}")
    
    def create_labels_template(self, output_path='manual_labels.csv'):
        
        """Create CSV template for manual labeling with default Arabic letters."""

        # Default Arabic letters order (ascending by frequency)
        DEFAULT_ARABIC_LETTERS = "_النميهربتكعفقسدذحجخشصضزثطغظكديفلت"

        with open(output_path, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                'cluster_id', 'character', 'count',
                'first_occurrence_seconds', 'method', 'notes'
            ])
            
            for i, cluster in enumerate(self.clusters):
                cluster_id = cluster['id']
                count = len(cluster['segments'])
                first_occ = cluster['representative']['start_seconds']
                method = cluster.get('method', 'unknown')
                
                # Assign default letter if within range
                if i < len(DEFAULT_ARABIC_LETTERS):
                    default_char = DEFAULT_ARABIC_LETTERS[i]
                else:
                    default_char = ''  # No default for clusters beyond 32
                
                writer.writerow([
                    cluster_id,
                    default_char,  # Pre-filled with default letter
                    count,
                    f'{first_occ:.2f}',
                    method,
                    ''
                ])

        print(f"Created labels template: {output_path}")
        print(f"  Pre-filled {sum(1 for c in self.clusters if c['id'] < 32)} clusters with default Arabic letters")
    
    def load_manual_labels(self, labels_path='manual_labels.csv'):
        """Load manual labels from CSV."""
        self.labels = {}
        
        with open(labels_path, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                cluster_id = int(row['cluster_id'])
                character = row['character'].strip()
                if character:
                    self.labels[cluster_id] = character
        
        print(f"Loaded {len(self.labels)} labels")
    
    def generate_text(self):
        """Generate text from labels."""
        if not self.clusters:
            raise ValueError("No clusters available")
        
        if not self.labels:
            raise ValueError("No labels loaded")
        
        # Create label lookup
        segment_labels = {}
        for cluster in self.clusters:
            cluster_id = cluster['id']
            if cluster_id in self.labels:
                character = self.labels[cluster_id]
                for seg in cluster['segments']:
                    segment_labels[seg['index']] = character
        
        # Generate text
        self.text_result = []
        for seg in self.segments:
            if seg['index'] in segment_labels:
                self.text_result.append({
                    'index': seg['index'],
                    'character': segment_labels[seg['index']],
                    'start': seg['start'],
                    'end': seg['end'],
                    'start_seconds': seg['start_seconds'],
                    'end_seconds': seg['end_seconds'],
                })
        
        # Sort by start position
        self.text_result.sort(key=lambda x: x['start'])
        
        print(f"Generated {len(self.text_result)} text segments")
    
    def save_text(
        self,
        output_txt='output_text.txt',
        output_csv='output_text_details.csv',
        output_srt='output_subtitles.srt',
    ):
        """Save transcription results."""
        if not self.text_result:
            raise ValueError("No text generated")
        
        # Save text
        with open(output_txt, 'w', encoding='utf-8-sig') as f:
            for item in self.text_result:
                f.write(item['character'])
        
        # Save details
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow([
                'character', 'start', 'end',
                'start_seconds', 'end_seconds'
            ])
            
            for item in self.text_result:
                writer.writerow([
                    item['character'],
                    item['start'],
                    item['end'],
                    f"{item['start_seconds']:.3f}",
                    f"{item['end_seconds']:.3f}",
                ])
        
        # Save SRT
        with open(output_srt, 'w', encoding='utf-8-sig') as f:
            for i, item in enumerate(self.text_result):
                f.write(f"{i+1}\n")
                f.write(f"{self._seconds_to_srt(item['start_seconds'])} --> ")
                f.write(f"{self._seconds_to_srt(item['end_seconds'])}\n")
                f.write(f"{item['character']}\n\n")
        
        print(f"Saved results to:\n  - {output_txt}\n  - {output_csv}\n  - {output_srt}")
    
    def _seconds_to_srt(self, seconds):
        """Convert seconds to SRT time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"
