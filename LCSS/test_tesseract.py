import pytesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'  # Update for your OS
print("Tesseract Version:", pytesseract.get_tesseract_version())
