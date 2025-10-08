// keyboardHandler.js - Keyboard navigation and shortcuts

export class KeyboardHandler {
  constructor(imageLoader, scrollHandler, uiController) {
    this.imageLoader = imageLoader;
    this.scrollHandler = scrollHandler;
    this.uiController = uiController;

    this.attachEventListeners();
  }

  attachEventListeners() {
    document.addEventListener("keydown", (e) => this.handleKeydown(e));

    const pageInput = document.getElementById("pageInput");
    pageInput.addEventListener("keydown", (e) =>
      this.handlePageInputKeydown(e)
    );
  }

  async handleKeydown(e) {
    // Toggle shortcuts (work everywhere)


    if (e.key.toLowerCase() === "f") {
      e.preventDefault();
      await this.handleFitToggle();
      return;
    }    

    if (e.key.toLowerCase() === "b") {
      e.preventDefault();
      await this.handleBorderToggle();
      return;
    }

    if (e.key.toLowerCase() === "s") {
      e.preventDefault();
      this.scrollHandler.toggleScrollbar();
      return;
    }

    // Navigation (only if images loaded)
    if (!this.imageLoader.hasImages) return;
    if (document.activeElement.tagName === "INPUT") return;

    const currentPage = this.imageLoader.getCurrentPage();
    let targetPage = currentPage;
    let handled = false;

    switch (e.key) {
      case "ArrowRight":
        targetPage = Math.min(currentPage + 1, this.imageLoader.totalPages);
        handled = true;
        break;
      case "ArrowLeft":
        targetPage = Math.max(currentPage - 1, 1);
        handled = true;
        break;
      case "PageDown":
        targetPage = Math.min(currentPage + 10, this.imageLoader.totalPages);
        handled = true;
        break;
      case "PageUp":
        targetPage = Math.max(currentPage - 10, 1);
        handled = true;
        break;
      case "Home":
        targetPage = 1;
        handled = true;
        break;
      case "End":
        targetPage = this.imageLoader.totalPages;
        handled = true;
        break;
    }

    if (handled) {
      e.preventDefault();
      await this.imageLoader.scrollToPage(targetPage);

      // Force UI update after jump
      this.imageLoader.currentPageCache = null;
      await new Promise((r) => setTimeout(r, 50));
      this.uiController.updatePageUI();
    }
  }

  async handlePageInputKeydown(e) {
    if (e.key !== "Enter") return;

    let pageNum = parseInt(e.target.value);
    if (isNaN(pageNum) || pageNum < 1) return;

    pageNum = Math.min(pageNum, this.imageLoader.totalPages);

    const currentPage = this.imageLoader.getCurrentPage();
    const smooth = Math.abs(pageNum - currentPage) <= 5;

    await this.imageLoader.scrollToPage(pageNum);
    this.uiController.updatePageUI();
  }

  async handleFitToggle() {
    const currentPage = this.imageLoader.getCurrentPage();
    const newState = await this.imageLoader.toggleFit(currentPage);
    this.uiController.updateToggleButtons();
    this.uiController.updatePageUI();
  }

  async handleBorderToggle() {
    const currentPage = this.imageLoader.getCurrentPage();
    const newState = await this.imageLoader.toggleBorders(currentPage);
    this.uiController.updateToggleButtons();
    this.uiController.updatePageUI();
  }
}
