from flask import Flask, request, jsonify
from models.ocr import run_ocr  
from models.clova import CompletionExecutor 

app = Flask(__name__)

@app.route('/categories', methods=['POST'])
def process_poster():
    try:
        data = request.get_json()

        image_url = data.get('image_url', '')

        if not image_url:
            return jsonify({"error": "No image_url provided"}), 400

        # 1. OCR로 텍스트 추출
        ocr_result = run_ocr(image_url)
        extracted_text = ocr_result.get('extracted_text', '')

        if not extracted_text:
            return jsonify({"error": "No text extracted from image"}), 400

        # 2. 추출된 내용 Clova API로 분석
        completion_executor = CompletionExecutor()
        clova_result = completion_executor.execute(extracted_text)

        # 카테고리 반환
        return jsonify({"clova_response": clova_result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
