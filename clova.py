# -*- coding: utf-8 -*-

import requests


class CompletionExecutor:
    def __init__(self, host, api_key, api_key_primary_val, request_id):
        self._host = host
        self._api_key = api_key
        self._api_key_primary_val = api_key_primary_val
        self._request_id = request_id

    def execute(self, completion_request):
        headers = {
            'X-NCP-CLOVASTUDIO-API-KEY': self._api_key,
            'X-NCP-APIGW-API-KEY': self._api_key_primary_val,
            'X-NCP-CLOVASTUDIO-REQUEST-ID': self._request_id,
            'Content-Type': 'application/json; charset=utf-8',
            'Accept': 'text/event-stream'
        }

        with requests.post(self._host + '/testapp/v1/chat-completions/HCX-DASH-001',
                           headers=headers, json=completion_request, stream=True) as r:
            for line in r.iter_lines():
                if line:
                    print(line.decode("utf-8"))


if __name__ == '__main__':
    completion_executor = CompletionExecutor(
        host='https://clovastudio.stream.ntruss.com',
        api_key='NTA0MjU2MWZlZTcxNDJiY0OVIiaDGW9G30APwPRv2Y53pQCHMBkJtKBTwV1msasY',
        api_key_primary_val='JLoUixMPktNwoN3r91KBSvNFsgPzrSe5GMitb3gg',
        request_id='640e9ccf-8f3a-4690-b19e-8cd9875489c5'
    )

    preset_text = [
    {
        "role": "system",
        "content": "너는 공연 포스터 설명을 분석하는 시스템이다. 사용자가 제공한 공연 포스터 설명을 5가지 카테고리로 분석하고, 그 결과를 반환해야 한다. 카테고리는 감성적, 드라마틱, 클래식, 세련된, 로맨틱 등의 성격을 가진다. 결론적으로 너는 반환값을 json 형식으로 카테고리 5가지를 배열로 보내면 돼"
    },
    {
        "role": "user",
        "content": "이 공연의 포스터 설명을 분석해줘: '환상적인 오케스트라 연주와 함께하는 마법 같은 밤. 우아하고 세련된 분위기의 연주회에서 클래식 음악의 진수를 느껴보세요.'"
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

    print(preset_text)
    completion_executor.execute(request_data)
