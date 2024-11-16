import requests
from PIL import Image
import pytesseract
from io import BytesIO
import re
import sys

def run_ocr(image_url):
    try:
        # 이미지 URL로부터 요청
        response = requests.get(image_url)
        response.raise_for_status()

        # 이미지를 PIL로 열기
        img = Image.open(BytesIO(response.content))

        # Tesseract OCR 실행
        text = pytesseract.image_to_string(img, lang="kor")

        # 텍스트 정리 (공백 제거)
        cleaned_text = re.sub(r'\s+', '', text)
        print("Extracted Text:", cleaned_text)  

        return {"extracted_text": cleaned_text}

    except requests.exceptions.RequestException as req_err:
        print(f"[ERROR] Image URL Request Failed: {req_err}")  
        return {"error": str(req_err)}

    except pytesseract.TesseractError as tess_err:
        print(f"[ERROR] Tesseract OCR Error: {tess_err}")  
        return {"error": str(tess_err)}

    except IOError as io_err:
        print(f"[ERROR] Image Processing Failed: {io_err}")  
        return {"error": str(io_err)}

    except Exception as e:
        print(f"[ERROR] Unexpected Error: {e}")  
        return {"error": str(e)}

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("[USAGE] python script.py <image_url>")
        sys.exit(1)

    image_url = sys.argv[1]
    result = run_ocr(image_url)
    print(result)
