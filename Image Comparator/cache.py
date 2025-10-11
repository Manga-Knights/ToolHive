"""
Image and metrics cache management with distance-based eviction
"""
from constants import MAX_CACHE_DISTANCE


class ImageCache:
    """Cache for loaded images and metrics with distance-based eviction"""
    
    def __init__(self):
        self.thumbnails = {}  # index -> {'left': pixmap, 'right': pixmap}
        self.full_images = {}  # index -> {'left': pixmap, 'right': pixmap}
        self.metrics = {}      # index -> metrics dict (never evicted)
    
    def has_thumbnail(self, index):
        return index in self.thumbnails and \
               'left' in self.thumbnails[index] and \
               'right' in self.thumbnails[index]
    
    def has_full_image(self, index):
        return index in self.full_images and \
               'left' in self.full_images[index] and \
               'right' in self.full_images[index]
    
    def has_metrics(self, index):
        return index in self.metrics
    
    def set_image(self, index, side, pixmap, quality):
        if quality == 'thumbnail':
            if index not in self.thumbnails:
                self.thumbnails[index] = {}
            self.thumbnails[index][side] = pixmap
        else:  # full
            if index not in self.full_images:
                self.full_images[index] = {}
            self.full_images[index][side] = pixmap
    
    def get_image(self, index, side, prefer_full=True):
        """Get best available image"""
        if prefer_full and self.has_full_image(index):
            return self.full_images[index].get(side)
        elif index in self.thumbnails:
            return self.thumbnails[index].get(side)
        return None
    
    def set_metrics(self, index, metrics):
        """Metrics are never evicted - they're just text/numbers"""
        self.metrics[index] = metrics
    
    def get_metrics(self, index):
        return self.metrics.get(index)
    
    def evict_distant(self, current_index, max_distance=MAX_CACHE_DISTANCE):
        """Evict images too far from current position (keep metrics)"""
        # Evict full images
        indices_to_remove = [
            idx for idx in self.full_images.keys()
            if abs(idx - current_index) > max_distance
        ]
        for idx in indices_to_remove:
            del self.full_images[idx]
        
        # Evict thumbnails
        indices_to_remove = [
            idx for idx in self.thumbnails.keys()
            if abs(idx - current_index) > max_distance
        ]
        for idx in indices_to_remove:
            del self.thumbnails[idx]
        
        return len(indices_to_remove)
    
    def get_cache_stats(self):
        """Return cache statistics"""
        return {
            'thumbnails': len(self.thumbnails),
            'full_images': len(self.full_images),
            'metrics': len(self.metrics)
        }
    
    def clear(self):
        self.thumbnails.clear()
        self.full_images.clear()
        self.metrics.clear()