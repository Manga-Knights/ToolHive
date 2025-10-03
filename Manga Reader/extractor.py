import os
import zipfile
import fitz  # PyMuPDF
import shutil
import subprocess
from natsort import natsorted
from collections import defaultdict
import tempfile

from launcherlib.prints import print_success, print_warning, print_error, print_info, print_menu_header, print_menu_option
from launcherlib.dialogs import ask_directory

IMAGE_EXTS = ('.jpg', '.jpeg', '.png', '.webp', '.bmp', '.gif', '.tif', '.tiff')

def get_unique_path(output_dir, filename):
    """Return a unique path if filename already exists in output_dir."""
    base, ext = os.path.splitext(filename)
    candidate = os.path.join(output_dir, filename)
    counter = 1
    while os.path.exists(candidate):
        candidate = os.path.join(output_dir, f"{base}_{counter}{ext}")
        counter += 1
    return candidate

def detect_collisions(archives):
    groups = defaultdict(list)
    for path in archives:
        base = os.path.splitext(os.path.basename(path))[0]
        groups[(os.path.dirname(path), base)].append(path)
    # keep only groups with >1
    return {k: v for k, v in groups.items() if len(v) > 1}

def find_archives(master_folder):
    supported_exts = {'.cbz', '.pdf', '.rar'}
    archives = []
    extensions_found = set()

    for root, _, files in os.walk(master_folder):
        for f in files:
            ext = os.path.splitext(f)[1].lower()
            if ext in supported_exts:
                full_path = os.path.join(root, f)
                archives.append(full_path)
                extensions_found.add(ext)

    return archives, extensions_found

def extract_cbz(file_path, output_dir):
    with zipfile.ZipFile(file_path, 'r') as zip_ref:
        for name in zip_ref.namelist():
            if name.lower().endswith(IMAGE_EXTS) and not name.endswith('/'):
                # preserve folder structure inside output_dir
                rel_path = os.path.normpath(name)
                original = os.path.join(output_dir, rel_path)
                unique = get_unique_path(output_dir, rel_path)

                if unique != original:
                    print_warning(f"Duplicate filename sanitized: {rel_path}")

                os.makedirs(os.path.dirname(unique), exist_ok=True)

                try:
                    with zip_ref.open(name) as src, open(unique, "wb") as out_file:
                        shutil.copyfileobj(src, out_file)
                except Exception as e:
                    print_error(
                        f"Failed to extract {rel_path} from {os.path.basename(file_path)}: {e}"
                    )

def extract_pdf(file_path, output_dir):
    try:
        doc = fitz.open(file_path)
        total_pages = len(doc)
        pages_with_images = 0
        img_index = 0

        # Pass 1: check distribution
        for i in range(total_pages):
            if doc.get_page_images(i):
                pages_with_images += 1

        # If not all pages have images → ask user
        if pages_with_images < total_pages:
            print_warning(
                f"PDF {os.path.basename(file_path)} contains {total_pages} pages "
                f"but only {pages_with_images} pages with embedded images."
            )
            print_menu_header("Choose extraction mode:")
            print_menu_option("1", "Extract embedded images only")
            print_menu_option("2", "Render all pages as images.(⚠️ Some embedded images may not extract due to PDF encoding.)")
            choice = input("Select (1/2): ").strip()
        else:
            choice = "1"

        if choice == "1":
            for i in range(total_pages):
                for img in doc.get_page_images(i):
                    xref = img[0]
                    base_image = doc.extract_image(xref)
                    image_bytes = base_image["image"]
                    ext = base_image["ext"]
                    filename = f"{img_index:03d}.{ext}"
                    out_path = get_unique_path(output_dir, filename)
                    unique_path = get_unique_path(output_dir, filename)
                    if unique_path != os.path.join(output_dir, filename):
                        print_warning(f"Duplicate filename sanitized: {filename}")
                    out_path = unique_path
                    with open(out_path, "wb") as f:
                        f.write(image_bytes)
                    img_index += 1
            if img_index == 0:
                print_warning(f"No embedded images found in {os.path.basename(file_path)}")
            else:
                print_success(f"Extracted {img_index} images from {os.path.basename(file_path)}")

        elif choice == "2":
            for i, page in enumerate(doc):
                pix = page.get_pixmap()
                filename = f"{i:03d}.png"
                out_path = get_unique_path(output_dir, filename)
                unique_path = get_unique_path(output_dir, filename)
                if unique_path != os.path.join(output_dir, filename):
                    print_warning(f"Duplicate filename sanitized: {filename}")
                out_path = unique_path
                pix.save(out_path)
            print_success(f"Rendered {total_pages} pages as images in {os.path.basename(file_path)}")

        doc.close()
        return True

    except Exception as e:
        print_error(f"Failed to extract PDF {os.path.basename(file_path)}: {e}")
        return False

def extract_rar(file_path, output_dir):
    exe = os.path.join(os.path.dirname(__file__), "UnRAR.exe")
    if not os.path.exists(exe):
        print_error(f"Missing UnRAR.exe in {os.path.dirname(__file__)}")
        return False

    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            # first test if archive requires a password
            test_cmd = [exe, "t", "-y", "-p-", file_path]
            test = subprocess.run(
                test_cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
            )
            needs_password = (
                test.returncode in (1, 3)
                or b"password" in test.stdout.lower()
                or b"password" in test.stderr.lower()
                or b"crc failed" in test.stdout.lower()
                or b"crc failed" in test.stderr.lower()
            )

            while True:
                cmd = [exe, "x", "-y"]

                if needs_password:
                    pw = input(f"Password required for {os.path.basename(file_path)}: ").strip()
                    cmd.append(f"-p{pw}")
                else:
                    cmd.append("-p-")

                cmd.extend([file_path, temp_dir + os.sep])

                result = subprocess.run(
                    cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE
                )

                # check if extraction succeeded
                if result.returncode == 0:
                    break

                if needs_password and (
                    result.returncode in (1, 3)
                    or b"password" in result.stdout.lower()
                    or b"password" in result.stderr.lower()
                    or b"crc failed" in result.stdout.lower()
                    or b"crc failed" in result.stderr.lower()
                ):
                    print_warning("Incorrect password.")
                    retry = input("Retry password? (y to retry / s to skip): ").strip().lower()
                    if retry == "y":
                        continue
                    else:
                        print_warning(f"Skipping {os.path.basename(file_path)}")
                        return False
                else:
                    print_error(f"UnRAR failed on {os.path.basename(file_path)}")
                    return False

            # move files safely into output_dir, preserving structure
            for root, _, files in os.walk(temp_dir):
                for f in files:
                    src = os.path.join(root, f)
                    rel_path = os.path.relpath(src, temp_dir)
                    original = os.path.join(output_dir, rel_path)
                    unique = get_unique_path(output_dir, rel_path)

                    if unique != original:
                        print_warning(f"Duplicate filename sanitized: {rel_path}")

                    os.makedirs(os.path.dirname(unique), exist_ok=True)
                    shutil.move(src, unique)

        return True
    except Exception as e:
        print_error(f"Failed to extract RAR {file_path}: {e}")
        return False

def safe_folder_name(path):
    return os.path.splitext(os.path.basename(path))[0]

def main():
    master_folder = ask_directory("Select Master Folder Containing CBZ/PDF/RAR")
    if not master_folder:
        print_warning("No folder selected.")
        return 1

    archives, ext_types = find_archives(master_folder)

    if not archives:
        print_warning("No supported files found.")
        return 1

    if len(ext_types) > 1:
        print_warning(f"Mixed formats detected: {', '.join(ext_types)}")
        choice = input("Proceed anyway? (y/n): ").strip().lower()
        if choice != 'y':
            print_error("Aborted.")
            return 1
            
    # 👉 Detect collisions once, before extraction
    collisions = detect_collisions(archives)      

    print_info(f"\n📦 Found {len(archives)} archive(s). Beginning extraction...\n")

    for path in natsorted(archives):
        name = safe_folder_name(path)
        dest_folder = os.path.join(os.path.dirname(path), name)

        if not os.path.exists(dest_folder):
            os.makedirs(dest_folder)

        ext = os.path.splitext(path)[1].lower()
        print(f"📁 Extracting: {os.path.basename(path)}")

        try:
            if ext == '.cbz':
                extract_cbz(path, dest_folder)
            elif ext == '.pdf':
                success = extract_pdf(path, dest_folder)
                if not success:
                    print_error(f"Failed to extract {os.path.basename(path)}")
                    continue
            elif ext == '.rar':
                success = extract_rar(path, dest_folder)
                if not success:
                    print_error(f"Failed to extract {os.path.basename(path)}")
                    continue
            else:
                print_warning(f"Unsupported format: {path}")
                continue

        except Exception as e:
            print_error(f"Extraction failed for {os.path.basename(path)}: {e}")
            continue
    print_success("\nAll done. Extracted folders are next to their respective archive files.")
    return 0

if __name__ == "__main__":
    try:
        exit_code = main()
        exit(exit_code)
    except KeyboardInterrupt:
        print_warning("\n👋 Interrupted.")
        exit(1)
