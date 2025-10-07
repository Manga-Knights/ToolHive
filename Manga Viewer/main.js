const { app, BrowserWindow, ipcMain, dialog } = require("electron");
const { autoUpdater } = require("electron-updater");
const path = require("path");

function createWindow() {
  const win = new BrowserWindow({
    width: 1200,
    height: 800,
    minWidth: 800,
    minHeight: 600,
    frame: true, // ✅ native title bar with minimize/maximize/close
    autoHideMenuBar: true, // ✅ hides File/Edit unless Alt is pressed
    icon: path.join(__dirname, "icon.ico"),
    webPreferences: {
      preload: path.join(__dirname, "preload.js"),
      contextIsolation: true,
      nodeIntegration: false,
    },
  });

  // Optional: permanently hide the menu bar (even with Alt key)
  win.setMenuBarVisibility(false);

  win.loadFile("index.html");
  // win.webContents.openDevTools(); // Uncomment for debugging
}

// --- Auto Updater Setup ---
function setupAutoUpdater() {
  autoUpdater.autoDownload = true;
  autoUpdater.autoInstallOnAppQuit = true;

  autoUpdater.on("checking-for-update", () => {
    console.log("Checking for update...");
  });
  autoUpdater.on("update-available", () => {
    console.log("Update available. Downloading...");
  });
  autoUpdater.on("update-not-available", () => {
    console.log("No updates available.");
  });
  autoUpdater.on("error", (err) => {
    console.error("Error in auto-updater:", err);
  });
  autoUpdater.on("update-downloaded", () => {
    console.log("Update downloaded; will install on quit.");
  });

  // Check for updates right after app starts
  autoUpdater.checkForUpdatesAndNotify();
}

// --- App Lifecycle ---
app.whenReady().then(() => {
  createWindow();
  setupAutoUpdater();
});

app.on("window-all-closed", () => {
  if (process.platform !== "darwin") app.quit();
});

app.on("activate", () => {
  if (BrowserWindow.getAllWindows().length === 0) createWindow();
});

// --- Example IPC handler for open file dialog ---
ipcMain.handle("dialog:openFile", async () => {
  const { canceled, filePaths } = await dialog.showOpenDialog({
    properties: ["openFile"],
  });
  return canceled ? null : filePaths[0];
});

ipcMain.on("toggle-fullscreen", () => {
  const win = BrowserWindow.getFocusedWindow();
  if (win) win.setFullScreen(!win.isFullScreen());
});

