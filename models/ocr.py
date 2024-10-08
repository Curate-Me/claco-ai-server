import requests
from PIL import Image
import pytesseract
from io import BytesIO
import re
import json
import sys

def run_ocr(image_url):
    try:
        response = requests.get(image_url)
        response.raise_for_status()

        img = Image.open(BytesIO(response.content))

        text = pytesseract.image_to_string(img, lang="kor")

        cleaned_text = re.sub(r'\s+', '', text)

        # Return a dictionary instead of a JSON string
        return {"extracted_text": cleaned_text}

    except Exception as e:
        # Return a dictionary with error message
        return {"error": str(e)}

if __name__ == '__main__':
    image_url = sys.argv[1]
    print(run_ocr(image_url))
