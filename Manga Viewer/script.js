// script.js - Application with hybrid lazy loading + memory management

import { ParticleEffects } from "./splash.js";
import { ConstellationHelper } from "./constellation.js";
import { ConstellationSpawner } from "./constellationSpawner.js";
import { ImageLoader } from "./imageLoader.js";
import { ScrollHandler } from "./scrollHandler.js";
import { UIController } from "./uiController.js";
import { KeyboardHandler } from "./keyboardHandler.js";

class MangaReaderApp {
  constructor() {
    this.imageLoader = new ImageLoader();
    this.scrollHandler = new ScrollHandler(this.imageLoader);
    this.uiController = null;
    this.keyboardHandler = null;

    this.init();
  }

  init() {
    document.addEventListener("DOMContentLoaded", () => {
      this.initializeUI();
      this.initializeParticles();
      this.attachEventListeners();
    });
  }

  initializeUI() {
    // Create UI controller
    this.uiController = new UIController(this.imageLoader, this.scrollHandler);

    // Create keyboard handler
    this.keyboardHandler = new KeyboardHandler(
      this.imageLoader,
      this.scrollHandler,
      this.uiController
    );

    // Set initial button states
    const fitToggle = document.getElementById("fitToggle");
    const borderToggle = document.getElementById("borderToggle");
    const scrollToggle = document.getElementById("scrollToggle");
    const openFolderBtn = document.getElementById("openFolderBtn");
    const openArchiveBtn = document.getElementById("openArchiveBtn");

    fitToggle.innerText = "🖥 Full Screen";
    borderToggle.innerText = "🎨 Add Borders";
    openFolderBtn.title = "Open a folder of images";
    openArchiveBtn.title = "View CBZ/PDF (see instructions)";
    fitToggle.title = "Toggle fit-to-width (F)";
    borderToggle.title = "Toggle borders (B)";
    scrollToggle.title = "Toggle Scrollbar (S)";

    // Hide initially
    fitToggle.style.display = "none";
    borderToggle.style.display = "none";
    document.getElementById("pageInput").style.display = "none";
    document.getElementById("pageTotalBtn").style.display = "none";
    scrollToggle.style.display = "none";

    // Show open buttons
    openFolderBtn.style.display = "inline-block";
    openArchiveBtn.style.display = "inline-block";

    const topBar = document.querySelector(".top-bar");
    topBar.classList.add("show");
    topBar.classList.remove("hide");
  }

  initializeParticles() {
    const particleSystem = ParticleEffects();
    const canvas = document.getElementById("splashParticles");
    const ctx = canvas.getContext("2d");

    const spawner = new ConstellationSpawner(
      ctx,
      window.innerWidth,
      window.innerHeight,
      particleSystem.particles
    );
    spawner.startBackground();

    this.scheduleConstellation(spawner);

    window.addEventListener("resize", () => {
      canvas.width = window.innerWidth;
      canvas.height = window.innerHeight;
      spawner.width = window.innerWidth;
      spawner.height = window.innerHeight;
    });
  }

  scheduleConstellation(spawner) {
    const delay = 12000 + Math.random() * 10000;
    setTimeout(() => {
      spawner.spawnConstellation(ConstellationHelper);
      this.scheduleConstellation(spawner);
    }, delay);
  }

  attachEventListeners() {
    const folderPicker = document.getElementById("folderPicker");
    const openFolderBtn = document.getElementById("openFolderBtn");
    const openArchiveBtn = document.getElementById("openArchiveBtn");
    const fitToggle = document.getElementById("fitToggle");
    const borderToggle = document.getElementById("borderToggle");
    const scrollToggle = document.getElementById("scrollToggle");
    const closeBannerBtn = document.querySelector("#infoBanner .close-btn");

    openFolderBtn.addEventListener("click", () => folderPicker.click());
    openArchiveBtn.addEventListener("click", () =>
      this.showArchiveInstructions()
    );

    fitToggle.addEventListener("click", async () => {
      await this.keyboardHandler.handleFitToggle();
    });
    
    

    borderToggle.addEventListener("click", () =>
      this.keyboardHandler.handleBorderToggle()
    );

    scrollToggle.addEventListener("click", () => {
      this.scrollHandler.toggleScrollbar();
    });

    closeBannerBtn.addEventListener("click", () =>
      this.uiController.hideInfoBanner()
    );

    folderPicker.addEventListener("change", () => this.handleFolderSelect());

    document.body.addEventListener("mousemove", (e) =>
      this.uiController.handleMouseMove(e)
    );

    // Fullscreen toggle (if Electron API exists)
    if (window.electronAPI) {
      window.addEventListener("keydown", (e) => {
        if (e.key.toLowerCase() === "f" && e.ctrlKey) {
          e.preventDefault();
          window.electronAPI.toggleFullscreen();
        }
      });
    }
  }

  handleFolderSelect() {
    const folderPicker = document.getElementById("folderPicker");
    this.imageLoader.setFiles(folderPicker.files);

    if (!this.imageLoader.hasImages) return;

    this.uiController.showTopBar();
    this.uiController.removeSplash();
    this.uiController.hideInfoBanner();
    this.imageLoader.clearImages();

    // Load initial batches
    this.imageLoader.loadNextBatch();
    this.imageLoader.loadNextBatch(); // Load 20 images initially

    this.uiController.updatePageUI();
  }

  showArchiveInstructions() {
    alert(
      "📦 To open a CBZ, PDF or RAR:\n\n" +
        "1. Open the 'Manga Reader' folder.\n" +
        "2. Run:\n\n    python mangareader.py\n\n" +
        "This will extract your manga and auto-launch this viewer."
    );
  }
}

// Initialize app
new MangaReaderApp();
