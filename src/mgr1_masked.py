"""
mgr1_masked - Fast matching with sample masking.
"""

import numpy as np


def mgr1_masked(x, y, mask, sensi=0):
    """
    Match x in y, but only at unmasked positions.
    
    Args:
        x: Pattern signal
        y: Target signal
        mask: Boolean array (True = available, False = masked)
        sensi: Sensitivity
    
    Returns:
        list: Positions where x matches y
    """
    x1 = np.sign(x)
    y1 = np.sign(y)
    
    len_x = len(x1)
    len_y = len(y1)
    
    # Find available positions
    available = np.where(mask[:len_y-len_x+1])[0]
    
    if len(available) == 0:
        return []
    
    # Create sliding windows
    from numpy.lib.stride_tricks import sliding_window_view
    y_windows = sliding_window_view(y1, len_x)
    
    # Calculate scores only at available positions
    scores = np.full(len_y - len_x + 1, -np.inf)
    
    for pos in available:
        scores[pos] = np.sum(x1 * y_windows[pos])
    
    # Find best match among available
    best_score = np.max(scores)
    
    # Find matches
    threshold = best_score - sensi
    matches = np.where(scores >= threshold)[0]
    
    # Subsample
    matches = matches[::4]
    
    return matches.tolist()


def create_mask(length):
    """Create all-True mask."""
    return np.ones(length, dtype=bool)


def mask_region(mask, start, length):
    """Mask a region in the mask."""
    end = min(start + length, len(mask))
    mask[start:end] = False