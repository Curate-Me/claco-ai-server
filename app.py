from flask import Flask, request, jsonify
from models.ocr import run_ocr  
from models.clova import CompletionExecutor 
from models.userbased import recommend_similar_concerts_user
from models.itembased import recommend_similar_concerts_item
from services.UserService import update_user_preferences


app = Flask(__name__)

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
    Request: Spring Main Server
    유저가 좋아할만한 공연 추천
'''
@app.route('/recommendations/users/<userId>', methods=['GET'])
def get_recommendations_users(userId):
    try:
        # 추천 결과 가져오기
        recommended_concerts = recommend_similar_concerts_user(userId)

        # 추천 결과를 JSON으로 반환
        return jsonify({"recommendations": recommended_concerts})

    except Exception as e:
        app.logger.error(f"Error in get_recommendations: {e}", exc_info=True)

        return jsonify({"error": str(e)}), 500
    
'''
    Request: Spring Main Server
    유저가 좋아요한 공연과 유사한 공연 추천
'''
@app.route('/recommendations/items/<concertId>', methods=['GET'])
def get_recommendations_items(concertId):
    try:
        # 추천 결과 가져오기
        recommended_concerts = recommend_similar_concerts_item(concertId)

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


    
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
