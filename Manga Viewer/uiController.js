// uiController.js - Performance-optimized UI updates

export class UIController {
  constructor(imageLoader, scrollHandler) {
    this.imageLoader = imageLoader;
    this.scrollHandler = scrollHandler;
    this.topBarHideTimeout = null;
    this.pageIndicatorPriority = false;
    this.scrollTimeout = null;

    // Performance optimizations
    this.updateScheduled = false;
    this.lastUpdateTime = 0;
    this.updateThrottle = 100; // ms between UI updates
    this.elements = {};

    this.initElements();
    this.attachEventListeners();
  }

  initElements() {
    // Cache all DOM queries
    this.elements = {
      topBar: document.querySelector(".top-bar"),
      pageIndicator: document.getElementById("pageIndicator"),
      pageInput: document.getElementById("pageInput"),
      pageTotal: document.getElementById("pageTotalBtn"),
      fitToggle: document.getElementById("fitToggle"),
      borderToggle: document.getElementById("borderToggle"),
      scrollToggle: document.getElementById("scrollToggle"),
      openFolderBtn: document.getElementById("openFolderBtn"),
      openArchiveBtn: document.getElementById("openArchiveBtn"),
      infoBanner: document.getElementById("infoBanner"),
      splash: document.getElementById("splash"),
    };
  }

  attachEventListeners() {
    const { pageInput } = this.elements;

    // Debounced input resize
    pageInput.addEventListener("input", () => this.scheduleResize());
    pageInput.addEventListener("keydown", () => this.scheduleResize());
    pageInput.addEventListener("blur", () => this.handlePageInputBlur());

    // Throttled scroll updates using RAF
    window.addEventListener("scroll", () => this.scheduleUpdate(), {
      passive: true,
    });
  }

  scheduleResize() {
    // Immediate resize for better responsiveness
    requestAnimationFrame(() => this.resizePageInput());
  }

  scheduleUpdate() {
    if (this.updateScheduled) return;

    this.updateScheduled = true;
    requestAnimationFrame(() => {
      const now = performance.now();

      // Throttle updates to avoid excessive reflows
      if (now - this.lastUpdateTime >= this.updateThrottle) {
        this.updatePageUI();
        this.showPageIndicator();
        this.lastUpdateTime = now;
      }

      this.updateScheduled = false;
    });
  }

  resizePageInput() {
    const input = this.elements.pageInput;
    const valueLength = input.value.length;
    const newWidth = `${Math.max(2, valueLength)}ch`;

    // Only update if changed (avoid unnecessary reflows)
    if (input.style.width !== newWidth) {
      input.style.width = newWidth;
    }
  }

  updatePageUI() {
    const {
      pageInput,
      pageTotal,
      pageIndicator,
      fitToggle,
      borderToggle,
      scrollToggle,
    } = this.elements;
    const hasFolder = this.imageLoader.hasImages;

    // Batch DOM reads and writes
    const display = hasFolder ? "inline-block" : "none";

    // Write phase
    requestAnimationFrame(() => {
      pageInput.style.display = display;
      pageTotal.style.display = display;
      fitToggle.style.display = display;
      borderToggle.style.display = display;
      scrollToggle.style.display = display;

      if (!hasFolder) {
        pageIndicator.style.display = "none";
        return;
      }

      // Force fresh calculation - don't use cached value during jumps
      const current = this.imageLoader.getCurrentPage();
      const total = this.imageLoader.totalPages;

      pageIndicator.style.display = "block";
      pageIndicator.textContent = `${current} / ${total}`;
      pageTotal.textContent = `/ ${total}`;

      // Only update input if it's not focused (user might be typing)
      if (document.activeElement !== pageInput) {
        pageInput.value = current;
      }

      this.resizePageInput();
    });
  }

  showPageIndicator(priority = false) {
    if (priority) this.pageIndicatorPriority = true;

    const indicator = this.elements.pageIndicator;

    // Use CSS class for smoother transitions
    if (indicator.style.opacity !== "1") {
      indicator.style.opacity = 1;
    }

    clearTimeout(this.scrollTimeout);

    if (!priority) {
      this.scrollTimeout = setTimeout(() => {
        if (!this.pageIndicatorPriority) {
          indicator.style.opacity = 0;
        }
      }, 1200);
    }
  }

  hidePageIndicator() {
    this.elements.pageIndicator.style.opacity = 0;
    this.pageIndicatorPriority = false;
  }

  showTopBar() {
    const { topBar } = this.elements;
    topBar.classList.add("show");
    topBar.classList.remove("hide");
    this.slideDownElements();
  }

  hideTopBar() {
    const { topBar } = this.elements;
    topBar.classList.remove("show");
    topBar.classList.add("hide");
    this.slideUpElements();
    this.resetPageInputOnHide();
  }

  slideDownElements() {
    const { pageInput, pageTotal, fitToggle, borderToggle } = this.elements;
    const elems = [pageInput, pageTotal, fitToggle, borderToggle];

    // Batch style updates
    requestAnimationFrame(() => {
      elems.forEach((el) => {
        el.style.transition = "all 0.3s ease";
        el.style.opacity = "1";
        el.style.transform = "translateY(0)";
        el.style.display = "inline-block";
      });
    });
  }

  slideUpElements() {
    const { pageInput, pageTotal, fitToggle, borderToggle } = this.elements;
    const elems = [pageInput, pageTotal, fitToggle, borderToggle];

    // Batch style updates
    requestAnimationFrame(() => {
      elems.forEach((el) => {
        el.style.transition = "all 0.3s ease";
        el.style.opacity = "0";
        el.style.transform = "translateY(-20px)";
      });

      // Delay display:none to allow animation
      setTimeout(() => {
        elems.forEach((el) => (el.style.display = "none"));
      }, 300);
    });
  }

  resetPageInputOnHide() {
    const indicator = this.elements.pageIndicator;
    const text = indicator.textContent;

    if (!text.includes("/")) return;

    const current = text.split(" / ")[0];
    if (this.elements.pageInput.value !== current) {
      this.elements.pageInput.value = current;
    }
  }

  handlePageInputBlur() {
    if (!this.imageLoader.hasImages) return;

    clearTimeout(this.topBarHideTimeout);
    this.topBarHideTimeout = setTimeout(() => {
      this.hideTopBar();
      this.pageIndicatorPriority = false;
      this.hidePageIndicator();
    }, 900);
  }

  handleMouseMove(e) {
    const hasImages = this.imageLoader.hasImages;

    if (e.clientY <= 50 && hasImages) {
      this.showTopBar();
      this.pageIndicatorPriority = true;
      this.showPageIndicator(true);
      this.scheduleUpdate();
      clearTimeout(this.topBarHideTimeout);
    } else if (hasImages) {
      clearTimeout(this.topBarHideTimeout);
      this.topBarHideTimeout = setTimeout(() => {
        if (document.activeElement === this.elements.pageInput) return;
        this.hideTopBar();
        this.pageIndicatorPriority = false;
        this.hidePageIndicator();
      }, 900);
    }
  }

  hideInfoBanner() {
    const banner = this.elements.infoBanner;
    if (!banner) return;

    banner.style.animation = "slideOut 0.5s forwards";
    banner.addEventListener("animationend", () => banner.remove(), {
      once: true,
    });
  }

  removeSplash() {
    const splash = this.elements.splash;
    if (splash) splash.remove();
  }

  updateToggleButtons() {
    requestAnimationFrame(() => {
      this.elements.fitToggle.innerText = this.imageLoader.fitToWidth
        ? "🖼 Original Size"
        : "🖥 Full Screen";

      this.elements.borderToggle.innerText = this.imageLoader.bordersOn
        ? "🎨 Remove Borders"
        : "🎨 Add Borders";
    });
  }
}
