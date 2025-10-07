// script.js
import { ParticleEffects } from "./splash.js";
import { ConstellationHelper } from "./constellation.js";
import { ConstellationSpawner } from "./constellationSpawner.js";

let fitToWidth = false;
let bordersOn = false;
let allFiles = [];
let loadedCount = 0;
let scrollbarVisible = true;
const batchSize = 10;

document.addEventListener("DOMContentLoaded", () => {
  const folderPicker = document.getElementById("folderPicker");
  const openFolderBtn = document.getElementById("openFolderBtn");
  const openArchiveBtn = document.getElementById("openArchiveBtn");
  const fitToggle = document.getElementById("fitToggle");
  const borderToggle = document.getElementById("borderToggle");
  const closeBannerBtn = document.querySelector("#infoBanner .close-btn");
  const topBar = document.querySelector(".top-bar");
  const pageInput = document.getElementById("pageInput");
  const pageTotal = document.getElementById("pageTotalBtn");
  const scrollToggle = document.getElementById("scrollToggle");
  // restore saved preference (if present)
  const saved = localStorage.getItem("scrollbarVisible");
  if (saved !== null) scrollbarVisible = saved === "1";
  // apply initial class according to state
  document.body.classList.toggle("hide-scrollbar", !scrollbarVisible);

  openFolderBtn.addEventListener("click", () => folderPicker.click());
  openArchiveBtn.addEventListener("click", chooseFolder);
  fitToggle.addEventListener("click", toggleFit);
  borderToggle.addEventListener("click", toggleBorders);
  closeBannerBtn.addEventListener("click", hideInfoBanner);

  scrollToggle.addEventListener("click", () => {
    scrollbarVisible = !scrollbarVisible;

    if (scrollbarVisible) {
      // fully show scrollbar
      document.body.classList.remove("hide-scrollbar", "show-scrollbar");
    } else {
      // hide scrollbar, and ensure temporary-show is not set
      document.body.classList.add("hide-scrollbar");
      document.body.classList.remove("show-scrollbar");
    }

    // persist preference (optional, but useful)
    try {
      localStorage.setItem("scrollbarVisible", scrollbarVisible ? "1" : "0");
    } catch (e) {}
  });

  // UI initialization
  fitToggle.innerText = fitToWidth ? "🖼 Original Size" : "🖥 Full Screen";
  borderToggle.innerText = bordersOn ? "🎨 Remove Borders" : "🎨 Add Borders";
  openFolderBtn.title = "Open a folder of images";
  openArchiveBtn.title = "View CBZ/PDF (see instructions)";
  fitToggle.title = "Toggle fit-to-width (F)";
  borderToggle.title = "Toggle borders (B)";
  scrollToggle.title = "Toggle Scrollbar (S)";


  // Hide buttons that should start hidden
  fitToggle.style.display = "none";
  borderToggle.style.display = "none";
  pageInput.style.display = "none";
  pageTotal.style.display = "none";
  scrollToggle.style.display = "none";


  // Show only the Open Folder/Open Archive buttons
  openFolderBtn.style.display = "inline-block";
  openArchiveBtn.style.display = "inline-block";

  // Show top bar container so the open buttons are visible
  topBar.classList.add("show");
  topBar.classList.remove("hide");
});

function chooseFolder() {
  alert(
    "📦 To open a CBZ, PDF or RAR:\n\n1. Open the 'Manga Reader' folder.\n2. Run:\n\n    python mangareader.py\n\nThis will extract your manga and auto-launch this viewer."
  );
}

async function toggleFit() {
  const currentPage = getCurrentPage(); // record current page
  fitToWidth = !fitToWidth;

  document.querySelectorAll("img.manga-img").forEach((img) => {
    fitToWidth
      ? img.classList.remove("original-size")
      : img.classList.add("original-size");
  });

  document.getElementById("fitToggle").innerText = fitToWidth
    ? "🖼 Original Size"
    : "🖥 Full Screen";

  // Force jump to the current page after toggle
  await scrollToPage(currentPage);
}

// Helper function to scroll to a page with batch loading
async function scrollToPage(pageNum) {
  pageNum = Math.min(Math.max(1, pageNum), allFiles.length);

  // Load batches until page exists
  while (loadedCount < pageNum) {
    loadNextBatch();
    await new Promise((r) => setTimeout(r, 0)); // yield to DOM
  }

  // Instant jump (no smooth)
  document
    .querySelectorAll("img.manga-img")
    [pageNum - 1].scrollIntoView({ behavior: "auto", block: "start" });

  // Wait until page is visible
  await new Promise((resolve) => {
    const checkVisible = () => {
      const rect = document
        .querySelectorAll("img.manga-img")
        [pageNum - 1].getBoundingClientRect();
      if (rect.top >= 0 && rect.bottom <= window.innerHeight + 20) {
        resolve();
      } else {
        requestAnimationFrame(checkVisible);
      }
    };
    checkVisible();
  });

  pageInput.value = getCurrentPage();
  resizePageInput();
}

async function toggleBorders() {
  const currentPage = getCurrentPage();
  bordersOn = !bordersOn;

  document.getElementById("borderToggle").innerText = bordersOn
    ? "🎨 Remove Borders"
    : "🎨 Add Borders";

  document.querySelectorAll("img.manga-img").forEach((img) => {
    bordersOn
      ? img.classList.add("bordered")
      : img.classList.remove("bordered");
  });

  await scrollToPage(currentPage);
}


function hideInfoBanner() {
  const banner = document.getElementById("infoBanner");
  if (!banner) return;
  banner.style.animation = "slideOut 0.5s forwards";
  banner.addEventListener("animationend", () => banner.remove(), {
    once: true,
  });
}

function showTopBar() {
  const topBar = document.querySelector(".top-bar");
  topBar.classList.add("show");
  topBar.classList.remove("hide");
  slideDownElements();
}

function hideTopBar() {
  const topBar = document.querySelector(".top-bar");
  topBar.classList.remove("show");
  topBar.classList.add("hide");
  slideUpElements();
  resetPageInputOnHide();
}

function slideDownElements() {
  const elems = [
    pageInput,
    pageTotal,
    document.getElementById("fitToggle"),
    document.getElementById("borderToggle"),
  ];
  elems.forEach((el) => {
    el.style.transition = "all 0.3s ease";
    el.style.opacity = "1";
    el.style.transform = "translateY(0)";
    el.style.display = "inline-block";
  });
}

function slideUpElements() {
  const elems = [
    pageInput,
    pageTotal,
    document.getElementById("fitToggle"),
    document.getElementById("borderToggle"),
  ];
  elems.forEach((el) => {
    el.style.transition = "all 0.3s ease";
    el.style.opacity = "0";
    el.style.transform = "translateY(-20px)";
    setTimeout(() => (el.style.display = "none"), 300);
  });
}

let topBarHideTimeout;

document.body.addEventListener("mousemove", (e) => {
  const topBar = document.querySelector(".top-bar");

  if (e.clientY <= 50 && allFiles.length) {
    // Show immediately
    topBar.classList.add("show");
    topBar.classList.remove("hide");

    pageIndicatorPriority = true;
    showPageIndicator(true);
    updatePageUI();

    // Cancel pending hide
    clearTimeout(topBarHideTimeout);
  } else if (allFiles.length) {
    // Start delayed hide
    clearTimeout(topBarHideTimeout);
    topBarHideTimeout = setTimeout(() => {
      // Don't hide if pageInput is focused
      if (document.activeElement === pageInput) return;

      topBar.classList.remove("show");
      topBar.classList.add("hide");
      pageIndicatorPriority = false;
      hidePageIndicator();
    }, 900); // delay
  }
});

const folderPicker = document.getElementById("folderPicker");
folderPicker.addEventListener("change", () => {
  allFiles = Array.from(folderPicker.files)
    .sort((a, b) => a.name.localeCompare(b.name))
    .filter((f) => f.type.startsWith("image/"));
  loadedCount = 0;
  if (!allFiles.length) return;

  showTopBar();

  const splash = document.getElementById("splash");
  if (splash) splash.remove();

  hideInfoBanner();
  document.querySelectorAll(".manga-img").forEach((el) => el.remove());

  loadNextBatch();
  updatePageUI();
});

function loadNextBatch() {
  const nextFiles = allFiles.slice(loadedCount, loadedCount + batchSize);
  nextFiles.forEach((file) => {
    const img = document.createElement("img");
    img.classList.add("manga-img");
    img.src = URL.createObjectURL(file);
    if (bordersOn) img.classList.add("bordered");
    if (!fitToWidth) img.classList.add("original-size");
    document.body.appendChild(img);
  });
  loadedCount += nextFiles.length;
}

document.addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() === "f") toggleFit();
  if (e.key.toLowerCase() === "b") toggleBorders();
  if (e.key.toLowerCase() === "s") {
    e.preventDefault();
    scrollToggle.click();
  }
});

const pageIndicator = document.getElementById("pageIndicator");
const pageInput = document.getElementById("pageInput");
const pageTotal = document.getElementById("pageTotalBtn");
let scrollTimeout;
let pageIndicatorPriority = false;

function getCurrentPage() {
  const imgs = document.querySelectorAll("img.manga-img");
  if (!imgs.length) return 1;
  const viewportMiddle = window.innerHeight / 2;
  let currentPage = 1;
  imgs.forEach((img, index) => {
    const rect = img.getBoundingClientRect();
    if (rect.top <= viewportMiddle && rect.bottom >= viewportMiddle)
      currentPage = index + 1;
  });
  return currentPage;
}

function resizePageInput() {
  const input = pageInput;
  const valueLength = input.value.length;
  input.style.width = `${Math.max(2, valueLength)}ch`;
}

// Call this whenever the pageInput value changes
pageInput.addEventListener("input", resizePageInput);
pageInput.addEventListener("keydown", () => setTimeout(resizePageInput, 0));

pageInput.addEventListener("blur", () => {
  if (allFiles.length) {
    clearTimeout(topBarHideTimeout);
    topBarHideTimeout = setTimeout(() => {
      const topBar = document.querySelector(".top-bar");
      topBar.classList.remove("show");
      topBar.classList.add("hide");
      pageIndicatorPriority = false;
      hidePageIndicator();
    }, 900);
  }
});

// Also call after UI updates
function updatePageUI() {
  const imgs = document.querySelectorAll("img.manga-img");
  const hasFolder = imgs.length > 0;

  pageInput.style.display = hasFolder ? "inline-block" : "none";
  pageTotal.style.display = hasFolder ? "inline-block" : "none";
  document.getElementById("fitToggle").style.display = hasFolder
    ? "inline-block"
    : "none";
  document.getElementById("borderToggle").style.display = hasFolder
    ? "inline-block"
    : "none";
  document.getElementById("scrollToggle").style.display = hasFolder
    ? "inline-block"
    : "none";  

  if (!hasFolder) {
    pageIndicator.style.display = "none";
    return;
  }

  const current = getCurrentPage();
  const total = allFiles.length;

  pageIndicator.style.display = "block";
  pageIndicator.textContent = `${current} / ${total}`;
  pageTotal.textContent = `/ ${total}`;
  pageInput.value = current;

  resizePageInput(); // adjust width dynamically
}

function showPageIndicator(priority = false) {
  if (priority) pageIndicatorPriority = true;
  pageIndicator.style.opacity = 1;
  clearTimeout(scrollTimeout);
  if (!priority) {
    scrollTimeout = setTimeout(() => {
      if (!pageIndicatorPriority) pageIndicator.style.opacity = 0;
    }, 1200);
  }
}

function hidePageIndicator() {
  pageIndicator.style.opacity = 0;
  pageIndicatorPriority = false;
}

window.addEventListener("scroll", () => {
  updatePageUI();
  showPageIndicator();
  if (loadedCount < allFiles.length) {
    const lastImg = document.querySelector("img.manga-img:last-of-type");
    if (
      lastImg &&
      lastImg.getBoundingClientRect().bottom <= window.innerHeight + 200
    ) {
      loadNextBatch();
    }
  }
});

pageInput.addEventListener("keydown", async (e) => {
  if (e.key === "Enter") {
    let pageNum = parseInt(pageInput.value);

    if (isNaN(pageNum) || pageNum < 1) return;

    // Clamp to max
    pageNum = Math.min(pageNum, allFiles.length);

    // Load batches until page exists
    while (loadedCount < pageNum) {
      loadNextBatch();
      await new Promise((r) => setTimeout(r, 0));
    }

    // Wait until the image is actually rendered in DOM
    const targetImg = document.querySelectorAll("img.manga-img")[pageNum - 1];
    await new Promise((resolve) => {
      function checkRendered() {
        const rect = targetImg.getBoundingClientRect();
        if (rect.height > 0) resolve();
        else requestAnimationFrame(checkRendered);
      }
      checkRendered();
    });

    // Decide scroll behavior
    const currentPage = getCurrentPage();
    const behavior = Math.abs(pageNum - currentPage) <= 5 ? "smooth" : "auto";
    targetImg.scrollIntoView({ behavior: behavior, block: "start" });

    pageInput.value = getCurrentPage();
    resizePageInput();
  }
});

document.addEventListener("keydown", async (e) => {
  if (!allFiles.length) return;

  const currentPage = getCurrentPage();
  let targetPage = currentPage;
  let handled = false;

  switch (e.key) {
    case "ArrowRight":
      targetPage = Math.min(currentPage + 1, allFiles.length);
      handled = true;
      break;
    case "ArrowLeft":
      targetPage = Math.max(currentPage - 1, 1);
      handled = true;
      break;
    case "PageDown":
      targetPage = Math.min(currentPage + 10, allFiles.length);
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
      targetPage = allFiles.length;
      handled = true;
      break;
    // ArrowUp and ArrowDown are not intercepted, normal scroll works
  }

  if (handled) {
    e.preventDefault(); // only prevent default for keys we handle
    await scrollToPage(targetPage);
  }
});

window.addEventListener("keydown", (e) => {
  if (e.key.toLowerCase() === "f") {
    e.preventDefault();
    window.electronAPI.toggleFullscreen();
  }
});


// Reset top bar input to match floating indicator when top bar hides
function resetPageInputOnHide() {
  if (!pageIndicator.textContent.includes("/")) return;
  pageInput.value = pageIndicator.textContent.split(" / ")[0];
}

// 1️⃣ Start background particle system and get particles
const particleSystem = ParticleEffects(); // returns { particles }

// 2️⃣ Setup canvas context
const canvas = document.getElementById("splashParticles");
const ctx = canvas.getContext("2d");

// 3️⃣ Create constellation spawner using the same background particles
const spawner = new ConstellationSpawner(
  ctx,
  window.innerWidth,
  window.innerHeight,
  particleSystem.particles
);
spawner.startBackground(); // ensures background runs right away

// 4️⃣ Launch random constellations at intervals
function scheduleConstellation() {
  const delay = 12000 + Math.random() * 10000; // 12–22 sec between constellations
  setTimeout(() => {
    spawner.spawnConstellation(ConstellationHelper);
    scheduleConstellation(); // schedule next
  }, delay);
}
scheduleConstellation();

// 5️⃣ Optional: handle resize
window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
  spawner.width = window.innerWidth;
  spawner.height = window.innerHeight;
});

let scrollbarTimeout;

// only show temporary scrollbar when the user has chosen to hide it
window.addEventListener("scroll", () => {
  // if scrollbars are visible by default, nothing to do
  if (!document.body.classList.contains("hide-scrollbar")) return;

  document.body.classList.add("show-scrollbar");
  clearTimeout(scrollbarTimeout);
  scrollbarTimeout = setTimeout(() => {
    document.body.classList.remove("show-scrollbar");
  }, 1200); // 1.2s after last scroll
});




