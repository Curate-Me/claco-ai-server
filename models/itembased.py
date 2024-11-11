import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from infra.s3 import get_csv_from_s3
from models.userbased import read_concert_data, read_specific_concert_data

def recommend_similar_concerts_item(concert_id, top_n=2):

    # S3 파일 경로 설정
    concert_file = 'concerts.csv'
    bucket_name = 'claco-bucket'
    folder_name = 'datasets'

    # CSV 파일에서 공연 데이터 가져오기
    concerts = read_concert_data(bucket_name, folder_name, concert_file)
    target_features = read_specific_concert_data(concert_id, bucket_name, folder_name, concert_file)

    # 찾으려는 concert_id가 없으면 종료
    if target_features is None:
        print(f"Concert ID {concert_id} not found.")
        return []

    # target_features에서 0이 아닌 성격 인덱스를 추출
    target_nonzero_indices = [i for i, value in enumerate(target_features) if value > 0]

    # 유사도 계산 및 정렬
    recommendations = []
    for other_concert_id, other_features in concerts:
        if other_concert_id == concert_id:
            continue  

        # other_features에서 target_features와 일치하는 0이 아닌 성격의 개수 계산
        match_count = sum(1 for i in target_nonzero_indices if other_features[i] > 0)

        recommendations.append((other_concert_id, match_count))

    # 일치하는 성격 개수가 많은 순으로 정렬
    recommendations.sort(key=lambda x: x[1], reverse=True)

    # 상위 N개의 유사한 콘서트 추천
    return recommendations[:top_n]


