import requests
import json
import os

class CompletionExecutor:
    def __init__(self):
        self._host = os.getenv('CLOVA_HOST')
        self._api_key = os.getenv('CLOVA_API_KEY')
        self._api_key_primary_val = os.getenv('CLOVA_API_KEY_PRIMARY')
        self._request_id = os.getenv('CLOVA_REQUEST_ID')

    def execute(self, extracted_text):
        preset_text = [
            {
                "role": "system",
                "content": ("너는 공연 포스터 설명을 분석하는 시스템이다. 사용자가 제공한 공연 포스터 설명을 바탕으로 "
                            "따뜻한, 상쾌한, 우아한, 드라마틱한, 감성적인, 신비로운, 경쾌한, 차분한, 강렬한, "
                            "소소한, 몽환적인, 고요한, 열정적인, 신나는, 회상적인, 우울한, 환상적인, 선명한 "
                            "등 18가지 성격 중에서 5가지를 뽑아 분석하고, 그 결과를 JSON 형식으로 반환해야 한다."
                            "반환하는 예제는 다음과 같아야해")
            },
            {
                "role": "user",
                "content": f"이 공연의 포스터 설명을 분석해줘: '{extracted_text}'"
            }
        ]

        request_data = {
            'messages': preset_text,
            'topP': 0.8,
            'topK': 0,
            'maxTokens': 256,
            'temperature': 0.5,
            'repeatPenalty': 5.0,
            'stopBefore': [],
            'includeAiFilters': True,
            'seed': 0
        }

        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        response_content = ''
        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001',
                           headers=headers, json=request_data, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    decoded_line = line.decode("utf-8")
                    if 'data:' in decoded_line:
                        json_data = decoded_line.split('data:')[1].strip()
                        try:
                            parsed_data = json.loads(json_data)
                            if 'message' in parsed_data and 'content' in parsed_data['message']:
                                response_content = parsed_data['message']['content']
                        except json.JSONDecodeError:
                            continue  

        analysis_result = self.extract_analysis(response_content)
        return analysis_result

    def extract_analysis(self, content):
        json_start = content.find('{')
        json_end = content.find('}') + 1
        
        if json_start != -1 and json_end != -1:
            json_str = content[json_start:json_end]

            try:
                analysis_dict = json.loads(json_str)
                return analysis_dict
            except json.JSONDecodeError:
                return {"error": "Failed to parse analysis JSON"}
        
        return {"error": "No valid JSON found in response"}
