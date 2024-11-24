from flask import Flask, request, jsonify
from models.ocr import run_ocr  
from models.clova import CompletionExecutor 
from models.userbased import recommend_similar_concerts_user, recommend_similar_users
from models.itembased import recommend_similar_concerts_item
from services.UserService import update_user_preferences
from infra.s3 import upload_poster_to_s3
import os
import requests
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

'''
    Request: Spring Batch Server
'''
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
    

'''
    Request: Spring Batch Server
'''
@app.route('/summaries', methods=['POST'])
def process_poster_summary():
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
        clova_result = completion_executor.execute_summary(extracted_text)

        # 요약 반환
        return jsonify({"clova_response": clova_result})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


'''
    Request: Spring Main Server
    추천 시스템1: 유저가 좋아할만한 공연 추천
'''
@app.route('/recommendations/users/<userId>/<topn>', methods=['GET'])
def get_recommendations_users(userId, topn):
    try:
        # 추천 결과 가져오기
        recommended_concerts = recommend_similar_concerts_user(userId, topn)

        # 추천 결과를 JSON으로 반환
        return jsonify({"recommendations": recommended_concerts})

    except Exception as e:
        app.logger.error(f"Error in get_recommendations: {e}", exc_info=True)

        return jsonify({"error": str(e)}), 500
    
'''
    Request: Spring Main Server
    추천 시스템2: 유저가 좋아요한 공연과 유사한 공연 추천
'''
@app.route('/recommendations/items/<concertId>/<topn>', methods=['GET'])
def get_recommendations_items(concertId, topn):
    try:
        # 추천 결과 가져오기
        recommended_concerts = recommend_similar_concerts_item(concertId,topn)

        # 추천 결과를 JSON으로 반환
        return jsonify({"recommendations": recommended_concerts})

    except Exception as e:
        app.logger.error(f"Error in get_recommendations: {e}", exc_info=True)

        return jsonify({"error": str(e)}), 500

'''
    Request: Spring Main Server
    추천 시스템3: 유저가 좋아할만한 공연 추천
'''
@app.route('/recommendations/clacobooks/<userId>', methods=['GET'])
def get_recommendations_clacobooks(userId):
    try:
        # 추천 결과 가져오기
        recommended_concerts = recommend_similar_users(userId)

        # 추천 결과를 JSON으로 반환
        return jsonify({"recommendations": recommended_concerts})

    except Exception as e:
        app.logger.error(f"Error in get_recommendations: {e}", exc_info=True)

        return jsonify({"error": str(e)}), 500
    
'''
    Request: Spring Main Server
    유저 취향 csv 파일 등록
'''
@app.route('/users/preferences', methods=['POST'])
def post_preferences():
    try:
        data = request.get_json()

        user_id = data.get("userId")
        preferences = data.get("preferences")

        if not user_id or not preferences:
            return jsonify({"error": "userId and preferences are required"}), 400

        response = update_user_preferences(user_id, preferences)

        if "error" in response:
            return jsonify(response), 404  
        
        return jsonify(response), 201

    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/download/posters', methods=['POST'])
def download_and_upload_image():
    try:
        # 요청 데이터 가져오기
        data = request.get_json()
        image_url = data.get('image_url')
        bucket_name = 'claco-bucket'
        folder_name = 'posters'

        if not image_url or not bucket_name:
            return jsonify({"error": "image_url and bucket_name are required"}), 400

        # 이미지 다운로드
        response = requests.get(image_url)
        response.raise_for_status()  # 상태 코드 확인

        # 파일 이름 추출 및 저장
        file_name = image_url.split("/")[-1]
        with open(file_name, 'wb') as file:
            file.write(response.content)

        # S3에 업로드
        s3_url = upload_poster_to_s3(bucket_name, folder_name, file_name)

        if not s3_url:
            return jsonify({"error": "Failed to upload file to S3"}), 500

        if os.path.exists(file_name):
            os.remove(file_name)

        # 결과 반환
        return jsonify({
            "message": "Image successfully uploaded",
            "s3_url": s3_url
        }), 200

    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to download image: {str(e)}"}), 500

    except Exception as e:
        # 오류 메시지를 문자열로 변환
        return jsonify({"error": f"Unexpected error: {str(e)}"}), 500

    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
