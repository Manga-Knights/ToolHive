// scrollHandler.js - Hybrid scroll handler with smart loading

export class ScrollHandler {
  constructor(imageLoader) {
    this.imageLoader = imageLoader;
    this.scrollTimeout = null;
    this.scrollbarTimeout = null;
    this.scrollbarVisible = true;
    this.loadThreshold = 300; // pixels before triggering load

    // Performance optimizations
    this.lastScrollTime = 0;
    this.scrollThrottle = 16;
    this.rafPending = false;
    this.lastKnownScrollY = 0;
    this.ticking = false;

    // Unload check throttling
    this.lastUnloadCheck = 0;
    this.unloadCheckInterval = 2000; // Check every 2 seconds

    this.init();
  }

  init() {
    // Restore scrollbar preference
    const saved = localStorage.getItem("scrollbarVisible");
    if (saved !== null) {
      this.scrollbarVisible = saved === "1";
      document.body.classList.toggle("hide-scrollbar", !this.scrollbarVisible);
    }

    // Use passive listeners for better scroll performance
    window.addEventListener("scroll", () => this.onScroll(), { passive: true });
  }

  onScroll() {
    this.lastKnownScrollY = window.scrollY;

    if (!this.ticking) {
      requestAnimationFrame(() => {
        this.handleScroll();
        this.ticking = false;
      });
      this.ticking = true;
    }

    this.handleScrollbarVisibility();
  }

  handleScroll() {
    // Invalidate imageLoader's rect cache on scroll
    this.imageLoader.invalidateRectCache();

    // Check if we need to load more images
    this.checkLoadMore();

    // Periodically check if we should unload distant images
    const now = Date.now();
    if (now - this.lastUnloadCheck > this.unloadCheckInterval) {
      this.imageLoader.unloadDistantImages();
      this.lastUnloadCheck = now;
    }
  }

  checkLoadMore() {
    if (!this.imageLoader.hasImages) return;

    const imgs = document.querySelectorAll("img.manga-img");
    if (imgs.length === 0) return;

    // Get first and last loaded images
    const firstImg = imgs[0];
    const lastImg = imgs[imgs.length - 1];

    const firstRect = firstImg.getBoundingClientRect();
    const lastRect = lastImg.getBoundingClientRect();

    const viewportHeight = window.innerHeight;

    // Load more at bottom if needed
    if (lastRect.bottom <= viewportHeight + this.loadThreshold) {
      const lastIndex = parseInt(lastImg.dataset.pageIndex);
      if (lastIndex < this.imageLoader.totalPages - 1) {
        this.imageLoader.loadBatch(lastIndex + 1);
      }
    }

    // Load more at top if needed (for scrolling back up)
    if (firstRect.top >= -this.loadThreshold) {
      const firstIndex = parseInt(firstImg.dataset.pageIndex);
      if (firstIndex > 0) {
        this.imageLoader.loadBatch(firstIndex - this.imageLoader.batchSize);
      }
    }
  }

  handleScrollbarVisibility() {
    // Only show temporary scrollbar when user has chosen to hide it
    if (!document.body.classList.contains("hide-scrollbar")) return;

    if (!document.body.classList.contains("show-scrollbar")) {
      document.body.classList.add("show-scrollbar");
    }

    clearTimeout(this.scrollbarTimeout);
    this.scrollbarTimeout = setTimeout(() => {
      document.body.classList.remove("show-scrollbar");
    }, 1200);
  }

  toggleScrollbar() {
    this.scrollbarVisible = !this.scrollbarVisible;

    if (this.scrollbarVisible) {
      document.body.classList.remove("hide-scrollbar", "show-scrollbar");
    } else {
      document.body.classList.add("hide-scrollbar");
      document.body.classList.remove("show-scrollbar");
    }

    try {
      localStorage.setItem(
        "scrollbarVisible",
        this.scrollbarVisible ? "1" : "0"
      );
    } catch (e) {
      console.warn("Could not save scrollbar preference");
    }
  }

  async navigateToPage(targetPage, smooth = false) {
    targetPage = Math.min(Math.max(1, targetPage), this.imageLoader.totalPages);
    const pageIndex = targetPage - 1;

    // Load images around target
    await this.imageLoader.loadAroundPage(pageIndex);

    // Find target image
    let targetImg = this.imageLoader.imageCache.get(pageIndex);

    if (!targetImg) {
      await new Promise((r) => setTimeout(r, 50));
      targetImg = this.imageLoader.imageCache.get(pageIndex);
    }

    if (!targetImg) {
      console.warn(`Could not find image for page ${targetPage}`);
      return;
    }

    // Wait for image to load
    if (!targetImg.complete) {
      await new Promise((resolve) => {
        targetImg.onload = resolve;
        targetImg.onerror = resolve;
        setTimeout(resolve, 2000);
      });
    }

    const behavior = smooth ? "smooth" : "auto";
    targetImg.scrollIntoView({ behavior, block: "start" });
  }

  cleanup() {
    // Cleanup if needed
  }
}
