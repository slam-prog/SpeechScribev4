"""
Hybrid Transcriber - Masked Version (Ultra-Fast!).
"""

import numpy as np
import json
import csv
import time

from audio_processor import AudioProcessor
from mgr1_masked import mgr1_masked, create_mask, mask_region


class HybridTranscriberMasked:
    """Hybrid transcription with sample masking for speed."""
    
    def __init__(
        self,
        audio_path=None,
        segment_ms=25.0,
        hop_ms=12.5,
        mgr1_sensi=0,
        traditional_threshold=0.85,
        max_clusters=200,
    ):
        self.audio_path = audio_path
        self.segment_ms = segment_ms
        self.hop_ms = hop_ms
        self.mgr1_sensi = mgr1_sensi
        self.traditional_threshold = traditional_threshold
        self.max_clusters = max_clusters
        
        self.audio_processor = AudioProcessor()
        
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
        """Run masked hybrid transcription."""
        start_time = time.time()
        
        # ========== Load Audio ==========
        print("Loading audio...")
        self.load_audio()
        print(f"Loaded {len(self.audio)/self.sample_rate:.2f}s audio")
        
        # ========== Extract Segments ==========
        print("Extracting segments...")
        self.extract_segments()
        print(f"Extracted {len(self.segments)} segments")
        
        # ========== Phase 1: Masked Fast Filtering ==========
        print("\n" + "="*60)
        print("=== Phase 1: Masked Filtering (mgr1_masked) ===")
        print("="*60)
        phase1_start = time.time()
        
        # Create mask (all available initially)
        mask = create_mask(len(self.audio))
        
        clusters_fast = []
        cluster_id = 0
        
        # Sort segments by energy
        def get_energy(seg):
            return np.sum(seg['data'] ** 2)
        
        segments_sorted = sorted(self.segments, key=get_energy, reverse=True)
        
        for template_seg in segments_sorted:
            if template_seg['labeled']:
                continue
            
            # Get template
            template = template_seg['data']
            len_template = len(template)
            
            # Match with masked audio (only available positions!)
            matches = mgr1_masked(template, self.audio, mask, self.mgr1_sensi)
            
            if not matches:
                continue
            
            # Create cluster
            cluster = {
                'id': cluster_id,
                'representative': template_seg,
                'segments': [template_seg],
                'method': 'mgr1_masked',
            }
            
            template_seg['labeled'] = True
            template_seg['cluster_id'] = cluster_id
            
            # Find matching segments and mask regions
            hop_samples = int(self.hop_ms * self.sample_rate / 1000)
            masked_count = 0
            
            for match_pos in matches:
                # Mask this region
                mask_region(mask, match_pos, len_template)
                masked_count += len_template
                
                # Find segments near this match
                for seg in self.segments:
                    if seg['labeled']:
                        continue
                    
                    if abs(seg['start'] - match_pos) < hop_samples:
                        seg['labeled'] = True
                        seg['cluster_id'] = cluster_id
                        cluster['segments'].append(seg)
            
            if len(cluster['segments']) > 1:
                clusters_fast.append(cluster)
                cluster_id += 1
                
                # Progress info
                available_pct = np.sum(mask) / len(mask) * 100
                if len(clusters_fast) % 50 == 0:
                    print(f"  Created {len(clusters_fast)} clusters | "
                          f"Masked: {100-available_pct:.1f}% | "
                          f"Remaining: {available_pct:.1f}%")
                
                # Stop if most audio is masked
                if available_pct < 5:
                    print(f"  Stopping: Only {available_pct:.1f}% of audio remaining")
                    break
                
                # Stop if enough clusters
                if len(clusters_fast) >= self.max_clusters:
                    break
        
        phase1_time = time.time() - phase1_start
        segments_labeled_p1 = sum(1 for s in self.segments if s['labeled'])
        available_samples = np.sum(mask)
        
        print(f"\nPhase 1 Results:")
        print(f"  Time: {phase1_time:.2f}s")
        print(f"  Clusters: {len(clusters_fast)}")
        print(f"  Segments labeled: {segments_labeled_p1}/{len(self.segments)} ({segments_labeled_p1/len(self.segments)*100:.1f}%)")
        print(f"  Audio masked: {100-available_samples/len(mask)*100:.1f}%")
        
        # ========== Phase 2: Traditional Clustering ==========
        print("\n" + "="*60)
        print("=== Phase 2: Traditional Clustering (Remaining) ===")
        print("="*60)
        phase2_start = time.time()
        
        unlabeled_segments = [s for s in self.segments if not s['labeled']]
        print(f"Remaining segments: {len(unlabeled_segments)}")
        
        clusters_traditional = []
        
        if len(unlabeled_segments) > 0:
            clusters_traditional = self._cluster_traditional(
                unlabeled_segments,
                self.traditional_threshold,
                min(50, self.max_clusters),
            )
            
            for cluster in clusters_traditional:
                cluster['id'] = cluster_id
                cluster['method'] = 'traditional'
                
                for seg in cluster['segments']:
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
        self.clusters.sort(key=lambda c: len(c['segments']), reverse=True)
        
        for i, cluster in enumerate(self.clusters):
            cluster['id'] = i
        
        total_time = time.time() - start_time
        segments_labeled = sum(1 for s in self.segments if s['labeled'])
        
        print(f"\nFinal Results:")
        print(f"  Total time: {total_time:.2f}s")
        print(f"  Phase 1 (masked): {phase1_time:.2f}s ({phase1_time/total_time*100:.1f}%)")
        print(f"  Phase 2 (traditional): {phase2_time:.2f}s ({phase2_time/total_time*100:.1f}%)")
        print(f"  Total clusters: {len(self.clusters)}")
        print(f"  Segments labeled: {segments_labeled}/{len(self.segments)} ({segments_labeled/len(self.segments)*100:.1f}%)")
        print(f"  Speedup: ~{100*phase1_time/(phase1_time+phase2_time):.0f}x faster than traditional")
        print("="*60)
        
        return self.clusters
    
    def _cluster_traditional(self, segments, similarity_threshold=0.85, max_clusters=50):
        """Traditional clustering for remaining segments."""
        if not segments:
            return []
        
        clusters = []
        used = set()
        
        def get_energy(seg):
            return np.sum(seg['data'] ** 2)
        
        segments_sorted = sorted(segments, key=get_energy, reverse=True)
        
        for i, seg in enumerate(segments_sorted):
            if i in used:
                continue
            
            seg_data = seg['data']
            cluster_segments = [seg]
            used.add(i)
            
            for j, other in enumerate(segments_sorted):
                if j in used:
                    continue
                
                other_data = other['data']
                
                a = seg_data - np.mean(seg_data)
                b = other_data - np.mean(other_data)
                
                norm_a = np.linalg.norm(a)
                norm_b = np.linalg.norm(b)
                
                if norm_a == 0 or norm_b == 0:
                    continue
                
                similarity = np.dot(a / norm_a, b / norm_b)
                
                if similarity >= similarity_threshold:
                    cluster_segments.append(other)
                    used.add(j)
            
            if len(cluster_segments) > 1:
                clusters.append({
                    'id': len(clusters),
                    'segments': cluster_segments,
                    'representative': seg,
                    'count': len(cluster_segments),
                })
                
                if len(clusters) >= max_clusters:
                    break
        
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
                    for seg in cluster['segments'][:10]
                ]
            }
            clusters_lite.append(cluster_lite)
        
        with open(output_path, 'w', encoding='utf-8-sig') as f:
            json.dump(clusters_lite, f, indent=2, ensure_ascii=False)
        
        print(f"Saved clusters to {output_path}")
    
    def create_labels_template(self, output_path='manual_labels.csv'):
        """Create CSV template with default Arabic letters."""
        DEFAULT_ARABIC_LETTERS = "النميهربتكعفقسدذحجخشصضزثطغظكديفلت"
        
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
                
                if i < len(DEFAULT_ARABIC_LETTERS):
                    default_char = DEFAULT_ARABIC_LETTERS[i]
                else:
                    default_char = ''
                
                writer.writerow([
                    cluster_id,
                    default_char,
                    count,
                    f'{first_occ:.2f}',
                    method,
                    ''
                ])
        
        print(f"Created labels template: {output_path}")
    
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
        
        segment_labels = {}
        for cluster in self.clusters:
            cluster_id = cluster['id']
            if cluster_id in self.labels:
                character = self.labels[cluster_id]
                for seg in cluster['segments']:
                    segment_labels[seg['index']] = character
        
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
        
        self.text_result.sort(key=lambda x: x['start'])
        print(f"Generated {len(self.text_result)} text segments")
    
    def save_text(self, output_txt='output_text.txt', output_csv='output_text_details.csv', output_srt='output_subtitles.srt'):
        """Save transcription results."""
        if not self.text_result:
            raise ValueError("No text generated")
        
        with open(output_txt, 'w', encoding='utf-8-sig') as f:
            for item in self.text_result:
                f.write(item['character'])
        
        with open(output_csv, 'w', newline='', encoding='utf-8-sig') as f:
            writer = csv.writer(f)
            writer.writerow(['character', 'start', 'end', 'start_seconds', 'end_seconds'])
            
            for item in self.text_result:
                writer.writerow([
                    item['character'],
                    item['start'],
                    item['end'],
                    f"{item['start_seconds']:.3f}",
                    f"{item['end_seconds']:.3f}",
                ])
        
        with open(output_srt, 'w', encoding='utf-8-sig') as f:
            for i, item in enumerate(self.text_result):
                f.write(f"{i+1}\n")
                f.write(f"{self._seconds_to_srt(item['start_seconds'])} --> {self._seconds_to_srt(item['end_seconds'])}\n")
                f.write(f"{item['character']}\n\n")
        
        print(f"Saved results to:\n  - {output_txt}\n  - {output_csv}\n  - {output_srt}")
    
    def _seconds_to_srt(self, seconds):
        """Convert seconds to SRT time format."""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = int(seconds % 60)
        millis = int((seconds % 1) * 1000)
        return f"{hours:02d}:{minutes:02d}:{secs:02d},{millis:03d}"