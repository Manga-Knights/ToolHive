const { contextBridge, ipcRenderer } = require("electron");
contextBridge.exposeInMainWorld("electronAPI", {
  setFullscreen: (isFullscreen) =>
    ipcRenderer.send("set-fullscreen", isFullscreen),
  toggleFullscreen: () => ipcRenderer.send("toggle-fullscreen"),
});
  