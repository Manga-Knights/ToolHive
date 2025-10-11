# Image Comparator

A powerful, feature-rich desktop application for comparing images side-by-side with advanced metrics, caching, and intuitive navigation.

![Version](https://img.shields.io/badge/version-0.5-blue)
![Python](https://img.shields.io/badge/python-3.7+-green)
![License](https://img.shields.io/badge/license-MIT-orange)

## 🤝 Credits

This project is built upon the excellent work of [hawier-dev](https://github.com/hawier-dev), who created the original [image_comparator](https://github.com/hawier-dev/image_comparator) structure.

**Special Thanks:**
- **hawier-dev** - For the initial codebase and structure (used with permission)
- **PyQt5 Team** - For the excellent GUI framework
- **Python Community** - For amazing libraries and tools

## 📸 Features

### Core Functionality
- **Side-by-Side Comparison** - Compare two folders of images simultaneously
- **Advanced Image Metrics** - Real-time calculation of PSNR, SSIM, Sharpness, and Noise metrics
- **Smart Caching System** - Intelligent memory management with distance-based eviction
- **Lazy Loading** - Thumbnail preview with delayed full-quality loading
- **Preloading** - Automatic background loading of adjacent images for smooth navigation
- **Animated Placeholders** - Loading and error states with animated GIF support

### User Interface
- **Dark Theme** - Easy on the eyes with modern dark UI
- **Synchronized Zoom & Pan** - Lock/unlock zoom and scroll between images
- **Fullscreen Mode** - Distraction-free comparison view
- **Resolution Switching** - Dynamic resolution selection
- **Antialiasing Toggle** - Smooth or pixel-perfect rendering
- **File Size Display** - See compressed file sizes for each image
- **Cache Statistics** - Monitor memory usage in real-time

### Navigation
- **Keyboard Shortcuts** - Fast navigation with arrow keys, page jumps, and more
- **Direct Page Jump** - Type any page number to jump instantly
- **Batch Navigation** - Jump forward/backward by 10 images
- **Home/End Keys** - Instant first/last image access

### Performance
- **Multi-threaded Loading** - Non-blocking image loading with configurable thread pool
- **Memory Efficient** - Automatic cleanup of distant images from cache
- **Smart Preloading** - Background loading of nearby images when idle
- **Optimized Rendering** - Fast thumbnail generation and scaling

## 🎯 Use Cases

- **Image Quality Comparison** - Compare original vs compressed images
- **A/B Testing** - Visual quality assessment between different processing methods
- **Before/After Analysis** - Side-by-side comparison of edited images
- **Model Output Comparison** - Compare AI model outputs (e.g., image generation, upscaling)
- **Compression Analysis** - Evaluate different compression settings
- **Quality Assurance** - Visual inspection of image processing pipelines

## 📋 Table of Contents

- [Credits](#credits)
- [Installation](#installation)
- [Usage](#usage)
- [Keyboard Shortcuts](#keyboard-shortcuts)
- [Metrics Explained](#metrics-explained)
- [Configuration](#configuration)
- [Building Executable](#building-executable)
- [Project Structure](#project-structure)
- [License](#license)

## 🚀 Installation

### Prebuilt EXE
see releases in the repo: 
https://github.com/Manga-Knights/ToolHive

look for the name Image Comparator v(whatever is latest)
download the exe. nothing else needed


### Prerequisites. for Terminal Usage

- Python 3.7 or higher
- pip (Python package manager)


### Install from Source

1. Clone the repository:
```bash
git clone https://github.com/Manga-Knights/ToolHive.git
cd Image Comparator
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

### Dependencies

- **PyQt5** - GUI framework
- **Pillow**  - Additional image format support
- **NumPy**  - For metrics calculation
- **scikit-image**  - Advanced image metrics

## 📖 Usage

### Via EXE (easiest)
just run the exe. read further for instructions


## Usage for Running from source

### Via Launcher (Recommended)
double click toolhive.bat for interactive run.

for argument forwarding
- open cmd in the project root. and run
toolhive {compare} --argument
 
### Arguments Supported:
--input {folder1} {folder2}  
this directly starts the tool. usage:

either 
toolhive compare --input path/to/folder/1 path/to/folder/2

or
cd Image Comapartor
start_with_folder.py --input path/to/folder/1 path/to/folder/2


--debug
adding this anywhere prints full traceback output if any error ocuurs


### Standalone Usage Via Terminal ( if you are expirienced)

Run the application with two folders:

```bash
python start_with_folder.py
```

Then use the GUI to select two folders for comparison.


### Command Line Usage

You can also pass folder paths directly:

```bash
python start_with_folder.py /path/to/folder1 /path/to/folder2
```

### Folder Requirements

- Both folders should contain images with matching filenames
- Supported formats: `.jpg`, `.jpeg`, `.png`, `.webp`, `.tif`, `.tiff`
- Images are matched and sorted using natural sorting (e.g., img1, img2, img10)
- Folder mismatch warning is shown if image counts differ

### Interface Overview

```

├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────┐         ┌─────────────────┐            |
│  │                 │         │                 │            |
│  │   Left Image    │         │   Right Image   │            |
│  │                 │         │                 │            |
│  └─────────────────┘         └─────────────────┘            |
│                                                             |
┌─────────────────────────────────────────────────────────────┐
│ [Resolution] [Antialiasing] [Sync Lock] [Page: 1 / 100]     |
│ [filename1.jpg]                          [filename2.jpg]    │
├─────────────────────────────────────────────────────────────┤
│ Version | Resolution | Cache Stats | File Sizes | Metrics   │
└─────────────────────────────────────────────────────────────┘
```

### Status Bar Information

- **Version** - Application version number
- **Resolution** - Current display status (Loading/Thumbnail/Full/Cached)
- **Cache Stats** - Format: `Cache: XF / YT / ZM`
  - `XF` - Full quality images cached
  - `YT` - Thumbnails cached
  - `ZM` - Metrics cached
- **File Sizes** - Compressed file sizes of both images
- **Metrics** - Image quality metrics (see [Metrics Explained](#metrics-explained))

## ⌨️ Keyboard Shortcuts

### Navigation
| Shortcut | Action |
|----------|--------|
| `→` Right Arrow | Next image |
| `←` Left Arrow | Previous image |
| `Page Down` | Jump forward 10 images |
| `Page Up` | Jump backward 10 images |
| `Home` | Jump to first image |
| `End` | Jump to last image |

### View Controls
| Shortcut | Action |
|----------|--------|
| `F` | Toggle fullscreen mode |
| `L` | Toggle sync lock (zoom & pan) |
| `Ctrl+S` | Save comparison screenshot |

### Mouse Controls
| Action | Function |
|--------|----------|
| **Scroll Wheel** | Zoom in/out |
| **Click + Drag** | Pan image (when zoomed) |
| **Double Click** | Fit image to view |

### Direct Navigation
| Action | Function |
|--------|----------|
| **Type number + Enter** | Jump to specific page |
| **Click page counter** | Edit page number directly |

## 📊 Metrics Explained

The application displays comprehensive image quality metrics in the status bar:

### Left & Right Side Metrics

#### PSNR (Peak Signal-to-Noise Ratio)
- **Range**: 0-100 (higher is better)
- **Meaning**: Measures difference between original and compared image
- **Typical Values**:
  - 30-40 dB: Good quality
  - 40-50 dB: Excellent quality
  - 50+ dB: Nearly identical
- **Color Coding**: Green (better) / Red (worse)

#### Sharpness
- **Range**: 0+ (higher is better)
- **Meaning**: Measures image detail and edge clarity
- **Use Case**: Detect blur or loss of detail
- **Color Coding**: Green (sharper) / Red (blurrier)

#### Noise
- **Range**: 0+ (lower is better)
- **Meaning**: Measures random variation/grain in the image
- **Use Case**: Detect compression artifacts or noise
- **Color Coding**: Green (less noise) / Red (more noise)

### Center Metric

#### SSIM (Structural Similarity Index)
- **Range**: 0-1 (higher is better)
- **Meaning**: Perceptual similarity between images
- **Typical Values**:
  - 0.90-0.95: Very similar
  - 0.95-0.99: Nearly identical
  - 0.99+: Virtually identical
- **Color**: Cyan (always)

### Metric Display Format

```
PSNR: 35.42 | Sharp: 125.3 | Noise: 12.5    SSIM: 0.9523    PSNR: 33.18 | Sharp: 118.7 | Noise: 15.2
      [LEFT IMAGE METRICS]                  [COMPARISON]           [RIGHT IMAGE METRICS]
```

Colors indicate which image is better for each metric.

## ⚙️ Configuration

### Performance Tuning

Edit `constants.py` to adjust performance parameters:

```python
# Threading
MAX_THREAD_COUNT = 4           # Concurrent loading threads

# Loading behavior
NAVIGATION_DELAY_MS = 300      # Delay before loading full quality
PRELOAD_DELAY_MS = 5000        # Delay before preloading adjacent images
THUMBNAIL_SIZE = 400           # Thumbnail resolution

# Preloading range
MAX_PRELOAD_FORWARD = 10       # Images to preload ahead
MAX_PRELOAD_BACKWARD = 5       # Images to preload behind

# Memory management
MAX_CACHE_DISTANCE = 15        # Keep images within N positions
```

### UI Customization

Modify colors and theme in `constants.py`:

```python
# Metric colors
COLOR_BETTER = "#00FF00"       # Green for better metrics
COLOR_WORSE = "#FF5555"        # Red for worse metrics
COLOR_NEUTRAL = "#FFFFFF"      # White for equal metrics
COLOR_SSIM = "#00FFFF"         # Cyan for SSIM

# Window size
MIN_WINDOW_WIDTH = 1200
MIN_WINDOW_HEIGHT = 600
```

### Theme Customization

The dark theme stylesheet can be modified in `constants.py`:

```python
DARK_THEME = """
    QWidget {
        background-color: #121212;
        color: #e0e0e0;
    }
    /* ... more styles ... */
"""
```

## 🔧 Building Executable

### Using PyInstaller

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the executable:
```bash
pyinstaller image_comparator.spec
```

3. Find your executable in:
```
dist/ImageComparator         # Linux/Mac
dist/ImageComparator.exe     # Windows
```

### Executable Features

- **Single File** - All dependencies bundled
- **No Console** - GUI-only mode
- **Icon Embedded** - Custom application icon
- **Assets Included** - Loading/error GIFs bundled

### Distribution

Distribute the entire `dist/` folder or just the executable. Users don't need Python installed.


## 📁 Project Structure

```
image_comparator/
├── start_with_folder.py      # Application entry point
├── main_window.py             # Main UI window and logic
├── workers.py                 # Threading workers (loading/metrics)
├── cache.py                   # Image and metrics caching
├── constants.py               # Configuration and constants
├── utils.py                   # Utility functions
├── graphics_view.py           # Custom graphics view widget
├── image_view.py              # Image display component
├── image_sync.py              # Zoom/pan synchronization
├── image_metrics.py           # Metrics calculation
├── metrics_display.py         # Metrics UI component
├── assets/
│   ├── loading.gif            # Loading animation
│   ├── error.webp             # Error animation
│   └── icon.ico               # Application icon
├── image_comparator.spec      # PyInstaller build config
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

### Module Responsibilities

- **`start_with_folder.py`** - Entry point, logging setup
- **`main_window.py`** - Main window, UI, navigation, worker management
- **`workers.py`** - Threaded image loading and metrics computation
- **`cache.py`** - Memory-efficient caching with eviction strategy
- **`constants.py`** - All configuration values and themes
- **`utils.py`** - Helper functions (sorting, formatting, colorization)
- **`graphics_view.py`** - Custom Qt graphics view with zoom/pan
- **`image_view.py`** - Image display and rendering
- **`image_sync.py`** - Synchronized zoom and scroll
- **`image_metrics.py`** - PSNR, SSIM, sharpness, noise calculations
- **`metrics_display.py`** - Metrics visualization component

## 🎨 Features in Detail

### Smart Caching System

The application uses a sophisticated three-tier caching strategy:

1. **Thumbnails** (400×400) - Fast loading for quick navigation
2. **Full Quality** - Loaded after navigation settles
3. **Metrics** - Kept permanently (small memory footprint)

**Distance-Based Eviction:**
- Images beyond 15 positions from current are evicted
- Prevents memory bloat during long sessions
- Metrics are never evicted (useful for comparison)

### Loading Strategy

**Phase 1: Immediate**
- Show placeholder (loading animation or black)
- Load thumbnail in background

**Phase 2: After 300ms**
- User has stopped navigating
- Load full quality image

**Phase 3: After 5 seconds**
- User is viewing current image
- Preload 10 images forward, 5 backward
- Compute metrics for adjacent images

This ensures:
- ✅ Instant response to navigation
- ✅ No blocking during rapid key presses
- ✅ Full quality available quickly
- ✅ Smooth experience when browsing sequentially

### Synchronized Viewing

**Sync Lock Enabled (Default):**
- Zoom on one image affects both
- Pan on one image affects both
- Perfect alignment for comparison

**Sync Lock Disabled:**
- Independent zoom levels
- Independent pan positions
- Useful for inspecting different details

Toggle with checkbox or press `L` key.

### Resolution Management

The application detects and offers all available resolutions:
- Original image dimensions
- Scaled versions if applicable
- Select from dropdown to change both images
- Maintains aspect ratio

### Fullscreen Mode

Press `F` to enter fullscreen:
- Hides all controls and status bar
- Maximum screen space for images
- All keyboard shortcuts still work
- Press `F` again to exit

Perfect for presentations or detailed analysis.

## 🐛 Troubleshooting

### Images Not Loading

**Problem**: Placeholder stays, images don't load

**Solutions**:
1. Check file permissions
2. Verify image formats are supported
3. Check logs in `image_comparator.log`
4. Try smaller images to rule out memory issues

### Slow Performance

**Problem**: Application feels sluggish

**Solutions**:
1. Reduce `MAX_THREAD_COUNT` in `constants.py`
2. Increase `NAVIGATION_DELAY_MS` for slower systems
3. Decrease `MAX_PRELOAD_FORWARD/BACKWARD`
4. Close other applications to free memory

### Metrics Not Showing

**Problem**: "Computing metrics..." stays forever

**Solutions**:
1. Check if `image_metrics.py` dependencies are installed
2. Verify images are valid and readable
3. Check logs for errors
4. Try smaller/simpler images

### Out of Memory

**Problem**: Application crashes with large image sets

**Solutions**:
1. Decrease `MAX_CACHE_DISTANCE` in `constants.py`
2. Reduce `THUMBNAIL_SIZE` to save memory
3. Limit preloading: reduce `MAX_PRELOAD_FORWARD/BACKWARD`
4. Process images in smaller batches

### Sync Not Working

**Problem**: Zoom/pan not synchronized

**Solutions**:
1. Check "Sync Lock" checkbox is enabled
2. Press `L` key to toggle sync
3. Restart application if stuck
4. Check logs for synchronization errors

## 💡 Tips & Best Practices

### For Best Performance
- Use images of similar sizes in both folders
- Keep image resolution reasonable (< 8K)
- Close application when not in use to free memory
- Use SSD for faster loading

### For Accurate Comparison
- Ensure images are properly aligned/matched
- Use same format in both folders when possible
- Enable sync lock for side-by-side analysis
- Use fullscreen mode to eliminate distractions

### For Large Image Sets
- Use direct page jump instead of scrolling
- Utilize Page Up/Down for batch navigation
- Monitor cache statistics to understand memory usage
- Consider processing in multiple sessions

### For Quality Analysis
- Pay attention to all metrics, not just one
- SSIM is usually most reliable for perceptual quality
- PSNR can be misleading for heavy compression
- Visual inspection is still important


### Changes & Enhancements

This fork includes significant enhancements:
- Modular architecture with separate concerns
- Advanced caching system with smart eviction
- Multi-threaded loading with configurable workers
- Comprehensive image metrics (PSNR, SSIM, Sharpness, Noise)
- Animated placeholders (loading/error states)
- Enhanced navigation with direct page jumps
- Fullscreen mode
- Sync lock toggle
- Cache statistics monitoring
- File size display
- PyInstaller packaging support
- Extensive documentation

## 📄 License

This project is licensed under the license GPL 3.0 later. see LICENCE file in  project root for details
## 🔮 Future Enhancements

Potential features for future releases:

- [ ] Difference highlighting (pixel-level diff)
- [ ] Export comparison reports (PDF/HTML)
- [ ] Batch metric export (CSV)
- [ ] Custom metric plugins
- [ ] Image annotation tools
- [ ] Side-by-side histogram comparison
- [ ] Zoom-to-region comparison
- [ ] Video frame comparison
- [ ] Network folder support
- [ ] Cloud storage integration

## 📞 Support

- **Issues**: Report bugs on GitHub Issues
- **Discussions**: Ask questions on GitHub Discussions
- **Email**: huyiamunknownguy@gmail.com

## 🌟 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

Please follow the existing code style and add documentation for new features.

## 📚 Additional Resources

- [PyQt5 Documentation](https://www.riverbankcomputing.com/static/Docs/PyQt5/)
- [Image Quality Metrics Overview](https://en.wikipedia.org/wiki/Image_quality)
- [SSIM Explained](https://en.wikipedia.org/wiki/Structural_similarity)
- [PyInstaller Documentation](https://pyinstaller.readthedocs.io/)

---

**Made with ❤️ by [Manga-Knights]

*Based on [hawier-dev's image_comparator](https://github.com/hawier-dev/image_comparator)*