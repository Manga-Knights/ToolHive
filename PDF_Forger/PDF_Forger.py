import os
import re
import sys
import math
from io import BytesIO
from tqdm import tqdm
from natsort import natsorted
from PyPDF2 import PdfMerger
import img2pdf
from PIL import Image, ImageDraw
import pytesseract
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
from launcherlib import (
    ask_directory,
    ask_file,
    print_success,
    print_warning,
    print_error,
    print_info,
    print_menu_option,
    ask_yes_no,
    ask_choice,
    ask_float,
)
from concurrent.futures import ProcessPoolExecutor, as_completed
from functools import partial
MAX_WORKERS = 3  # Restrict the number of concurrent workers
IMAGE_EXTS = (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")

import tempfile
import atexit
import os
import sys
import signal

# Keep track of temp files in a set to avoid duplicates
_temp_files = set()

def create_temp_file(suffix="", prefix="tmp", dir=None):
    tf = tempfile.NamedTemporaryFile(delete=False, suffix=suffix, prefix=prefix, dir=dir)
    tf.close()  # Close immediately; user can open later
    _temp_files.add(tf.name)
    return tf.name

def cleanup_temp_files():
    for fpath in list(_temp_files):
        try:
            if os.path.exists(fpath):
                os.remove(fpath)
        except Exception:
            pass
        finally:
            _temp_files.discard(fpath)  # Always discard, even if deletion failed

def _cleanup_and_exit(signum=None, frame=None):
    cleanup_temp_files()
    sys.exit(0)

# Normal exit
atexit.register(cleanup_temp_files)

# Handle termination signals
signal.signal(signal.SIGINT, _cleanup_and_exit)
signal.signal(signal.SIGTERM, _cleanup_and_exit)


paddle_model = None

# Map Tesseract language codes to PaddleOCR codes
PADDLE_LANG_MAP = {
    "eng": "en",
    "jpn": "japan",
    # extend as needed
}

def _map_paddle_langs(tess_langs: str):
    parts = tess_langs.split("+")
    mapped = [PADDLE_LANG_MAP.get(p, p) for p in parts if p in PADDLE_LANG_MAP]
    if not mapped:
        return "en"
    if len(mapped) > 1:
        print_warning(f"PaddleOCR supports only one language. Using '{mapped[0]}' from {tess_langs}")
    return mapped[0]

def load_paddleocr(tess_langs=None):
    """Load PaddleOCR only once, when needed."""
    global paddle_model
    if paddle_model is not None:
        return True  # already loaded

    if not tess_langs:
        tess_langs = DEFAULT_LANGUAGES

    print_info("Loading PaddleOCR (this may take a few seconds)...")
    try:
        os.environ["FLAGS_log_level"] = "3"
        from paddleocr import PaddleOCR
        import contextlib
        from io import StringIO

        paddle_lang = _map_paddle_langs(tess_langs)

        with contextlib.redirect_stdout(StringIO()), contextlib.redirect_stderr(StringIO()):
            paddle_model = PaddleOCR(use_textline_orientation=True, lang=paddle_lang)

        print_success(f"PaddleOCR initialized successfully with lang={paddle_lang}.")
        return True
    except Exception as e:
        print_error(f"Failed to initialize PaddleOCR: {e}")
        return False

# ---- CONFIG ----
zoom = 0.88
offset_y = 33
LOG_FILE = "log.txt"
DEFAULT_LANGUAGES = "eng+jpn"
DEFAULT_THRESHOLDS = {"paddle": 0.6, "tesseract": 60}
PSM_OPTIONS = {
    "1": ("Automatic layout", "--psm 1"),
    "2": ("Manga-style bubbles", "--psm 6"),
    "3": ("Sparse text", "--psm 11"),
    "4": ("Columns (newspapers)", "--psm 4"),
    "5": ("Auto detect", ""),
}


# ---- UTILS ----
def sanitize_filename(name):
    valid = re.sub(r'[\\/:"*?<>|]+', "", name)
    return valid if valid.strip() else "pdf"

def sorted_images(folder):
    images = natsorted(
        f
        for f in os.listdir(folder)
        if f.lower().endswith(
            (".jpg", ".jpeg", ".png", ".bmp", ".webp", ".tif", ".tiff")
        )
    )
    if not images:
        print_warning(f"No images found in folder: {folder}")
    else:
        print_info(f"Found {len(images)} images in folder: {folder}")
    return images


# ---- FOLDER SELECTION ----
def select_folder():
    folder = ask_directory("Select folder containing images")
    if not folder:
        sys.exit(1)
    return folder

# ---- OCR FUNCTIONS ----
def perform_tesseract_ocr(img_path, lang, psm_args):
    try:
        with Image.open(img_path) as im:
            image = im.convert("RGB")
        config = f"-l {lang}"
        if psm_args:
            config += f" {psm_args}"
        data = pytesseract.image_to_data(
            image, config=config, output_type=pytesseract.Output.DICT
        )

        text_items = []
        for i in range(len(data["text"])):
            try:
                conf = float(data["conf"][i])
            except ValueError:
                conf = -1.0
            txt = data["text"][i].strip()
            if txt:
                text_items.append((txt, conf))

        pdf_data = pytesseract.image_to_pdf_or_hocr(
            image, config=config, extension="pdf"
        )
        print_success(f"OCR successful: {os.path.basename(img_path)}")
        return pdf_data, text_items

    except Exception as e:
        print_error(f"Tesseract OCR failed: {os.path.basename(img_path)} → {e}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[TESS] {img_path} → {e}\n")
        return None, []

def perform_paddleocr_overlay_from_result(img_path, result, visible=True, threshold=0.6):
    """
    Create a PDF overlay from a precomputed PaddleOCR result.
    """
    try:
        boxes = result.get("dt_polys", [])
        texts = result.get("rec_texts", [])
        confs = result.get("rec_scores", [])
        ocr_img = result.get("doc_preprocessor_res", {}).get("output_img")

        if not boxes or ocr_img is None:
            print_warning(f"No PaddleOCR results for {os.path.basename(img_path)}")
            return None

        img = Image.open(img_path)
        orig_w, orig_h = img.size
        ocr_h, ocr_w = ocr_img.shape[:2]
        x_scale = orig_w / ocr_w
        y_scale = orig_h / ocr_h
        cx = orig_w / 2
        cy = orig_h / 2

        buffer = BytesIO()
        c = canvas.Canvas(buffer, pagesize=(orig_w, orig_h))
        c.drawImage(
            ImageReader(img_path),
            0,
            0,
            width=orig_w,
            height=orig_h,
            preserveAspectRatio=False,
            anchor="c",
        )

        for i, box in enumerate(boxes):
            try:
                conf = confs[i] if i < len(confs) else 0
                text = texts[i] if i < len(texts) else ""
                if conf < threshold or not text:
                    continue

                pts = box.tolist() if hasattr(box, "tolist") else box
                scaled = []
                for x, y in pts:
                    sx = cx + ((x * x_scale - cx) * zoom)
                    sy = orig_h - (cy + ((y * y_scale - cy) * zoom)) + offset_y
                    scaled.append((sx, sy))

                # Draw box if visible
                if visible:
                    c.setStrokeColorRGB(1, 0, 0)
                    c.setLineWidth(0.5)
                    for j in range(4):
                        p1, p2 = scaled[j], scaled[(j + 1) % 4]
                        c.line(p1[0], p1[1], p2[0], p2[1])

                # Calculate angle and font size
                p1, p2, p3, p4 = scaled
                dx, dy = p3[0] - p4[0], p3[1] - p4[1]
                angle = math.degrees(math.atan2(dy, dx))
                height = max(1, math.hypot(p1[0] - p4[0], p1[1] - p4[1]))
                font_size = max(1, min(height * 0.9, 50))  # clamp to avoid reportlab errors

                # Draw text
                if visible:
                    c.saveState()
                    c.translate(p4[0], p4[1])
                    c.rotate(angle)
                    c.setFont("Helvetica", font_size)
                    c.setFillColorRGB(1, 0, 0)
                    c.drawString(0, 0, text)
                    c.restoreState()

            except Exception as e:
                print_warning(f"Paddle box {i} failed on {os.path.basename(img_path)} → {e}")
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[PADDLE] Box {i} → {e}\n")
                continue

        c.save()
        buffer.seek(0)
        print_success(f"PaddleOCR overlay created: {os.path.basename(img_path)}")
        return buffer

    except Exception as e:
        print_error(f"PaddleOCR overlay failed: {os.path.basename(img_path)} → {e}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[PADDLE] {img_path} → {e}\n")
        return None

def perform_image_only_pdf(img_path):
    try:
        with open(img_path, "rb") as f:
            return BytesIO(img2pdf.convert(f))
    except Exception as e:
        print_error(f"IMG2PDF failed: {os.path.basename(img_path)} → {e}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[IMG2PDF] {img_path} → {e}\n")
        return None

def create_pdf_from_folder(folder, lang, psm_args, engine, overlays_visible, threshold):
    images = sorted_images(folder)
    if not images:
        print_warning(f"No images found in folder: {folder}")
        return

    print_info(f"Creating PDF for folder: {os.path.basename(folder)} using {engine}")
    merger = PdfMerger()

    def append_buffer_to_merger(buffer):
        try:
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                tmp_file.write(buffer.read())
                tmp_path = tmp_file.name
            try:
                merger.append(tmp_path)
            finally:
                if os.path.exists(tmp_path):
                    os.remove(tmp_path)
        except Exception as e:
            print_error(f"Failed to append buffer to PDF → {e}")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[PDFMERGE] {folder} → {e}\n")

    if engine == "paddle":
        BATCH_SIZE = 5
        for i in range(0, len(images), BATCH_SIZE):
            batch_imgs = images[i:i+BATCH_SIZE]
            batch_paths = [os.path.join(folder, img) for img in batch_imgs]

            try:
                batch_results = paddle_model.predict(batch_paths)
            except Exception as e:
                print_error(f"PaddleOCR batch failed for images {batch_paths} → {e}")
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[PADDLE_BATCH] {batch_paths} → {e}\n")
                continue

            for img_path, result in zip(batch_paths, batch_results):
                buffer = perform_paddleocr_overlay_from_result(
                    img_path, result, visible=overlays_visible, threshold=threshold
                )
                if buffer:
                    append_buffer_to_merger(buffer)

    else:
        for img in images:
            full_path = os.path.join(folder, img)
            try:
                if engine == "tesseract":
                    if overlays_visible:
                        buffer = generate_tesseract_overlay_pdf(full_path, lang, psm_args)
                        if buffer:
                            append_buffer_to_merger(buffer)
                    else:
                        pdf_data, _ = perform_tesseract_ocr(full_path, lang, psm_args)
                        if pdf_data:
                            append_buffer_to_merger(BytesIO(pdf_data))
                elif engine == "none":
                    buffer = perform_image_only_pdf(full_path)
                    if buffer:
                        append_buffer_to_merger(buffer)
            except Exception as e:
                print_error(f"Failed processing image {full_path} → {e}")
                with open(LOG_FILE, "a", encoding="utf-8") as f:
                    f.write(f"[IMAGE_PROCESS] {full_path} → {e}\n")
                continue

    # Save merged PDF
    if merger.pages:
        base = os.path.basename(folder)
        safe_name = sanitize_filename(base)
        suffix = {
            "tesseract": ".pdf",
            "paddle": "_paddle.pdf",
            "none": "_images.pdf",
        }.get(engine, ".pdf")
        out_path = os.path.join(os.path.dirname(folder), safe_name + suffix)
        try:
            with open(out_path, "wb") as f:
                merger.write(f)
            merger.close()
            print_success(f"PDF created: {out_path}")
        except Exception as e:
            print_error(f"Failed to save PDF {out_path} → {e}")
            merger.close()
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[PDF_SAVE] {out_path} → {e}\n")

# --- Master folder analysis ---
def analyze_master_folder(master_folder):
    """Return list of subfolders containing images."""
    folders_to_process = []
    for root, _, files in os.walk(master_folder):
        if any(f.lower().endswith(IMAGE_EXTS) for f in files):
            folders_to_process.append(root)
    return folders_to_process


# --- Worker for parallel execution ---
def process_folder_worker(args):
    """Worker function for Tesseract/No-OCR PDF creation."""
    folder, lang, psm_args, engine, overlays_visible, threshold = args
    try:
        create_pdf_from_folder(folder, lang, psm_args, engine, overlays_visible, threshold)
        return folder, True
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[WORKER] {folder} → {e}\n")
        return folder, False


# --- Sequential wrapper for single folder ---
def process_subfolder(folder, lang, psm_args, engine, overlays_visible, threshold):
    """Wrapper to process a single folder; returns success flag."""
    try:
        create_pdf_from_folder(folder, lang, psm_args, engine, overlays_visible, threshold)
        return folder, True
    except Exception as e:
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[WORKER] {folder} → {e}\n")
        return folder, False


# --- Parallel runner ---
def run_parallel(master_folder, lang, psm_args, engine, overlays_visible, threshold):
    folders_to_process = analyze_master_folder(master_folder)
    print_info(f"Found {len(folders_to_process)} image folders.")

    if engine == "paddle":
        # PaddleOCR handled sequentially in batch mode
        for folder in tqdm(folders_to_process, desc="Processing (PaddleOCR)"):
            process_subfolder(folder, lang, psm_args, engine, overlays_visible, threshold)

    else:
        # Tesseract / No-OCR: parallel execution
        args_list = [
            (folder, lang, psm_args, engine, overlays_visible, threshold)
            for folder in folders_to_process
        ]

        with ProcessPoolExecutor(max_workers=MAX_WORKERS) as executor:
            futures = {executor.submit(process_folder_worker, args): args[0] for args in args_list}

            for future in tqdm(as_completed(futures), total=len(futures), desc="Processing (Parallel)"):
                folder_done = futures[future]
                try:
                    folder_result, success = future.result()
                    if success:
                        print_success(f"Finished PDF for folder: {folder_done}")
                    else:
                        print_error(f"Worker failed for folder: {folder_done}")
                except Exception as e:
                    print_error(f"Worker exception for folder: {folder_done} → {e}")
                    with open(LOG_FILE, "a", encoding="utf-8") as f:
                        f.write(f"[WORKER_EXC] {folder_done} → {e}\n")

# ---- PREVIEWS ----
def preview_paddle(threshold):
    global paddle_model
    if paddle_model is None:
        print_error("PaddleOCR model not loaded.")
        return "menu"

    while True:
        path = ask_file(title="Select image for preview")
        if not path:
            print_warning("Cancelled.")
            return "menu"

        try:
            result = paddle_model.predict(path)[0]

            # Generate overlay PDF
            buf = perform_paddleocr_overlay_from_result(path, result, visible=True, threshold=threshold)
            if buf:
                preview_file = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                preview_file.write(buf.read())
                preview_file.close()
                os.startfile(preview_file.name)
                _temp_files.add(preview_file.name)  # Track temp file
                print_info(f"Preview saved as {preview_file.name}")

            # Print text with confidence
            texts, confs = result.get("rec_texts", []), result.get("rec_scores", [])
            print_info("\nText preview with confidence:")
            for txt, conf in zip(texts, confs):
                print(f"[{round(conf*100)}%] {txt}")

        except Exception as e:
            print_error(f"PaddleOCR preview failed: {e}")

        response = ask_choice(
            "Preview finished. What do you want to do?",
            {
                "1": "Finalize this engine and proceed",
                "2": "Switch engine",
                "3": "Test another image",
                "4": "Return to home",
            },
            repeat_option="3"
        )

        if response == "3":
            continue
        else:
            return response

def preview_tesseract(lang, psm_args, overlays_visible):
    while True:
        path = ask_file(title="Select image for preview")
        if not path:
            print_warning("Cancelled.")
            return "menu"

        text_items = []

        try:
            if overlays_visible:
                buffer = generate_tesseract_overlay_pdf(path, lang, psm_args)
                if buffer:
                    preview_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    preview_pdf.write(buffer.read())
                    preview_pdf.close()
                    os.startfile(preview_pdf.name)
                    _temp_files.add(preview_pdf.name)  # Track temp file
                    print_info(f"Preview saved as {preview_pdf.name}")

                _, text_items = perform_tesseract_ocr(path, lang, psm_args)
            else:
                pdf_data, text_items = perform_tesseract_ocr(path, lang, psm_args)
                if pdf_data:
                    preview_pdf = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
                    preview_pdf.write(pdf_data)
                    preview_pdf.close()
                    os.startfile(preview_pdf.name)
                    _temp_files.add(preview_pdf.name)  # Track temp file
                    print_info(f"Preview saved as {preview_pdf.name}")

        except Exception as e:
            print_error(f"Tesseract preview failed: {e}")
            with open(LOG_FILE, "a", encoding="utf-8") as f:
                f.write(f"[PREVIEW_TESS] {path} → {e}\n")

        if text_items:
            print_info("\nText preview with confidence:")
            for txt, conf in text_items:
                print(f"[{conf}%] {txt}")

        response = ask_choice(
            "Preview finished. What do you want to do?",
            {
                "1": "Finalize this engine and proceed",
                "2": "Switch engine",
                "3": "Test another image",
                "4": "Return to home",
            },
            repeat_option="3"
        )

        if response == "3":
            continue
        else:
            return response

# ---- MAIN ----
def run():
    while True:
        # ---- OCR CONFIGURATION ----
        use_ocr = ask_yes_no("Do you want to OCR your PDF?")
        lang, psm_args, threshold = None, None, None

        if use_ocr == "no":
            selected_engine = "none"
            overlays_visible = False
        else:
            engine_choice = ask_choice(
                "Choose OCR Engine:",
                {"1": "PaddleOCR", "2": "Tesseract", "3": "Return to home"}
            )
            if engine_choice == "3":
                continue  # return to home

            # PaddleOCR
            if engine_choice == "1":
                selected_engine = "paddle"

                # Lazy-load PaddleOCR
                if not load_paddleocr():
                    continue  # restart loop if loading fails

                threshold = ask_float("Confidence threshold?", DEFAULT_THRESHOLDS["paddle"])

                if ask_yes_no("Preview this OCR output?") == "yes":
                    action = preview_paddle(threshold)
                    if action in ["2", "4", "menu"]:
                        continue

                overlays_visible = ask_yes_no(
                    "Do you want OCR overlays (text + rectangles) to be visible?"
                ) == "yes"

            # Tesseract
            elif engine_choice == "2":
                selected_engine = "tesseract"
                overlays_visible = False
                pytesseract.pytesseract.tesseract_cmd = "tesseract"

                lang_input = input(f"Enter Tesseract languages (default: {DEFAULT_LANGUAGES}): ").strip()
                lang = lang_input or DEFAULT_LANGUAGES

                psm_key = ask_choice(
                    "Select Page Segmentation Mode (PSM):",
                    {k: desc for k, (desc, _) in PSM_OPTIONS.items()}
                )
                psm_args = PSM_OPTIONS[psm_key][1]

                if ask_yes_no("Preview this OCR output?") == "yes":
                    preview_overlays_visible = ask_yes_no(
                        "Do you want OCR overlays to be visible in the preview?"
                    ) == "yes"
                    print_info("\nNote: Confidence threshold does not affect final Tesseract PDF.")
                    preview_tesseract(lang, psm_args, preview_overlays_visible)

                overlays_visible = ask_yes_no(
                    "Do you want OCR overlays (text + rectangles) to be visible?"
                ) == "yes"

        # ---- CONFIRM SETTINGS ----
        if ask_yes_no("Proceed with current settings?") == "no":
            continue  # restart loop to reconfigure

        # ---- MASTER FOLDER SELECTION ----
        master_folder = ask_directory("Select Master Folder")
        if not master_folder:
            print_error("Cancelled.")
            continue
        master_folder = os.path.abspath(master_folder)

        # ---- SUBFOLDER COLLECTION ----
        subfolders = [
            root for root, _, files in os.walk(master_folder)
            if any(f.lower().endswith(IMAGE_EXTS) for f in files)
        ]

        if not subfolders:
            print_error("No subfolders with images found.")
            continue

        print_info(f"Found {len(subfolders)} image folders.")

        # ---- PDF CREATION ----
        run_parallel(master_folder, lang, psm_args, selected_engine, overlays_visible, threshold)

        print_success("\nDone. All PDFs saved to the master folder.")
        print_info(f"Check '{LOG_FILE}' for any warnings or errors.")

        # ---- NEXT ACTION ----
        choice = ask_choice(
            "\nWhat do you want to do next?",
            {"1": "🔁 Return to home", "2": "❌ Exit"}
        )
        if choice == "1":
            continue  # restart loop → return to home
        elif choice == "2":
            sys.exit()


def generate_tesseract_overlay_pdf(img_path, lang, psm_args):
    try:
        with Image.open(img_path) as image:
            image = image.convert("RGB")
            draw = ImageDraw.Draw(image)

        config = f"-l {lang} {psm_args or ''}"
        data = pytesseract.image_to_data(
            image, config=config, output_type=pytesseract.Output.DICT
        )

        for i in range(len(data["text"])):
            txt = data["text"][i].strip()
            try:
                conf = float(data["conf"][i])
            except ValueError:
                conf = -1.0
            if not txt:
                continue

            x, y, w, h = (
                int(data["left"][i]),
                int(data["top"][i]),
                int(data["width"][i]),
                int(data["height"][i]),
            )

            draw.rectangle([(x, y), (x + w, y + h)], outline="red", width=1)
            text_y = max(y - 10, 0)
            draw.text((x, text_y), txt, fill="red")

        image_bytes = BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        buffer = BytesIO()
        buffer.write(img2pdf.convert(image_bytes))
        buffer.seek(0)
        return buffer

    except Exception as e:
        print_error(f"Tesseract overlay failed: {os.path.basename(img_path)} → {e}")
        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"[TESS-OVERLAY] {img_path} → {e}\n")
        return None


if __name__ == "__main__":
    run()
