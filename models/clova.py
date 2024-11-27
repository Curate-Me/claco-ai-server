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
                "content": (
                    "너는 공연 포스터 설명을 분석하는 시스템이다. 사용자가 제공한 공연 포스터 설명을 바탕으로 "
                    "아래 성격 중 각각 두 가지 대조되는 성격에서 하나씩 선택하여 총 5가지를 선택해야 한다."
                    "또한 선택된 5가지의 성격들에 대해 각각 0.1이상 1이하 사이의 점수를 가져서 반환해야한다. 1에 가까울수록 그 성격이 강한것 0.1로 갈수록 낮은것"
                    "여기서 둘중 낮은 값을 갖는 성격은 제외하고 보내줘"
                    "결과값은 JSON 형식으로 리스트에 넣어서 반환해야 한다."
                    "성격과 점수는 반드시 다음 형식을 따라야 한다: 'categories': [{ 'name': '성격', 'score': 점수 }, ...]. "
                    "\n\n"
                    "1. 웅장한 vs 섬세한\n()"
                    "   웅장한: 큰 규모의 오케스트라나 무대 장치, 강렬한 감정이 느껴지는 공연.\n"
                    "   섬세한: 작은 규모의 연주나 무대, 미세한 감정의 변화와 정교함이 돋보이는 공연.\n"
                    "2. 고전적인 vs 현대적인\n"
                    "   고전적인: 고전적인 형식과 규칙을 따르는 클래식 공연 (예: 고전 교향곡).\n"
                    "   현대적인: 혁신적이고 새로운 형식의 공연 (예: 현대 무용, 현대 클래식).\n"
                    "3. 서정적인 vs 역동적인\n"
                    "   서정적인: 감정적으로 부드럽고 서정적인 음악과 무대.\n"
                    "   역동적인: 빠르고 에너지 넘치는 공연, 강한 움직임과 템포.\n"
                    "4. 낭만적인 vs 비극적인\n"
                    "   낭만적인: 사랑과 감성을 주제로 한 공연, 따뜻하고 감미로운 분위기.\n"
                    "   비극적인: 슬프고 어두운 감정을 전달하는 공연.\n"
                    "5. 친숙한 vs 새로운\n"
                    "   친숙한: 클래식하거나 대중들에게 친숙한 곡이나 춤을 기반으로 한 공연 (예: 지브리 OST, 비발디 '사계').\n"
                    "   새로운: 평소 자주 들어보지 못했던 새로운 곡을 기반으로 한 공연."
                )
            }
            ,
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
        print(response_content)
        analysis_result = self.extract_analysis(response_content)
        return analysis_result

    def execute_summary(self, extracted_text):
        preset_text = [
            {
                "role": "system",
                "content": (
                   "너는 지금부터 주어지는 내용을 바탕으로 공연 내용을 요약해야해. "
                    "평균 50자에서 100자 사이로 요약을 해줘야하고, "
                    "관람객들이 흥미를 느낄 수 있도록 작성해줘."
                    "또한 답변 형식이 아닌 그냥 딱 요약만해서 전달해줘."
                    "또한 무조건 존댓말로 보내줘."
                    "만약 공연 내용을 파악하기 어렵다면 그냥 '없음' 이 두단어만 보내줘"
                        )
            }
            ,
            {
                "role": "user",
                "content": f"이 공연의 내용을 요약해줘: '{extracted_text}'"
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
        print(response_content)
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

        return response_content

    def extract_analysis(self, content):
        try:
            categories_start = content.find('categories')
            if categories_start == -1:
                return {"error": "Categories not found"}

            list_start = content.find('[', categories_start)
            list_end = content.find(']', list_start) + 1

            if list_start == -1 or list_end == -1:
                return {"error": "Failed to find the categories list"}

            categories_str = content[list_start:list_end]

            categories_list = json.loads(categories_str)

            return categories_list

        except json.JSONDecodeError:
            return {"error": "Failed to parse categories JSON"}



