import sys
import os
from pathlib import Path

def discover_imperial_anchor(anchor_names=[".eden", "MONEWMENT-0", "dna.lock"]):
    """
    Dynamically finds the Imperial Core directory by searching upwards.
    Ensures that the core is added to sys.path for DNA Autonomy.
    """
    current_path = Path(__file__).resolve().parent
    
    # Search up to 10 levels deep
    for _ in range(10):
        for anchor in anchor_names:
            if (current_path / anchor).exists():
                # Found the anchor. Ensure this directory is in sys.path
                anchor_dir = str(current_path)
                if anchor_dir not in sys.path:
                    sys.path.insert(0, anchor_dir)
                return current_path
        
        # Move up to the parent directory
        parent = current_path.parent
        if parent == current_path: # Reached the root
            break
        current_path = parent
        
    return None

def sanitize_and_inject_path():
    """Removes rigid sys.path entries and injects the discovered anchor."""
    anchor = discover_imperial_anchor()
    if anchor:
        return anchor
    else:
        # Fallback to current directory
        # print("!!! WARNING: Imperial DNA Anchor not found. !!!")
        return Path.cwd()
