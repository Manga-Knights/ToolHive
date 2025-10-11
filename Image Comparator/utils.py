"""
Utility functions for Image Comparator
"""
import os
import re
from constants import VALID_IMAGE_EXTENSIONS


def natural_sort_key(name):
    """Generate sort key for natural sorting (handles numbers in filenames)"""
    return [int(s) if s.isdigit() else s for s in re.split(r'(\d+)', name)]


def get_sorted_image_files(folder):
    """Get sorted list of image files from folder"""
    return sorted(
        [os.path.join(folder, f) for f in os.listdir(folder) 
         if f.lower().endswith(VALID_IMAGE_EXTENSIONS)], 
        key=natural_sort_key
    )


def format_file_size(path):
    """Format file size in human-readable format"""
    try:
        size = os.path.getsize(path)
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f}{unit}"
            size /= 1024.0
        return f"{size:.1f}TB"
    except:
        return "??"


def colorize_metrics(val1, val2, higher_is_better=True):
    """Return colors for metric comparison"""
    from constants import COLOR_BETTER, COLOR_WORSE, COLOR_NEUTRAL
    
    if val1 == val2:
        return COLOR_NEUTRAL, COLOR_NEUTRAL
    if (val1 > val2 and higher_is_better) or (val1 < val2 and not higher_is_better):
        return COLOR_BETTER, COLOR_WORSE
    else:
        return COLOR_WORSE, COLOR_BETTER