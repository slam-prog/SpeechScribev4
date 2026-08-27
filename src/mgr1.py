"""
mgr1 - Fast approximate matching function.
"""

import numpy as np


def mgr1(x, y, sensi=0):
    """
    Fast approximate matching using sign-based comparison.
    
    Args:
        x: Pattern signal (shorter)
        y: Target signal (longer)
        sensi: Sensitivity (0 = exact match, higher = more matches)
    
    Returns:
        list: Positions where x matches y
    """
    # Convert to sign (-1, 0, +1)
    x1 = np.sign(x)
    y1 = np.sign(y)
    
    # Find best match
    best_score = -np.inf
    
    for i in range(0, len(y1) - len(x1), 1):
        u = (x1 * y1[i:i+len(x1)]).sum()
        if u > best_score:
            best_score = u
    
    # Find all matches above threshold
    matches = []
    step = max(1, len(x1) // 4)
    
    for i in range(0, len(y1) - len(x1), step):
        u = (x1 * y1[i:i+len(x1)]).sum()
        if best_score - sensi <= u:
            matches.append(i)
    
    return matches