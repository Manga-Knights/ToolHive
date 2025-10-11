from PyQt5.QtWidgets import QLabel

def update_metrics_display(self, metrics):
    """Update or create a status bar metrics display with color-coded values."""
    # Create the label once and keep a reference
    if not hasattr(self, "metrics_label"):
        self.metrics_label = QLabel()
        self.metrics_label.setStyleSheet("padding: 4px;")
        self.status_bar.insertPermanentWidget(1, self.metrics_label, 1)

    # --- Color logic: green = better, red = worse, white = equal ---
    def colorize(val1, val2, higher_is_better=True):
        if val1 == val2:
            return "#FFFFFF", "#FFFFFF"
        if (val1 > val2 and higher_is_better) or (val1 < val2 and not higher_is_better):
            return "#00FF00", "#FF5555"  # left better: green/red
        else:
            return "#FF5555", "#00FF00"  # right better: red/green

    # --- Assign per-metric colors ---
    psnr_c1, psnr_c2 = colorize(metrics["psnr1"], metrics["psnr2"])
    sharp_c1, sharp_c2 = colorize(metrics["sharpness1"], metrics["sharpness2"])
    noise_c1, noise_c2 = colorize(metrics["noise1"], metrics["noise2"], higher_is_better=False)

    # --- Format display sections ---
    left = (
        f"<span style='color:{psnr_c1}'>PSNR: {metrics['psnr1']:.2f}</span>"
        f" | <span style='color:{sharp_c1}'>Sharp: {metrics['sharpness1']:.2f}</span>"
        f" | <span style='color:{noise_c1}'>Noise: {metrics['noise1']:.2f}</span>"
    )

    center = f"<span style='color:#00FFFF'>SSIM: {metrics['ssim']:.4f}</span>"

    right = (
        f"<span style='color:{psnr_c2}'>PSNR: {metrics['psnr2']:.2f}</span>"
        f" | <span style='color:{sharp_c2}'>Sharp: {metrics['sharpness2']:.2f}</span>"
        f" | <span style='color:{noise_c2}'>Noise: {metrics['noise2']:.2f}</span>"
    )

    # --- Update label HTML ---
    self.metrics_label.setText(
        f"""
        <div style="width:100%; overflow:hidden;">
            <div style="float:left;">{left}</div>
            <div style="text-align:center;">{center}</div>
            <div style="float:right;">{right}</div>
        </div>
        """
    )
