"""
Constants and configuration for Image Comparator
"""

# UI Constants
COLOR_BETTER = "#00FF00"
COLOR_WORSE = "#FF5555"
COLOR_NEUTRAL = "#e0e0e0"
COLOR_SSIM = "#00FFFF"
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 600
VERSION_STRING = "Image Comparer v1.5"

# Loading constants
THUMBNAIL_SIZE = 400
NAVIGATION_DELAY_MS = 300  # Wait before loading full quality
PRELOAD_DELAY_MS = 5000    # Wait before preloading adjacent images
MAX_PRELOAD_FORWARD = 10
MAX_PRELOAD_BACKWARD = 5

# Memory management
MAX_CACHE_DISTANCE = 15  # Keep images within this distance from current
MAX_THREAD_COUNT = 4     # Maximum concurrent loading threads

# Valid image extensions
VALID_IMAGE_EXTENSIONS = ('.jpg', '.jpeg', '.png', '.webp', '.tif', '.tiff')

# Dark theme stylesheet
DARK_THEME = """
    QWidget {
        background-color: #000000;
        color: #ffffff;
    }
    QComboBox, QPushButton, QCheckBox, QLabel {
        background-color: #121212;
        color: #e0e0e0;
        border: 1px solid #d0d0d0;
        padding: 6px 10px;  /* Increased padding */
        border-radius: 5px;  /* Added curved borders */
    }
    QScrollArea, QStatusBar {
        background-color: #121212;
        border: none;
    }
    QToolTip {
        color: #e0e0e0;
        background-color: #121212;
        border: 1px solid #d0d0d0;
    }
"""

COMMON_BUTTON_STYLE = """
    background-color: #121212;
    color: #e0e0e0;
    border: 1px solid #d0d0d0;
    padding: 6px 10px;  /* Increased padding */
    border-radius: 5px;  /* Added curved borders */
"""

# Hover effect for buttons
BUTTON_HOVER_STYLE = """
    QPushButton:hover {
        background-color: #333333;  /* Slightly lighter on hover */
        border-color: #b0b0b0;     /* Lighter border on hover */
    }
"""
