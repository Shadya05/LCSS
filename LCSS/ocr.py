import pytesseract
from PIL import Image
import re

FIELD_LABELS = {
    'owner_name': ['owner name', 'owner', 'name of owner', 'owner of land'],
    'survey_number': ['survey number', 'survey no'],
    'land_area': ['land area', 'area', 'extent'],
    'compensation_amount': ['compensation', 'amount', 'payment'],
    'date': ['date', 'issued on', 'notice date'],
    'register_number': ['register number', 'reg no', 'registration no'],
    'village': ['village', 'place'],
    'taluk': ['taluk', 'taluka'],
    'district': ['district', 'dist']
}

def extract_text_from_image(image_path):
    img = Image.open(image_path)
    text = pytesseract.image_to_string(img)
    return text

def clean_value(value):
    if not value:
        return ''
    value = value.strip()
    value = re.sub(r'[^a-zA-Z0-9\s.-]', '', value)
    return value

def extract_fields(text):
    lines = text.lower().split('\n')
    extracted = {}
    for key, labels in FIELD_LABELS.items():
        for line in lines:
            for label in labels:
                if label in line:
                    pattern = re.compile(re.escape(label) + r'[:\-\s]*([\w\s.,/-]+)')
                    match = pattern.search(line)
                    if match:
                        value = match.group(1)
                        extracted[key] = clean_value(value)
    return extracted
