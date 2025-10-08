// imageLoader.js - Hybrid lazy loading with smart memory management

export class ImageLoader {
  constructor() {
    this.allFiles = [];
    this.loadedCount = 0;
    this.batchSize = 10;
    this.fitToWidth = false;
    this.bordersOn = false;

    // Memory management
    this.maxImagesInDOM = 100;
    this.unloadThreshold = 50;
    this.loadedRanges = [];

    // Jump state management
    this.isJumping = false;
    this.jumpTargetPage = null;

    // Priority loading system
    this.loadQueue = [];
    this.isProcessingQueue = false;
    this.currentLoadController = null;

    // Performance caches
    this.imageCache = new Map();
    this.rectCache = new Map();
    this.rectCacheValid = false;
    this.currentPageCache = null;
    this.currentPageCacheTime = 0;
    this.CACHE_DURATION = 100;

    // Batch tracking
    this.pendingStyleUpdates = new Set();
    this.styleUpdateScheduled = false;
  }

  setFiles(files) {
    this.allFiles = Array.from(files)
      .sort((a, b) => a.name.localeCompare(b.name))
      .filter((f) => f.type.startsWith("image/"));
    this.loadedCount = 0;
    this.loadedRanges = [];
    this.clearCaches();
  }

  clearCaches() {
    this.imageCache.clear();
    this.rectCache.clear();
    this.rectCacheValid = false;
    this.currentPageCache = null;
  }

  invalidateRectCache() {
    this.rectCacheValid = false;
  }

  // Check if a page index is currently loaded
  isPageLoaded(pageIndex) {
    return this.imageCache.has(pageIndex);
  }

  // Get range of currently loaded pages
  getLoadedRange() {
    if (this.imageCache.size === 0) return { min: 0, max: 0 };

    const indices = Array.from(this.imageCache.keys()).sort((a, b) => a - b);
    return { min: indices[0], max: indices[indices.length - 1] };
  }

  // Unload images far from current viewport
  unloadDistantImages() {
    // Don't unload during jumps
    if (this.isJumping) return;

    const currentPage = this.getCurrentPage();
    const currentIndex = currentPage - 1;

    const imagesToUnload = [];

    this.imageCache.forEach((img, pageIndex) => {
      const distance = Math.abs(pageIndex - currentIndex);

      if (distance > this.unloadThreshold) {
        imagesToUnload.push(pageIndex);
      }
    });

    // Unload images
    imagesToUnload.forEach((pageIndex) => {
      const img = this.imageCache.get(pageIndex);
      if (img) {
        // Revoke blob URL to free memory
        if (img.src.startsWith("blob:")) {
          URL.revokeObjectURL(img.src);
        }
        img.remove();
        this.imageCache.delete(pageIndex);
        this.rectCache.delete(pageIndex);
      }
    });

    if (imagesToUnload.length > 0) {
      this.invalidateRectCache();
    }
  }

  // Load a specific batch starting at index
  loadBatch(startIndex) {
    startIndex = Math.max(0, startIndex);
    const endIndex = Math.min(
      startIndex + this.batchSize,
      this.allFiles.length
    );

    if (startIndex >= endIndex) return;

    const fragment = document.createDocumentFragment();
    const loadedIndices = [];

    for (let i = startIndex; i < endIndex; i++) {
      // Skip if already loaded
      if (this.isPageLoaded(i)) continue;

      const file = this.allFiles[i];
      const img = document.createElement("img");
      img.classList.add("manga-img");
      img.dataset.pageIndex = i;
      img.src = URL.createObjectURL(file);

      if (this.bordersOn) img.classList.add("bordered");
      if (!this.fitToWidth) img.classList.add("original-size");

      this.imageCache.set(i, img);
      loadedIndices.push(i);
      fragment.appendChild(img);
    }

    if (loadedIndices.length > 0) {
      // Insert images in correct order
      this.insertImagesInOrder(fragment, startIndex);
      this.invalidateRectCache();
    }
  }

  // Insert images at correct position in DOM to maintain order
  insertImagesInOrder(fragment, startIndex) {
    const allImages = document.querySelectorAll("img.manga-img");

    if (allImages.length === 0) {
      document.body.appendChild(fragment);
      return;
    }

    // Find insertion point
    let insertBefore = null;
    for (let img of allImages) {
      const imgIndex = parseInt(img.dataset.pageIndex);
      if (imgIndex > startIndex) {
        insertBefore = img;
        break;
      }
    }

    if (insertBefore) {
      document.body.insertBefore(fragment, insertBefore);
    } else {
      document.body.appendChild(fragment);
    }
  }

  // Load next batch (for initial loading)
  loadNextBatch() {
    const range = this.getLoadedRange();
    const nextStart = range.max > 0 ? range.max + 1 : 0;
    this.loadBatch(nextStart);

    // Check if we should unload distant images
    if (this.imageCache.size > this.maxImagesInDOM) {
      this.unloadDistantImages();
    }
  }

  // Load around a specific page (bi-directional)
  async loadAroundPage(pageIndex) {
    pageIndex = Math.max(0, Math.min(pageIndex, this.allFiles.length - 1));

    // Load current batch
    const batchStart = Math.floor(pageIndex / this.batchSize) * this.batchSize;
    this.loadBatch(batchStart);

    // Load previous batch
    if (batchStart > 0) {
      this.loadBatch(batchStart - this.batchSize);
    }

    // Load next batch
    if (batchStart + this.batchSize < this.allFiles.length) {
      this.loadBatch(batchStart + this.batchSize);
    }

    // Unload distant images
    if (this.imageCache.size > this.maxImagesInDOM) {
      this.unloadDistantImages();
    }

    await new Promise((r) => setTimeout(r, 0));
  }

  getCurrentPage() {
    // Always recalculate if we're jumping or cache is forced invalid
    const now = performance.now();

    if (
      !this.isJumping &&
      this.currentPageCache &&
      now - this.currentPageCacheTime < this.CACHE_DURATION
    ) {
      return this.currentPageCache;
    }

    const imgs = document.querySelectorAll("img.manga-img");
    if (!imgs.length) {
      this.currentPageCache = 1;
      this.currentPageCacheTime = now;
      return 1;
    }

    const viewportMiddle = window.innerHeight / 2;
    let currentPage = 1;

    for (let i = 0; i < imgs.length; i++) {
      const rect = imgs[i].getBoundingClientRect();
      const pageIndex = parseInt(imgs[i].dataset.pageIndex);

      if (rect.top <= viewportMiddle && rect.bottom >= viewportMiddle) {
        currentPage = pageIndex + 1;
        break;
      }
    }

    this.currentPageCache = currentPage;
    this.currentPageCacheTime = now;

    return currentPage;
  }

  async scrollToPage(pageNum, forceUpdate = false) {
    pageNum = Math.min(Math.max(1, pageNum), this.allFiles.length);
    const pageIndex = pageNum - 1;

    // Set jumping state
    this.isJumping = true;
    this.jumpTargetPage = pageNum;

    // Load images around target page - load MORE for big jumps
    const currentPage = this.getCurrentPage();
    const jumpDistance = Math.abs(pageNum - currentPage);

    // For big jumps, load extra batches
    const batchesToLoad = jumpDistance > 50 ? 5 : 3;

    for (let i = 0; i < batchesToLoad; i++) {
      const offset = (i - Math.floor(batchesToLoad / 2)) * this.batchSize;
      await this.loadAroundPage(pageIndex + offset);
    }

    // Wait for target image to be ready
    let targetImg = this.imageCache.get(pageIndex);
    let attempts = 0;
    const maxAttempts = 20;

    while (!targetImg && attempts < maxAttempts) {
      await new Promise((r) => setTimeout(r, 50));
      targetImg = this.imageCache.get(pageIndex);
      attempts++;
    }

    if (!targetImg) {
      console.warn(`Image ${pageNum} not found after ${attempts} attempts`);
      this.isJumping = false;
      return;
    }

    // Wait for image to load completely
    if (!targetImg.complete) {
      await new Promise((resolve) => {
        const timeout = setTimeout(resolve, 3000);
        targetImg.onload = () => {
          clearTimeout(timeout);
          resolve();
        };
        targetImg.onerror = () => {
          clearTimeout(timeout);
          resolve();
        };
      });
    }

    // Additional wait to ensure DOM is stable
    await new Promise((r) => setTimeout(r, 100));

    // Scroll to image
    targetImg.scrollIntoView({ behavior: "auto", block: "start" });

    // Force cache invalidation
    this.invalidateRectCache();
    this.currentPageCache = null;

    // Wait for scroll to settle
    await new Promise((r) => setTimeout(r, 150));

    // End jumping state
    this.isJumping = false;
    this.jumpTargetPage = null;

    // Force getCurrentPage recalculation
    this.currentPageCache = null;

    // Return the final page for UI update
    return this.getCurrentPage();
  }

  scheduleStyleUpdate(callback) {
    this.pendingStyleUpdates.add(callback);

    if (!this.styleUpdateScheduled) {
      this.styleUpdateScheduled = true;
      requestAnimationFrame(() => {
        this.pendingStyleUpdates.forEach((cb) => cb());
        this.pendingStyleUpdates.clear();
        this.styleUpdateScheduled = false;
      });
    }
  }

  async toggleFit(currentPage) {
    this.fitToWidth = !this.fitToWidth;

    this.scheduleStyleUpdate(() => {
      const imgs = document.querySelectorAll("img.manga-img");
      const className = "original-size";

      imgs.forEach((img) => {
        img.classList.toggle(className, !this.fitToWidth);
      });
    });

    await new Promise((resolve) => requestAnimationFrame(resolve));
    await this.scrollToPage(currentPage, true);

    return this.fitToWidth;
  }

  async toggleBorders(currentPage) {
    this.bordersOn = !this.bordersOn;

    this.scheduleStyleUpdate(() => {
      const imgs = document.querySelectorAll("img.manga-img");
      const className = "bordered";

      imgs.forEach((img) => {
        img.classList.toggle(className, this.bordersOn);
      });
    });

    await new Promise((resolve) => requestAnimationFrame(resolve));
    await this.scrollToPage(currentPage, true);

    return this.bordersOn;
  }

  clearImages() {
    this.imageCache.forEach((img) => {
      if (img.src.startsWith("blob:")) {
        URL.revokeObjectURL(img.src);
      }
      img.remove();
    });

    this.clearCaches();
    this.loadedRanges = [];
  }

  get totalPages() {
    return this.allFiles.length;
  }

  get hasImages() {
    return this.allFiles.length > 0;
  }
}
