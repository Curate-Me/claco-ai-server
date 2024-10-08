import requests
from PIL import Image
import pytesseract
from io import BytesIO
import re

# 이미지 URL
image_url = "http://www.kopis.or.kr/upload/pfmIntroImage/PF_PF250352_241002_0320530.jpg"

# 이미지 다운로드
response = requests.get(image_url)
img = Image.open(BytesIO(response.content))

text = pytesseract.image_to_string(img, lang="kor")
cleaned_text = re.sub(r'\s+', '', text)

print(cleaned_text)