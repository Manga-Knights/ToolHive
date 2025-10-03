=========================
🧾 README — PDF_Forger
=========================

This is a lightweight, folder-based OCR + PDF tool that:
✔️ Supports both **Tesseract** and **PaddleOCR**  
✔️ Accepts nested image folders  
✔️ Outputs merged PDFs (with or without OCR)  
✔️ Provides red text + box overlays when needed  
✔️ Allows invisible/searchable PDF text layer  
✔️ Offers preview with confidence stats before committing  
✔️ Also works in image-only mode (no OCR at all)

––––––––––––––––––––––––––––––––––––––––––––––––––––––––
🚀 HOW TO USE
––––––––––––––––––––––––––––––––––––––––––––––––––––––––

1. 🐍 Run the script using:
       python PDF_Forger.py

2. ❓ It will ask if you want to OCR your PDFs:
   - ❌ "No" → plain image-to-PDF conversion
   - ✅ "Yes" → choose between:
     - PaddleOCR (modern, better filtering)
     - Tesseract (faster, classic, built-in invisible layer)

3. 🖼️ It will ask if you want to *preview* a sample image first:
   - This helps check OCR quality and formatting

4. 👁️ For preview: you’ll be asked if overlays (red text + boxes) should be visible
   - You’ll then see the preview PDF
   - The console will display all detected text along with confidence values

5. ✅ If you proceed with the engine:
   - It will ask **again** whether the final output should have overlays visible

6. 📂 You will be prompted to select a *master folder*:
   - All subfolders containing images will be processed automatically

7. 📄 Output PDFs will be saved beside each image folder
   - Warnings (if any) are logged to `log.txt`

––––––––––––––––––––––––––––––––––––––––––––––––––––––––
🎛️ KEY FEATURES
––––––––––––––––––––––––––––––––––––––––––––––––––––––––

- **PaddleOCR**:
  - Confidence-based filtering works
  - Overlay visibility is user-selectable
  - Prints [confidence%] next to each line of detected text

- **Tesseract**:
  - Built-in invisible text layer (searchable PDF)
  - Confidence filtering is **not applied** to final output
  - But text + [confidence%] shown in console during preview
  - Optional Pillow-drawn overlay (if enabled)

- **No OCR mode**:
  - Quickly merges image folders to PDF with perfect visual fidelity

––––––––––––––––––––––––––––––––––––––––––––––––––––––––
🧱 DEPENDENCIES
––––––––––––––––––––––––––––––––––––––––––––––––––––––––

This script requires:

- Pillow==11.3.0  
- tqdm==4.67.1  
- natsort==8.4.0  
- PyPDF2==3.0.1  
- reportlab==4.4.3  
- pytesseract==0.3.13  
- paddleocr==3.2.0.dev23  
- paddlepaddle==3.1.0  
- img2pdf==0.5.1  

📦 To install everything reliably, run the bundled **dependency_check.py** script.

⚠️ We pin specific versions because newer package releases may break PDF formatting, OCR return formats, or overlay logic. Please install the exact versions for reliable results.

––––––––––––––––––––––––––––––––––––––––––––––––––––––––
⚠️ LIMITATIONS
––––––––––––––––––––––––––––––––––––––––––––––––––––––––

⚠️ OCR ACCURACY VARIES GREATLY

- Manga, handwritten notes, or curved layouts may yield poor results
- Tesseract does not allow reliable filtering of low-confidence words in the PDF
- Overlay alignment may be off slightly (especially in Paddle mode)

📌 This tool is best used as a lightweight converter for:
- Scanned image folders to searchable PDFs
- Image-only PDFs with excellent layout fidelity

💡 For serious OCR extraction, consider external tools like ABBYY, Google Cloud Vision, or document-specific fine-tuned models.

––––––––––––––––––––––––––––––––––––––––––––––––––––––––
💬 SUPPORT
––––––––––––––––––––––––––––––––––––––––––––––––––––––––

If you encounter issues, just reopen the `.py` script — everything is editable and clearly labeled.

No bloated config files. No compiled binaries. Fully yours to tweak.
